"""
Reset & Recovery
----------------
Handles system reset and failure containment.
"""

import importlib
import sys

def perform_reset(facilitator_instance, reason="manual"):
    """
    Resets the agentic system to a safe state.
    
    Args:
        facilitator_instance: The facilitator instance to reset.
        reason (str): Why the reset was triggered.
        
    Returns:
        str: Status message.
    """
    print(f"Triggering RESET. Reason: {reason}")
    
    try:
        # 1. Abort agent execution & Clear agent-local state
        # Since agents are stateless, we just reset the facilitator's tracking
        facilitator_instance.reset_state()
        
        # 2. Reload base files (config)
        # We reload the config module to pick up any changes
        if 'facilitator.config' in sys.modules:
            importlib.reload(sys.modules['facilitator.config'])
            
        # 3. Reload agent modules if they were modified (optional but safer)
        if 'agents.orientation' in sys.modules:
            importlib.reload(sys.modules['agents.orientation'])
        if 'agents.builder' in sys.modules:
            importlib.reload(sys.modules['agents.builder'])
        if 'agents.critic' in sys.modules:
            importlib.reload(sys.modules['agents.critic'])
            
        # Reload configuration in the facilitator
        facilitator_instance.reload_config()
        
        return f"System reset successfully. Reason: {reason}"
    except Exception as e:
        return f"Reset failed: {str(e)}"

def safe_recovery(facilitator_instance):
    """
    Attempts to recover from a failure without full reset if possible.
    For now, falls back to full reset.
    """
    return perform_reset(facilitator_instance, reason="Automatic Recovery")
