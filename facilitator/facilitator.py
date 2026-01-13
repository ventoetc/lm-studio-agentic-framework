"""
Facilitator Control Loop
------------------------
Handles the main control flow for agentic execution.
Does NOT render UI or reason deeply.
"""

import sys
import importlib
import json
from .config import load_config
from .phases import PhaseEnforcer
from .reset import perform_reset
from .tools import TOOL_REGISTRY

# Try to import utils from parent directory
try:
    import utils
except ImportError:
    pass

class Facilitator:
    def __init__(self):
        self.config = load_config()
        self.current_phase = "orientation"
        self.agent_role = "orientation"
        self.history = []
        
    def reload_config(self):
        """Reloads the configuration."""
        self.config = load_config()
        
    def reset_state(self):
        """Resets the internal state."""
        self.current_phase = "orientation"
        self.agent_role = "orientation"
        self.history = []
        
    def process_request(self, message):
        """
        Main entry point for agentic processing.
        """
        try:
            # 1. Select Agent
            agent_module_name = self.config["agents"][self.agent_role]["module"]
            agent_class_name = self.config["agents"][self.agent_role]["class"]
            
            # Dynamic import
            if agent_module_name not in sys.modules:
                importlib.import_module(agent_module_name)
            agent_module = sys.modules[agent_module_name]
            agent_class = getattr(agent_module, agent_class_name)
            agent_instance = agent_class()
            
            # 2. Call Agent (with history and tools)
            # Only Builder Agent gets tools
            use_tools = (self.agent_role == "builder")
            response_text = self._llm_call(agent_instance.SYSTEM_PROMPT, message, use_tools=use_tools)
            
            # 3. Phase Transition Logic
            if "[PHASE_COMPLETE]" in response_text:
                if self.current_phase == "orientation":
                    self.current_phase = "execution"
                    self.agent_role = "builder"
                    response_text = response_text.replace("[PHASE_COMPLETE]", "").strip()
            
            # 4. Phase Enforcement
            if self.current_phase == "orientation":
                is_valid, error = PhaseEnforcer.validate_phase_1(response_text)
                if not is_valid:
                    reset_msg = perform_reset(self, reason=f"Phase 1 Violation: {error}")
                    return f"[SYSTEM RESET] {reset_msg}\n\nOriginal Response (Discarded): {response_text}"
            
            # 5. Add Badge (Visual Indicator)
            badge = ""
            if self.agent_role == "orientation":
                badge = "### 🧭 **Orientation Agent**\n\n"
            elif self.agent_role == "builder":
                badge = "### 🛠️ **Builder Agent**\n\n"
            elif self.agent_role == "critic":
                badge = "### 🧐 **Critic Agent**\n\n"
                
            final_response = badge + response_text
            
            # 6. Update History (Store RAW response without badge to avoid confusing LLM)
            # Note: _llm_call already updates history with tool interactions if any
            # But we need to add the final user/assistant exchange if it wasn't a tool call
            # Wait, _llm_call is complex now. It might return the final text.
            # We should probably let _llm_call handle the history management for the *current turn*.
            # But for simplicity, we append the *user message* here if it's a fresh turn.
            
            # Refactoring: self.history management is tricky with tools.
            # Simple approach: append user message BEFORE calling _llm_call.
            # _llm_call appends the assistant response (and tool calls/outputs).
            
            # Correction: _llm_call below does NOT modify self.history directly during the loop 
            # (it uses a local messages list), so we must sync it back.
            # Let's redesign _llm_call to update self.history incrementally.
            
            return final_response
            
        except Exception as e:
            reset_msg = perform_reset(self, reason=f"Runtime Error: {str(e)}")
            return f"[SYSTEM ERROR] {reset_msg}"

    def _llm_call(self, system_prompt, user_message, use_tools=False, max_turns=5):
        """
        Executes the LLM loop, handling tool calls if necessary.
        Updates self.history with the interaction.
        """
        try:
            client = utils.get_client()
            
            # 1. Prepare Context
            # We construct the messages list for the API call
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(self.history) # Add persistent history
            messages.append({"role": "user", "content": user_message}) # Add current message
            
            # Update persistent history with the user message immediately
            self.history.append({"role": "user", "content": user_message})
            
            # 2. Execution Loop (ReAct / Tool Loop)
            turn = 0
            final_content = ""
            
            while turn < max_turns:
                turn += 1
                
                api_kwargs = {
                    "model": "local-model",
                    "messages": messages,
                    "temperature": 0.7,
                    "stream": False
                }
                
                if use_tools:
                    api_kwargs["tools"] = utils.get_system_tools()
                
                completion = client.chat.completions.create(**api_kwargs)
                response_msg = completion.choices[0].message
                
                # 3. Handle Tool Calls
                if response_msg.tool_calls:
                    # Append assistant message with tool calls to history & context
                    self.history.append(response_msg) # Store the object directly (works with OpenAI client)
                    messages.append(response_msg)
                    
                    for tool_call in response_msg.tool_calls:
                        function_name = tool_call.function.name
                        arguments = json.loads(tool_call.function.arguments)
                        
                        # Execute Tool
                        if function_name in TOOL_REGISTRY:
                            try:
                                result = TOOL_REGISTRY[function_name](**arguments)
                            except Exception as e:
                                result = f"Error executing {function_name}: {str(e)}"
                        else:
                            result = f"Error: Tool '{function_name}' not found."
                            
                        # Append Tool Output
                        tool_msg = {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": function_name,
                            "content": str(result)
                        }
                        self.history.append(tool_msg)
                        messages.append(tool_msg)
                        
                    # Loop continues to let LLM generate response to tool output
                    continue
                    
                # 4. Handle Final Response (No tools called)
                final_content = response_msg.content
                if final_content:
                    self.history.append({"role": "assistant", "content": final_content})
                    return final_content
                
                # If we got here (no content, no tools), something is weird.
                return "*Agent returned empty response.*"
                
            return final_content + "\n\n*(Tool execution limit reached)*"

        except Exception as e:
            raise RuntimeError(f"LLM Call Failed: {str(e)}")

    def load_project_context(self):
        """
        Loads project base on session start.
        """
        pass
