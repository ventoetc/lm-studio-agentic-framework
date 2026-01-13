"""
Application Router
------------------
Routes requests between the standard chat application and the agentic facilitator.
Protects the base chat app from agentic complexity.
"""

def route_request(message, agent_mode_enabled=False, facilitator=None):
    """
    Routes the user message.
    
    Args:
        message (str): The user's input message.
        agent_mode_enabled (bool): Whether agent mode is toggled on.
        facilitator (Facilitator): The facilitator instance (required if agent_mode_enabled is True).
        
    Returns:
        dict: Response object containing 'type' ('chat' or 'agent') and payload.
    """
    if agent_mode_enabled and facilitator:
        try:
            response = facilitator.process_request(message)
            return {"type": "agent", "payload": response}
        except Exception as e:
            # Fallback to chat if facilitator fails hard
            return {"type": "chat", "payload": f"[ROUTER ERROR] Agent failed: {str(e)}. Falling back to standard chat."}
    
    return {"type": "chat", "payload": message}
