"""
Système Mathématique Harmonieux pour Vectort.io
Basé sur Fibonacci et le Nombre d'Or (φ = 1.618)

Formules d'harmonie pour performance optimale
"""

import math
import logging
from typing import Dict, List, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class GoldenRatioOptimizer:
    """
    Optimiseur basé sur le Nombre d'Or (φ = 1.618033988749895)
    
    Le nombre d'or apparaît dans la nature (coquillages, galaxies, corps humain)
    et garantit l'équilibre et l'harmonie parfaits
    """
    
    PHI = (1 + math.sqrt(5)) / 2  # φ = 1.618033988749895
    
    @classmethod
    def calculate_optimal_ratios(cls, total_resources: float = 100.0) -> Dict[str, float]:
        """
        Calcule les ratios optimaux pour les 12 agents basés sur Fibonacci et φ
        
        Séquence Fibonacci: 1, 1, 2, 3, 5, 8, 13, 21, 34...
        Ratio entre nombres consécutifs tend vers φ
        
        Returns:
            Dict avec allocation optimale par agent
        """
        
        # Séquence Fibonacci pour 12 agents
        fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144]
        
        # Total de la séquence
        total_fib = sum(fibonacci)
        
        # Allocation basée sur ratios Fibonacci
        agents = [
            "diagnostic",      # 1
            "frontend",        # 1
            "styling",         # 2
            "backend",         # 3
            "config",          # 5
            "components",      # 8
            "database",        # 13
            "security",        # 21
            "testing",         # 34
            "qa",              # 55
            "meta_learning",   # 89
            "self_healing"     # 144
        ]
        
        # Normaliser pour obtenir des pourcentages
        ratios = {}
        for i, agent in enumerate(agents):
            ratio = (fibonacci[i] / total_fib) * total_resources
            ratios[agent] = round(ratio, 2)
        
        logger.info(f"✨ Ratios Fibonacci calculés (total: {sum(ratios.values()):.2f}%)")
        
        return ratios
    
    @classmethod
    def optimize_timeouts(cls, base_timeout: float = 20.0) -> Dict[str, float]:
        """
        Calcule les timeouts optimaux basés sur φ
        
        Chaque agent a un timeout proportionnel à son importance (Fibonacci)
        """
        
        ratios = cls.calculate_optimal_ratios(100.0)
        
        timeouts = {}
        for agent, ratio in ratios.items():
            # Timeout entre base_timeout et base_timeout * φ²
            timeout = base_timeout * (1 + (ratio / 100.0) * (cls.PHI - 1))
            timeouts[agent] = round(timeout, 1)
        
        return timeouts
    
    @classmethod
    def calculate_agent_priority(cls) -> Dict[str, int]:
        """
        Calcule la priorité de chaque agent (1 = plus haute priorité)
        
        Basé sur position dans séquence Fibonacci inversée
        """
        
        agents = [
            "diagnostic",
            "frontend", 
            "styling",
            "backend",
            "config",
            "components",
            "database",
            "security",
            "testing",
            "qa",
            "meta_learning",
            "self_healing"
        ]
        
        # Priorité inversée (diagnostic = 12, self_healing = 1)
        priorities = {}
        for i, agent in enumerate(agents):
            priorities[agent] = 12 - i  # 12, 11, 10, ..., 1
        
        return priorities
    
    @classmethod
    def calculate_harmonic_mean(cls, values: List[float]) -> float:
        """
        Calcule la moyenne harmonique (meilleure pour ratios et vitesses)
        
        H = n / (1/x₁ + 1/x₂ + ... + 1/xₙ)
        """
        
        if not values or any(v <= 0 for v in values):
            return 0.0
        
        n = len(values)
        sum_reciprocals = sum(1.0 / v for v in values)
        
        return n / sum_reciprocals
    
    @classmethod
    def calculate_geometric_mean(cls, values: List[float]) -> float:
        """
        Calcule la moyenne géométrique (idéale pour croissance)
        
        G = (x₁ × x₂ × ... × xₙ)^(1/n)
        """
        
        if not values or any(v <= 0 for v in values):
            return 0.0
        
        product = math.prod(values)
        n = len(values)
        
        return product ** (1.0 / n)
    
    @classmethod
    def is_golden_ratio(cls, a: float, b: float, tolerance: float = 0.01) -> bool:
        """
        Vérifie si deux nombres sont dans le ratio d'or
        
        a/b ≈ φ (avec tolérance)
        """
        
        if b == 0:
            return False
        
        ratio = a / b
        return abs(ratio - cls.PHI) < tolerance


class FibonacciScheduler:
    """
    Planificateur basé sur la séquence Fibonacci
    Pour ordonnancement optimal des tâches
    """
    
    @staticmethod
    def get_fibonacci_sequence(n: int) -> List[int]:
        """Génère n nombres de Fibonacci"""
        
        if n <= 0:
            return []
        elif n == 1:
            return [1]
        elif n == 2:
            return [1, 1]
        
        fib = [1, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        
        return fib
    
    @staticmethod
    def calculate_optimal_batch_size(total_items: int) -> int:
        """
        Calcule la taille de batch optimale (nombre Fibonacci le plus proche)
        
        Les tailles Fibonacci optimisent la division du travail
        """
        
        fib = FibonacciScheduler.get_fibonacci_sequence(20)
        
        # Trouver le nombre Fibonacci le plus proche
        closest = min(fib, key=lambda x: abs(x - total_items/5))
        
        return closest
    
    @staticmethod
    def schedule_tasks_fibonacci(tasks: List[str]) -> List[List[str]]:
        """
        Organise les tâches en batches selon Fibonacci
        
        Garantit distribution harmonieuse
        """
        
        n_tasks = len(tasks)
        batch_size = FibonacciScheduler.calculate_optimal_batch_size(n_tasks)
        
        batches = []
        for i in range(0, n_tasks, batch_size):
            batches.append(tasks[i:i+batch_size])
        
        return batches


class MathematicalHarmony:
    """
    Système d'harmonie mathématique pour Vectort.io
    
    Combine:
    - Nombre d'or (φ)
    - Fibonacci
    - Moyennes harmonique et géométrique
    - Ratios parfaits
    """
    
    def __init__(self):
        self.optimizer = GoldenRatioOptimizer()
        self.scheduler = FibonacciScheduler()
    
    def calculate_system_harmony_score(
        self,
        agent_performances: Dict[str, float]
    ) -> float:
        """
        Calcule le score d'harmonie du système /100
        
        Formule:
        Harmonie = (variance_faible * 40) + (ratio_or * 30) + (efficacité * 30)
        
        Plus le système est harmonieux (performances équilibrées), plus le score est élevé
        """
        
        if not agent_performances:
            return 0.0
        
        performances = list(agent_performances.values())
        
        # 1. Variance (plus faible = plus harmonieux)
        mean = sum(performances) / len(performances)
        variance = sum((p - mean) ** 2 for p in performances) / len(performances)
        std_dev = math.sqrt(variance)
        
        # Score variance (inverse - moins de variance = mieux)
        variance_score = max(0, 100 - (std_dev * 10))
        
        # 2. Vérifier ratios d'or entre agents
        golden_ratio_matches = 0
        total_comparisons = 0
        
        for i, p1 in enumerate(performances):
            for p2 in performances[i+1:]:
                if p2 > 0:
                    total_comparisons += 1
                    if self.optimizer.is_golden_ratio(p1, p2):
                        golden_ratio_matches += 1
        
        golden_ratio_score = (golden_ratio_matches / total_comparisons * 100) if total_comparisons > 0 else 0
        
        # 3. Efficacité globale (moyenne géométrique)
        geometric_mean = self.optimizer.calculate_geometric_mean(performances)
        efficiency_score = min(100, geometric_mean)
        
        # Score final pondéré
        harmony_score = (
            variance_score * 0.40 +
            golden_ratio_score * 0.30 +
            efficiency_score * 0.30
        )
        
        logger.info(f"✨ Score harmonie: {harmony_score:.1f}/100")
        logger.info(f"   Variance: {variance_score:.1f}, Ratio d'or: {golden_ratio_score:.1f}, Efficacité: {efficiency_score:.1f}")
        
        return harmony_score
    
    def optimize_resource_allocation(
        self,
        total_resources: float,
        current_loads: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Optimise l'allocation des ressources basée sur Fibonacci et charge actuelle
        
        Returns:
            Nouvelles allocations optimales
        """
        
        # Ratios Fibonacci de base
        fibonacci_ratios = self.optimizer.calculate_optimal_ratios(total_resources)
        
        # Ajuster selon charge actuelle
        optimized = {}
        
        for agent, fib_ratio in fibonacci_ratios.items():
            current_load = current_loads.get(agent, 50.0)
            
            # Si surcharge, augmenter allocation
            if current_load > 80:
                adjustment = 1 + (current_load - 80) / 100
            # Si sous-charge, diminuer allocation
            elif current_load < 30:
                adjustment = 0.8
            else:
                adjustment = 1.0
            
            optimized[agent] = fib_ratio * adjustment
        
        # Re-normaliser pour respecter total_resources
        total = sum(optimized.values())
        optimized = {k: (v / total) * total_resources for k, v in optimized.items()}
        
        return optimized
    
    def calculate_fibonacci_timeout_sequence(
        self,
        base_timeout: float,
        max_retries: int
    ) -> List[float]:
        """
        Calcule une séquence de timeouts basée sur Fibonacci
        
        Chaque retry a un timeout qui suit Fibonacci
        Exemple: 20s, 33s, 53s (ratio tend vers φ)
        """
        
        fib = self.scheduler.get_fibonacci_sequence(max_retries + 1)
        
        timeouts = []
        for f in fib:
            timeout = base_timeout * (f / fib[0])
            timeouts.append(round(timeout, 1))
        
        return timeouts
    
    def get_system_stats(self) -> Dict:
        """Retourne les statistiques du système mathématique"""
        
        return {
            "golden_ratio_phi": GoldenRatioOptimizer.PHI,
            "fibonacci_sequence_12": self.scheduler.get_fibonacci_sequence(12),
            "optimal_agent_ratios": self.optimizer.calculate_optimal_ratios(),
            "agent_priorities": self.optimizer.calculate_agent_priority(),
            "optimal_timeouts": self.optimizer.optimize_timeouts()
        }


# Export
__all__ = [
    'GoldenRatioOptimizer',
    'FibonacciScheduler',
    'MathematicalHarmony'
]
