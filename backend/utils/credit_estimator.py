"""
Credit Estimation System - Like Emergent
Estimates credit cost based on task complexity
"""

from typing import Dict, Tuple
import re


class CreditEstimator:
    """Estimate credits needed based on task complexity"""
    
    # Keywords indicating different levels of complexity
    SIMPLE_KEYWORDS = [
        "change", "modify", "update", "fix", "correct", "adjust",
        "couleur", "color", "text", "texte", "style", "titre"
    ]
    
    MEDIUM_KEYWORDS = [
        "add", "ajoute", "create", "crée", "implement", "implémente",
        "form", "formulaire", "button", "bouton", "section", "page"
    ]
    
    COMPLEX_KEYWORDS = [
        "integrate", "intègre", "api", "database", "authentication",
        "payment", "paiement", "real-time", "temps réel", "websocket",
        "animation", "responsive", "dashboard", "admin", "chart"
    ]
    
    VERY_COMPLEX_KEYWORDS = [
        "full", "complete", "entire", "complet", "entier", "refactor",
        "redesign", "migration", "optimization", "security", "sécurité",
        "architecture", "infrastructure", "deployment", "déploiement"
    ]
    
    @staticmethod
    def estimate_complexity(instruction: str) -> Tuple[int, str, str]:
        """
        Estimate credit cost based on instruction complexity
        
        Args:
            instruction: User's improvement request
            
        Returns:
            (credit_cost, complexity_level, explanation)
        """
        instruction_lower = instruction.lower()
        word_count = len(instruction.split())
        
        # Count keyword matches
        simple_count = sum(1 for kw in CreditEstimator.SIMPLE_KEYWORDS if kw in instruction_lower)
        medium_count = sum(1 for kw in CreditEstimator.MEDIUM_KEYWORDS if kw in instruction_lower)
        complex_count = sum(1 for kw in CreditEstimator.COMPLEX_KEYWORDS if kw in instruction_lower)
        very_complex_count = sum(1 for kw in CreditEstimator.VERY_COMPLEX_KEYWORDS if kw in instruction_lower)
        
        # Check for multiple files/components
        multi_file_indicators = ["and", "et", "also", "aussi", "plus", "avec"]
        is_multi_part = sum(1 for ind in multi_file_indicators if ind in instruction_lower) >= 2
        
        # Scoring system
        score = 0
        score += simple_count * 1
        score += medium_count * 2
        score += complex_count * 4
        score += very_complex_count * 8
        
        # Length factor
        if word_count > 50:
            score += 3
        elif word_count > 30:
            score += 2
        elif word_count > 15:
            score += 1
        
        # Multi-part factor
        if is_multi_part:
            score += 2
        
        # Determine complexity level and credit cost
        if score <= 2 or (simple_count > 0 and medium_count == 0 and complex_count == 0 and word_count < 15):
            # Simple: color change, text update, small style fix
            return (1, "simple", "Modification simple (couleur, texte, style basique)")
            
        elif score <= 5 or medium_count > 0 and complex_count == 0:
            # Medium: add a button, create a form, add section
            return (2, "medium", "Modification moyenne (ajout de composant, formulaire simple)")
            
        elif score <= 10 or complex_count > 0:
            # Complex: API integration, animations, responsive design
            return (3, "complex", "Modification complexe (intégration API, animations, design responsive)")
            
        else:
            # Very Complex: full refactor, multiple integrations, architecture changes
            return (5, "very_complex", "Modification très complexe (refonte complète, multiples intégrations)")
    
    @staticmethod
    def get_credit_breakdown(instruction: str) -> Dict:
        """Get detailed credit breakdown"""
        cost, level, explanation = CreditEstimator.estimate_complexity(instruction)
        
        return {
            "estimated_credits": cost,
            "complexity_level": level,
            "explanation": explanation,
            "factors": {
                "instruction_length": len(instruction.split()),
                "complexity_indicators": CreditEstimator._get_indicators(instruction)
            }
        }
    
    @staticmethod
    def _get_indicators(instruction: str) -> list:
        """Get list of complexity indicators found"""
        instruction_lower = instruction.lower()
        indicators = []
        
        all_keywords = {
            "simple": CreditEstimator.SIMPLE_KEYWORDS,
            "medium": CreditEstimator.MEDIUM_KEYWORDS,
            "complex": CreditEstimator.COMPLEX_KEYWORDS,
            "very_complex": CreditEstimator.VERY_COMPLEX_KEYWORDS
        }
        
        for level, keywords in all_keywords.items():
            for kw in keywords:
                if kw in instruction_lower:
                    indicators.append({"keyword": kw, "level": level})
        
        return indicators


# Example usage
if __name__ == "__main__":
    test_cases = [
        "Change la couleur du bouton en bleu",
        "Ajoute un formulaire de contact avec validation",
        "Intègre l'API Stripe pour les paiements et ajoute un dashboard admin",
        "Refactor complete de l'architecture avec migration vers Next.js"
    ]
    
    estimator = CreditEstimator()
    for test in test_cases:
        cost, level, explanation = estimator.estimate_complexity(test)
        print(f"\nInstruction: {test}")
        print(f"Credits: {cost} | Level: {level}")
        print(f"Explanation: {explanation}")
