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
    # Fallback for when running as a package or different context
    # This assumes the script is run from the root directory
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
        
        Args:
            message (str): The user's input message.
            
        Returns:
            str: The response from the agent.
        """
        try:
            # 1. Select Agent based on Phase/Role
            agent_module_name = self.config["agents"][self.agent_role]["module"]
            agent_class_name = self.config["agents"][self.agent_role]["class"]
            
            # Dynamic import of agent
            if agent_module_name not in sys.modules:
                importlib.import_module(agent_module_name)
            agent_module = sys.modules[agent_module_name]
            agent_class = getattr(agent_module, agent_class_name)
            agent_instance = agent_class()
            
            # 2. Call Agent (LLM Call via Utils)
            # Construct messages for LLM
            # For MVP, we just pass the user message and history
            # Ideally, we should manage history better
            
            # Wrapper for utils.get_client().chat.completions.create
            response_text = self._llm_call(agent_instance.SYSTEM_PROMPT, message)
            
            # 3. Phase Enforcement
            if self.current_phase == "orientation":
                is_valid, error = PhaseEnforcer.validate_phase_1(response_text)
                if not is_valid:
                    # Phase Violation -> Reset (as per PRD)
                    reset_msg = perform_reset(self, reason=f"Phase 1 Violation: {error}")
                    return f"[SYSTEM RESET] {reset_msg}\n\nOriginal Response (Discarded): {response_text}"
            
            # 4. Update History
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": response_text})
            
            return response_text
            
        except Exception as e:
            reset_msg = perform_reset(self, reason=f"Runtime Error: {str(e)}")
            return f"[SYSTEM ERROR] {reset_msg}"

    def _llm_call(self, system_prompt, user_message):
        """
        Thin wrapper around existing LM Studio client (utils.py).
        """
        try:
            client = utils.get_client()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Check if history should be included (simple append for now)
            # For a real agent, we might want to include more context
            
            completion = client.chat.completions.create(
                model="local-model", # This should ideally come from config or UI selection
                messages=messages,
                temperature=0.7,
                stream=False # Facilitator handles full response for validation
            )
            
            return completion.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM Call Failed: {str(e)}")

    def load_project_context(self):
        """
        Loads project base on session start.
        """
        # TODO: Load from base/project.md
        pass
