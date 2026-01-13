"""
Application Router
------------------
Routes requests between the standard chat application and the agentic facilitator.
Protects the base chat app from agentic complexity.
"""

def route_request(message, agent_mode_enabled=False):
    """
    Routes the user message.
    
    Args:
        message (str): The user's input message.
        agent_mode_enabled (bool): Whether agent mode is toggled on.
        
    Returns:
        dict: Response object containing 'type' ('chat' or 'agent') and payload.
    """
    # Placeholder for routing logic
    if agent_mode_enabled:
        return {"type": "agent", "payload": message}
    
    return {"type": "chat", "payload": message}
