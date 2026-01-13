"""
Facilitator Control Loop
------------------------
Handles the main control flow for agentic execution.
Does NOT render UI or reason deeply.
"""

import sys
import importlib
from .config import load_config
from .phases import PhaseEnforcer
from .reset import perform_reset

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
            
            # 2. Call Agent (with history)
            response_text = self._llm_call(agent_instance.SYSTEM_PROMPT, message)
            
            # 3. Phase Transition Logic
            if "[PHASE_COMPLETE]" in response_text:
                if self.current_phase == "orientation":
                    self.current_phase = "execution"
                    self.agent_role = "builder"
                    # Strip the token for display
                    response_text = response_text.replace("[PHASE_COMPLETE]", "").strip()
                    # Append a system note about transition (optional)
                    # response_text += "\n\n*(Phase 1 Complete. Switching to Builder Mode.)*"
            
            # 4. Phase Enforcement
            if self.current_phase == "orientation":
                is_valid, error = PhaseEnforcer.validate_phase_1(response_text)
                if not is_valid:
                    reset_msg = perform_reset(self, reason=f"Phase 1 Violation: {error}")
                    return f"[SYSTEM RESET] {reset_msg}\n\nOriginal Response (Discarded): {response_text}"
            
            # 5. Update History
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": response_text})
            
            return response_text
            
        except Exception as e:
            reset_msg = perform_reset(self, reason=f"Runtime Error: {str(e)}")
            return f"[SYSTEM ERROR] {reset_msg}"

    def _llm_call(self, system_prompt, user_message):
        """
        Thin wrapper around existing LM Studio client (utils.py).
        Includes conversation history.
        """
        try:
            client = utils.get_client()
            
            # Start with System Prompt
            messages = [{"role": "system", "content": system_prompt}]
            
            # Append History (Context)
            for msg in self.history:
                messages.append(msg)
            
            # Append Current User Message
            messages.append({"role": "user", "content": user_message})
            
            completion = client.chat.completions.create(
                model="local-model",
                messages=messages,
                temperature=0.7,
                stream=False
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM Call Failed: {str(e)}")

    def load_project_context(self):
        """
        Loads project base on session start.
        """
        pass
