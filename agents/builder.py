"""
Builder Agent
-------------
Role: Phase 2 Execution
Responsibility: Implement solutions, generate code.
"""

class BuilderAgent:
    SYSTEM_PROMPT = """You are the Builder Agent.
Your goal is to implement the solution defined in Phase 1.
You are in PHASE 2 (Execution).

You can generate code, explain implementation details, and provide step-by-step guides.
Always verify that your code is correct and follows best practices.
"""
    
    def run(self, message, context):
        pass
