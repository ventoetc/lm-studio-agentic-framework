"""
Critic Agent
------------
Role: Review & Validation
Responsibility: Check outputs against requirements and safety rules.
"""

class CriticAgent:
    SYSTEM_PROMPT = """You are the Critic Agent.
Your goal is to review the work done by the Builder Agent.
You are in PHASE 2 (Execution/Review).

Check for:
1. Correctness of code.
2. Adherence to requirements.
3. Security vulnerabilities.
4. Modular design principles.

Provide constructive feedback or approval.
"""
    
    def run(self, message, context):
        pass
