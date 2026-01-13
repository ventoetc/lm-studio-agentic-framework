"""
Phase Enforcement
-----------------
Enforces Phase 1 (Orientation) vs Phase 2 (Execution) rules.
"""

import re

class PhaseEnforcer:
    @staticmethod
    def validate_phase_1(response_text):
        """
        Validates Phase 1 constraints:
        - Max 1 paragraph OR 4 sentences
        - No lists
        - No solutions
        
        Args:
            response_text (str): The text to validate.
            
        Returns:
            bool: True if valid, False otherwise.
            str: Error message if invalid.
        """
        if not response_text:
            return True, None
            
        # Check for lists (lines starting with - or * or 1.)
        if re.search(r'^\s*[-*1-9]\.?\s+', response_text, re.MULTILINE):
            return False, "Phase 1 violation: Lists are not allowed in orientation."
            
        # Count sentences (rough approximation)
        sentences = re.split(r'[.!?]+', response_text)
        # Filter out empty strings
        sentences = [s for s in sentences if s.strip()]
        
        if len(sentences) > 4:
            return False, f"Phase 1 violation: Response too long ({len(sentences)} sentences). Max 4 allowed."
            
        return True, None
        
    @staticmethod
    def validate_phase_2(response_text):
        """
        Validates Phase 2 constraints.
        Currently Phase 2 has unlimited output, but we might want to check for JSON structure if required.
        """
        return True, None
