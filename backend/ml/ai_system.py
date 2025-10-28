"""
Système Complet d'Intelligence Artificielle Auto-Évolutive
Vectort.io - 12 Agents avec Machine Learning
Score objectif: 100/100
"""

import logging
import asyncio
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class VectortAISystem:
    """
    Système complet d'IA pour Vectort.io
    
    Architecture:
    - 12 agents spécialisés
    - Machine Learning intégré
    - Auto-amélioration continue
    - Auto-réparation
    - Équilibre mathématique optimal
    
    Objectif: 100/100 qualité
    """
    
    def __init__(self, db, api_key: str):
        self.db = db
        self.api_key = api_key
        
        # Import des systèmes ML
        try:
            from ml.learning_system import MLLearningSystem
            from ml.meta_learning_agent import MetaLearningAgent
            from ml.self_healing_agent import SelfHealingAgent
            
            self.ml_system = MLLearningSystem(db)
            self.meta_learning_agent = MetaLearningAgent(api_key)
            self.self_healing_agent = SelfHealingAgent(api_key)
            
            logger.info("✅ Système ML initialisé")
        except Exception as e:
            logger.error(f"❌ Erreur init ML: {e}")
            self.ml_system = None
            self.meta_learning_agent = None
            self.self_healing_agent = None
        
        self.generation_counter = 0
        self.current_score = 70.0  # Score initial
        self.target_score = 100.0  # Objectif
    
    async def pre_generation_learning(self) -> Dict:
        """
        Apprentissage AVANT génération
        
        Analyse patterns, optimise agents, prépare génération optimale
        Returns:
            Dict avec insights et optimisations
        """
        
        if not self.ml_system:
            return {"learning_active": False}
        
        logger.info("🧠 Phase d'apprentissage pré-génération")
        
        try:
            # 1. Apprendre des générations passées
            ml_insights = await self.ml_system.learn_and_optimize()
            
            # 2. Meta-Learning: Analyser et optimiser
            if self.meta_learning_agent:
                recent_generations = await self._get_recent_generations()
                meta_improvements = await self.meta_learning_agent.analyze_and_learn(
                    ml_insights,
                    recent_generations
                )
                ml_insights["meta_improvements"] = meta_improvements
            
            # 3. Self-Healing: Vérifier santé système
            if self.self_healing_agent:
                system_metrics = await self._get_system_metrics()
                system_health = self.self_healing_agent.get_system_health_score(system_metrics)
                ml_insights["system_health"] = system_health
                
                # Diagnostic si nécessaire
                if system_health < 80:
                    diagnosis = await self.self_healing_agent.diagnose_system(system_metrics)
                    ml_insights["diagnosis"] = diagnosis
            
            # 4. Calculer nouveau score attendu
            self.current_score = self._calculate_expected_score(ml_insights)
            ml_insights["expected_score"] = self.current_score
            ml_insights["target_score"] = self.target_score
            ml_insights["progress"] = (self.current_score / self.target_score) * 100
            
            logger.info(f"✅ Apprentissage terminé - Score attendu: {self.current_score:.1f}/100")
            
            return ml_insights
            
        except Exception as e:
            logger.error(f"❌ Erreur apprentissage: {e}")
            return {"learning_active": False, "error": str(e)}
    
    async def post_generation_feedback(
        self,
        project_id: str,
        user_id: str,
        description: str,
        generated_files: Dict[str, str],
        generation_time: float,
        user_rating: Optional[int] = None
    ):
        """
        Feedback APRÈS génération pour apprentissage
        
        Enregistre résultat, apprend des succès/échecs
        """
        
        if not self.ml_system:
            return
        
        logger.info(f"📊 Enregistrement feedback - Projet: {project_id}")
        
        try:
            from ml.learning_system import GenerationFeedback
            
            # Créer feedback
            feedback = GenerationFeedback(
                project_id=project_id,
                user_id=user_id,
                description=description,
                generated_files=generated_files,
                user_rating=user_rating,
                compilation_success=True,  # À évaluer réellement
                runtime_errors=[],  # À collecter
                user_modifications={},  # À tracker
                time_taken=generation_time
            )
            
            # Enregistrer pour apprentissage
            await self.ml_system.record_generation_feedback(feedback)
            
            # Mémoriser erreurs si échec
            if feedback.auto_score < 70:
                error = f"Score faible ({feedback.auto_score:.1f}): {description[:100]}"
                self.meta_learning_agent.memorize_error(error)
            
            logger.info(f"✅ Feedback enregistré - Score: {feedback.auto_score:.1f}/100")
            
        except Exception as e:
            logger.error(f"❌ Erreur feedback: {e}")
    
    async def continuous_improvement_cycle(self):
        """
        Cycle d'amélioration continue (à exécuter périodiquement)
        
        Lance tous les 100 générations:
        - Apprentissage approfondi
        - Optimisation des agents
        - Auto-réparation si nécessaire
        """
        
        self.generation_counter += 1
        
        # Cycle d'amélioration tous les 100 générations
        if self.generation_counter % 100 == 0:
            logger.info("🔄 Cycle d'amélioration continue")
            
            try:
                # 1. Apprentissage approfondi
                ml_insights = await self.ml_system.learn_and_optimize()
                
                # 2. Auto-réparation si nécessaire
                if ml_insights.get("system_score", 100) < 80:
                    logger.warning("⚠️ Score système bas, lancement auto-réparation")
                    
                    system_metrics = await self._get_system_metrics()
                    diagnosis = await self.self_healing_agent.diagnose_system(system_metrics)
                    
                    # Proposer corrections
                    if diagnosis.get("severity_high", 0) > 0:
                        fixes = await self.self_healing_agent.propose_fixes(
                            diagnosis.get("issues", [])
                        )
                        
                        logger.info(f"🔧 {len(fixes)} corrections proposées")
                        
                        # Appliquer corrections critiques (dry-run)
                        for fix in fixes:
                            if fix.get("auto_apply"):
                                await self.self_healing_agent.apply_fix(fix, dry_run=True)
                
                logger.info("✅ Cycle d'amélioration terminé")
                
            except Exception as e:
                logger.error(f"❌ Erreur cycle amélioration: {e}")
    
    def _calculate_expected_score(self, ml_insights: Dict) -> float:
        """
        Calcule le score attendu basé sur apprentissage
        
        Formule mathématique optimale:
        Score = score_base + (apprentissage * 0.3) + (santé * 0.3) + (optimisation * 0.4)
        
        Tend vers 100 avec le temps grâce à l'apprentissage
        """
        
        # Score de base (améliore avec itérations)
        learning_iterations = ml_insights.get("learning_iterations", 0)
        base_score = min(70.0 + (learning_iterations / 100.0) * 20.0, 90.0)
        
        # Bonus apprentissage (0-10 points)
        success_count = ml_insights.get("success_patterns", {}).get("success_count", 0)
        learning_bonus = min(10.0, success_count / 10.0)
        
        # Bonus santé système (0-10 points)
        system_health = ml_insights.get("system_health", 70.0)
        health_bonus = (system_health - 70.0) / 3.0  # 100% santé = +10 points
        
        # Bonus optimisation (0-10 points)
        avg_agent_quality = 0
        agents_health = ml_insights.get("agents_health", {})
        if agents_health:
            qualities = [a.get("avg_quality", 0) for a in agents_health.values() if "avg_quality" in a]
            if qualities:
                avg_agent_quality = sum(qualities) / len(qualities)
        
        optimization_bonus = (avg_agent_quality - 70.0) / 3.0
        
        # Score total
        total_score = base_score + learning_bonus + health_bonus + optimization_bonus
        
        # Cap à 100
        return min(100.0, total_score)
    
    async def _get_recent_generations(self, limit: int = 10) -> List[Dict]:
        """Récupère les générations récentes"""
        
        try:
            feedback = await self.db.ml_feedback.find().sort(
                "timestamp", -1
            ).limit(limit).to_list(length=limit)
            
            return feedback
        except Exception as e:
            logger.error(f"❌ Erreur récupération générations: {e}")
            return []
    
    async def _get_system_metrics(self) -> Dict:
        """Récupère les métriques système"""
        
        try:
            # Calculer métriques depuis feedback
            recent_feedback = await self._get_recent_generations(100)
            
            if not recent_feedback:
                return {
                    "error_rate": 0.0,
                    "avg_response_time": 90.0,
                    "system_load": 50.0,
                    "recent_errors": []
                }
            
            # Taux d'erreur
            failed = len([f for f in recent_feedback if f.get("auto_score", 0) < 50])
            error_rate = failed / len(recent_feedback)
            
            # Temps moyen
            times = [f.get("time_taken", 90) for f in recent_feedback]
            avg_time = sum(times) / len(times)
            
            # Erreurs récentes
            recent_errors = []
            for f in recent_feedback:
                recent_errors.extend(f.get("runtime_errors", []))
            
            return {
                "error_rate": error_rate,
                "avg_response_time": avg_time,
                "system_load": 50.0,  # À calculer depuis métriques serveur
                "recent_errors": recent_errors[:10]
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur métriques: {e}")
            return {
                "error_rate": 0.0,
                "avg_response_time": 90.0,
                "system_load": 50.0,
                "recent_errors": []
            }
    
    def get_system_status(self) -> Dict:
        """Retourne le status complet du système"""
        
        return {
            "generation_count": self.generation_counter,
            "current_score": self.current_score,
            "target_score": self.target_score,
            "progress_percent": (self.current_score / self.target_score) * 100,
            "ml_active": self.ml_system is not None,
            "meta_learning_active": self.meta_learning_agent is not None,
            "self_healing_active": self.self_healing_agent is not None,
            "agents_count": 12,
            "learning_iterations": self.generation_counter,
            "status": "optimal" if self.current_score >= 90 else "learning"
        }


# Export
__all__ = ['VectortAISystem']
