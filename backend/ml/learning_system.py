"""
Machine Learning System for Vectort.io
Sistema de aprendizaje automático que mejora continuamente
Los agentes aprenden de cada generación para no repetir errores
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class GenerationFeedback:
    """Feedback d'une génération pour apprentissage"""
    
    def __init__(
        self,
        project_id: str,
        user_id: str,
        description: str,
        generated_files: Dict[str, str],
        user_rating: Optional[int] = None,
        compilation_success: bool = False,
        runtime_errors: List[str] = None,
        user_modifications: Dict[str, str] = None,
        time_taken: float = 0.0
    ):
        self.project_id = project_id
        self.user_id = user_id
        self.description = description
        self.generated_files = generated_files
        self.user_rating = user_rating  # 1-5 étoiles
        self.compilation_success = compilation_success
        self.runtime_errors = runtime_errors or []
        self.user_modifications = user_modifications or {}
        self.time_taken = time_taken
        self.timestamp = datetime.utcnow()
        
        # Calcul auto du score
        self.auto_score = self._calculate_auto_score()
    
    def _calculate_auto_score(self) -> float:
        """
        Calcule automatiquement un score /100 basé sur métriques objectives
        
        Formule mathématique optimale:
        Score = (40 * compilation) + (30 * user_rating/5) + (20 * code_quality) + (10 * performance)
        """
        score = 0.0
        
        # 1. Compilation (40 points max)
        if self.compilation_success:
            score += 40.0
        
        # 2. User rating (30 points max)
        if self.user_rating:
            score += 30.0 * (self.user_rating / 5.0)
        
        # 3. Code quality (20 points max) - Basé sur modifications
        if self.user_modifications:
            modification_ratio = len(self.user_modifications) / max(len(self.generated_files), 1)
            # Moins de modifications = meilleure qualité
            quality_score = max(0, 20.0 * (1.0 - modification_ratio))
            score += quality_score
        else:
            score += 20.0  # Pas de modifications = parfait
        
        # 4. Performance (10 points max)
        if self.time_taken > 0:
            # Optimal: 60-90s, pénalité si trop long ou trop court
            if 60 <= self.time_taken <= 90:
                score += 10.0
            elif self.time_taken < 60:
                score += 10.0 * (self.time_taken / 60.0)
            else:
                score += 10.0 * (90.0 / self.time_taken)
        
        return min(100.0, score)
    
    def to_dict(self) -> Dict:
        """Convertit en dict pour stockage MongoDB"""
        return {
            "project_id": self.project_id,
            "user_id": self.user_id,
            "description": self.description,
            "generated_files_count": len(self.generated_files),
            "generated_files_sizes": {k: len(v) for k, v in self.generated_files.items()},
            "user_rating": self.user_rating,
            "compilation_success": self.compilation_success,
            "runtime_errors": self.runtime_errors,
            "user_modifications_count": len(self.user_modifications),
            "time_taken": self.time_taken,
            "auto_score": self.auto_score,
            "timestamp": self.timestamp
        }


class PatternLearner:
    """Apprend des patterns de succès et échecs"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.patterns_collection = db.ml_patterns
        self.feedback_collection = db.ml_feedback
    
    async def analyze_successes(self, min_score: float = 80.0) -> Dict:
        """
        Analyse les générations réussies pour identifier patterns
        
        Returns:
            Dict avec patterns de succès identifiés
        """
        logger.info(f"🧠 Analyse des succès (score >= {min_score})")
        
        # Récupérer les feedbacks réussis
        successes = await self.feedback_collection.find({
            "auto_score": {"$gte": min_score}
        }).to_list(length=100)
        
        if not successes:
            return {"patterns": [], "recommendations": []}
        
        # Analyser patterns communs
        patterns = {
            "description_lengths": [],
            "file_counts": [],
            "common_keywords": defaultdict(int),
            "optimal_time_range": [],
            "compilation_success_rate": 0.0
        }
        
        for feedback in successes:
            patterns["description_lengths"].append(len(feedback.get("description", "")))
            patterns["file_counts"].append(feedback.get("generated_files_count", 0))
            patterns["optimal_time_range"].append(feedback.get("time_taken", 0))
            
            # Extraire keywords de description
            desc = feedback.get("description", "").lower()
            for word in desc.split():
                if len(word) > 4:  # Mots significatifs
                    patterns["common_keywords"][word] += 1
        
        # Calculer moyennes et recommendations
        avg_length = sum(patterns["description_lengths"]) / len(patterns["description_lengths"])
        avg_files = sum(patterns["file_counts"]) / len(patterns["file_counts"])
        avg_time = sum(patterns["optimal_time_range"]) / len(patterns["optimal_time_range"])
        
        recommendations = [
            f"Description optimale: {int(avg_length)} caractères",
            f"Nombre de fichiers optimal: {int(avg_files)}",
            f"Temps optimal: {int(avg_time)}s",
            f"Keywords de succès: {', '.join(list(patterns['common_keywords'].keys())[:5])}"
        ]
        
        return {
            "patterns": patterns,
            "recommendations": recommendations,
            "success_count": len(successes)
        }
    
    async def analyze_failures(self, max_score: float = 50.0) -> Dict:
        """
        Analyse les échecs pour identifier erreurs à éviter
        
        Returns:
            Dict avec patterns d'échec identifiés
        """
        logger.info(f"⚠️ Analyse des échecs (score <= {max_score})")
        
        # Récupérer les feedbacks d'échec
        failures = await self.feedback_collection.find({
            "auto_score": {"$lte": max_score}
        }).to_list(length=100)
        
        if not failures:
            return {"errors": [], "recommendations": []}
        
        # Analyser erreurs communes
        error_patterns = {
            "common_errors": defaultdict(int),
            "problematic_keywords": defaultdict(int),
            "compilation_failures": 0
        }
        
        for feedback in failures:
            # Erreurs runtime
            for error in feedback.get("runtime_errors", []):
                error_patterns["common_errors"][error[:50]] += 1  # Premiers 50 chars
            
            # Problèmes de compilation
            if not feedback.get("compilation_success", False):
                error_patterns["compilation_failures"] += 1
            
            # Keywords problématiques
            desc = feedback.get("description", "").lower()
            for word in desc.split():
                if len(word) > 4:
                    error_patterns["problematic_keywords"][word] += 1
        
        # Top erreurs
        top_errors = sorted(
            error_patterns["common_errors"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        recommendations = [
            f"Éviter: {', '.join([e[0] for e in top_errors])}",
            f"Taux d'échec compilation: {error_patterns['compilation_failures']}/{len(failures)}",
            "Améliorer validation syntaxe avant génération"
        ]
        
        return {
            "errors": error_patterns,
            "recommendations": recommendations,
            "failure_count": len(failures)
        }
    
    async def calculate_optimal_ratios(self) -> Dict[str, float]:
        """
        Calcule les ratios mathématiques optimaux entre agents
        
        Basé sur analyse statistique des succès
        Returns:
            Dict avec poids optimal pour chaque agent
        """
        logger.info("🔢 Calcul des ratios mathématiques optimaux")
        
        # Récupérer toutes les générations avec score
        all_feedback = await self.feedback_collection.find({
            "auto_score": {"$exists": True}
        }).to_list(length=1000)
        
        if not all_feedback:
            # Ratios par défaut équilibrés
            return {
                "diagnostic": 0.10,
                "frontend": 0.15,
                "styling": 0.10,
                "backend": 0.15,
                "config": 0.08,
                "components": 0.10,
                "database": 0.12,
                "security": 0.10,
                "testing": 0.08,
                "qa": 0.02
            }
        
        # Analyser corrélation entre présence de types de fichiers et succès
        correlations = defaultdict(float)
        
        for feedback in all_feedback:
            score = feedback.get("auto_score", 0)
            file_sizes = feedback.get("generated_files_sizes", {})
            
            # Calculer contribution de chaque type
            for file_path, size in file_sizes.items():
                if '.jsx' in file_path or 'component' in file_path.lower():
                    correlations['frontend'] += score * (size / 10000.0)
                elif '.css' in file_path:
                    correlations['styling'] += score * (size / 10000.0)
                elif '.py' in file_path and 'backend' in file_path:
                    correlations['backend'] += score * (size / 10000.0)
                elif 'database' in file_path or 'model' in file_path.lower():
                    correlations['database'] += score * (size / 10000.0)
                elif 'security' in file_path or 'auth' in file_path:
                    correlations['security'] += score * (size / 10000.0)
                elif 'test' in file_path:
                    correlations['testing'] += score * (size / 10000.0)
        
        # Normaliser les corrélations pour obtenir ratios /1
        total = sum(correlations.values())
        if total > 0:
            optimal_ratios = {k: v/total for k, v in correlations.items()}
        else:
            optimal_ratios = {}
        
        # Compléter avec valeurs par défaut
        default_ratios = {
            "diagnostic": 0.10,
            "frontend": 0.15,
            "styling": 0.10,
            "backend": 0.15,
            "config": 0.08,
            "components": 0.10,
            "database": 0.12,
            "security": 0.10,
            "testing": 0.08,
            "qa": 0.02
        }
        
        for agent, default_ratio in default_ratios.items():
            if agent not in optimal_ratios:
                optimal_ratios[agent] = default_ratio
        
        logger.info(f"✅ Ratios optimaux calculés: {optimal_ratios}")
        return optimal_ratios


class AgentPerformanceTracker:
    """Suit et analyse les performances de chaque agent individuellement"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.performance_collection = db.agent_performance
    
    async def record_agent_performance(
        self,
        agent_name: str,
        execution_time: float,
        files_generated: int,
        errors: List[str],
        quality_score: float
    ):
        """Enregistre la performance d'un agent"""
        
        await self.performance_collection.insert_one({
            "agent_name": agent_name,
            "execution_time": execution_time,
            "files_generated": files_generated,
            "error_count": len(errors),
            "errors": errors,
            "quality_score": quality_score,
            "timestamp": datetime.utcnow()
        })
    
    async def get_agent_stats(self, agent_name: str, days: int = 7) -> Dict:
        """Obtient les statistiques d'un agent"""
        
        from datetime import timedelta
        since = datetime.utcnow() - timedelta(days=days)
        
        performances = await self.performance_collection.find({
            "agent_name": agent_name,
            "timestamp": {"$gte": since}
        }).to_list(length=1000)
        
        if not performances:
            return {"avg_time": 0, "avg_files": 0, "avg_quality": 0, "error_rate": 0}
        
        total_time = sum(p["execution_time"] for p in performances)
        total_files = sum(p["files_generated"] for p in performances)
        total_quality = sum(p["quality_score"] for p in performances)
        total_errors = sum(p["error_count"] for p in performances)
        
        return {
            "agent_name": agent_name,
            "executions": len(performances),
            "avg_time": total_time / len(performances),
            "avg_files": total_files / len(performances),
            "avg_quality": total_quality / len(performances),
            "error_rate": total_errors / len(performances),
            "status": "healthy" if (total_errors / len(performances)) < 0.1 else "needs_improvement"
        }
    
    async def get_all_agents_health(self) -> Dict[str, Dict]:
        """Obtient le status de santé de tous les agents"""
        
        agents = [
            "diagnostic", "frontend", "styling", "backend",
            "config", "components", "database", "security",
            "testing", "qa"
        ]
        
        health_report = {}
        for agent in agents:
            health_report[agent] = await self.get_agent_stats(agent)
        
        return health_report


class MLLearningSystem:
    """Système central de Machine Learning"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.pattern_learner = PatternLearner(db)
        self.performance_tracker = AgentPerformanceTracker(db)
        self.feedback_collection = db.ml_feedback
    
    async def record_generation_feedback(self, feedback: GenerationFeedback):
        """Enregistre le feedback d'une génération"""
        
        await self.feedback_collection.insert_one(feedback.to_dict())
        logger.info(f"📊 Feedback enregistré - Score: {feedback.auto_score}/100")
    
    async def learn_and_optimize(self) -> Dict:
        """
        Apprentissage et optimisation du système
        
        Analyse patterns, calcule ratios optimaux, génère recommendations
        Returns:
            Dict avec insights et recommendations
        """
        logger.info("🧠 Démarrage apprentissage ML")
        
        # Analyser succès
        success_analysis = await self.pattern_learner.analyze_successes()
        
        # Analyser échecs
        failure_analysis = await self.pattern_learner.analyze_failures()
        
        # Calculer ratios optimaux
        optimal_ratios = await self.pattern_learner.calculate_optimal_ratios()
        
        # Santé des agents
        agents_health = await self.performance_tracker.get_all_agents_health()
        
        # Générer score système global
        avg_agent_quality = sum(
            agent["avg_quality"] for agent in agents_health.values() if "avg_quality" in agent
        ) / len(agents_health)
        
        # Score d'apprentissage (tend vers 100 avec le temps)
        learning_iterations = await self.feedback_collection.count_documents({})
        learning_score = min(100.0, 50.0 + (learning_iterations / 100.0) * 50.0)
        
        return {
            "system_score": (avg_agent_quality + learning_score) / 2.0,
            "learning_iterations": learning_iterations,
            "success_patterns": success_analysis,
            "failure_patterns": failure_analysis,
            "optimal_ratios": optimal_ratios,
            "agents_health": agents_health,
            "recommendations": self._generate_recommendations(
                success_analysis,
                failure_analysis,
                agents_health
            )
        }
    
    def _generate_recommendations(
        self,
        success_analysis: Dict,
        failure_analysis: Dict,
        agents_health: Dict
    ) -> List[str]:
        """Génère des recommendations basées sur l'apprentissage"""
        
        recommendations = []
        
        # Recommendations basées sur succès
        if success_analysis.get("success_count", 0) > 10:
            recommendations.extend(success_analysis.get("recommendations", []))
        
        # Recommendations basées sur échecs
        if failure_analysis.get("failure_count", 0) > 5:
            recommendations.extend(failure_analysis.get("recommendations", []))
        
        # Recommendations basées sur santé agents
        for agent_name, health in agents_health.items():
            if health.get("status") == "needs_improvement":
                recommendations.append(
                    f"⚠️ Agent {agent_name}: Nécessite optimisation (taux d'erreur élevé)"
                )
        
        # Recommendation générale
        if len(recommendations) == 0:
            recommendations.append("✅ Système optimal - Continue apprentissage")
        
        return recommendations


# Export
__all__ = [
    'GenerationFeedback',
    'PatternLearner',
    'AgentPerformanceTracker',
    'MLLearningSystem'
]
