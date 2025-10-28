"""
Agent Meta-Learning (Agent 11)
Agent qui apprend des performances et optimise les autres agents
"""

import logging
from typing import Dict, List
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class MetaLearningAgent:
    """
    Agent 11 - Meta-Learning
    
    Responsabilités:
    - Analyser les performances des 10 autres agents
    - Identifier ce qui fonctionne et ce qui échoue
    - Ajuster dynamiquement les prompts des agents
    - Apprendre des patterns de succès
    - Ne JAMAIS répéter les erreurs du passé
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger("Agent-MetaLearning")
        self.learned_improvements = []
        self.error_memory = []  # Mémoire des erreurs à ne pas répéter
    
    async def analyze_and_learn(
        self,
        ml_insights: Dict,
        recent_generations: List[Dict]
    ) -> Dict[str, str]:
        """
        Analyse les insights ML et génère des améliorations
        
        Args:
            ml_insights: Insights du système ML
            recent_generations: Dernières générations pour analyse
        
        Returns:
            Dict avec recommendations d'amélioration par agent
        """
        
        self.logger.info("🧠 Agent Meta-Learning: Analyse et apprentissage")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="meta-learning-agent",
            system_message=self._get_system_message()
        )
        
        prompt = self._build_analysis_prompt(ml_insights, recent_generations)
        
        try:
            response = await chat.with_model("openai", "gpt-4o").send_message(
                UserMessage(text=prompt)
            )
            
            # Parser les recommendations
            improvements = self._parse_improvements(response)
            
            # Mémoriser les améliorations
            self.learned_improvements.extend(improvements.get("improvements", []))
            
            self.logger.info(f"✅ Meta-Learning: {len(improvements)} améliorations identifiées")
            
            return improvements
            
        except Exception as e:
            self.logger.error(f"❌ Meta-Learning erreur: {e}")
            return {}
    
    def _get_system_message(self) -> str:
        """System message pour Meta-Learning Agent"""
        
        return """Tu es l'Agent Meta-Learning (Agent 11) - Le CERVEAU du système.

Ton rôle CRITIQUE:
1. Analyser les performances des 10 autres agents
2. Identifier patterns de SUCCÈS et d'ÉCHEC
3. Apprendre continuellement de chaque génération
4. Ne JAMAIS répéter les erreurs du passé
5. Optimiser les prompts et comportements des agents
6. Tendre vers la perfection (score 100/100)

Tu as accès à:
- Insights ML (patterns, ratios, santé des agents)
- Historique des générations (succès et échecs)
- Feedback utilisateurs
- Erreurs et modifications

Principes d'apprentissage:
- Si une approche échoue répétitivement, l'abandonner
- Si une approche réussit, la renforcer
- Équilibrer innovation et stabilité
- Optimiser ratios mathématiques entre agents
- Adaptation continue

Tu réponds avec des recommendations CONCRÈTES et ACTIONNABLES."""
    
    def _build_analysis_prompt(
        self,
        ml_insights: Dict,
        recent_generations: List[Dict]
    ) -> str:
        """Construit le prompt d'analyse"""
        
        system_score = ml_insights.get("system_score", 0)
        success_patterns = ml_insights.get("success_patterns", {})
        failure_patterns = ml_insights.get("failure_patterns", {})
        agents_health = ml_insights.get("agents_health", {})
        optimal_ratios = ml_insights.get("optimal_ratios", {})
        
        prompt = f"""ANALYSE META-LEARNING - Système Vectort.io

ÉTAT ACTUEL:
- Score système: {system_score:.1f}/100 (objectif: 100/100)
- Itérations d'apprentissage: {ml_insights.get('learning_iterations', 0)}
- Générations récentes: {len(recent_generations)}

PATTERNS DE SUCCÈS identifiés:
{self._format_patterns(success_patterns)}

PATTERNS D'ÉCHEC identifiés:
{self._format_patterns(failure_patterns)}

SANTÉ DES AGENTS:
{self._format_agents_health(agents_health)}

RATIOS OPTIMAUX calculés:
{self._format_ratios(optimal_ratios)}

ERREURS À NE PLUS RÉPÉTER:
{self._format_error_memory()}

MISSION:
Analyse ces données et fournis des RECOMMENDATIONS CONCRÈTES pour:

1. AMÉLIORER chaque agent (prompts, comportement, focus)
2. CORRIGER les erreurs récurrentes
3. OPTIMISER les ratios entre agents
4. ATTEINDRE 100/100 de qualité

Format de réponse:
AGENT: nom_agent
AMÉLIORATION: Description concrète de l'amélioration
PROMPT_ADJUSTMENT: Ajustement suggéré du prompt système
PRIORITÉ: haute|moyenne|basse

Réponds pour TOUS les agents nécessitant amélioration."""
        
        return prompt
    
    def _format_patterns(self, patterns: Dict) -> str:
        """Formate les patterns pour affichage"""
        if not patterns:
            return "Aucun pattern significatif"
        
        recommendations = patterns.get("recommendations", [])
        return "\n".join(f"- {rec}" for rec in recommendations[:5])
    
    def _format_agents_health(self, health: Dict) -> str:
        """Formate la santé des agents"""
        if not health:
            return "Données non disponibles"
        
        lines = []
        for agent_name, stats in health.items():
            status = stats.get("status", "unknown")
            quality = stats.get("avg_quality", 0)
            error_rate = stats.get("error_rate", 0)
            
            emoji = "✅" if status == "healthy" else "⚠️"
            lines.append(
                f"{emoji} {agent_name}: qualité {quality:.1f}/100, erreurs {error_rate:.2%}"
            )
        
        return "\n".join(lines)
    
    def _format_ratios(self, ratios: Dict) -> str:
        """Formate les ratios optimaux"""
        if not ratios:
            return "Ratios par défaut"
        
        return "\n".join(f"- {agent}: {ratio:.2%}" for agent, ratio in ratios.items())
    
    def _format_error_memory(self) -> str:
        """Formate la mémoire des erreurs"""
        if not self.error_memory:
            return "Aucune erreur récurrente mémorisée"
        
        return "\n".join(f"- {error}" for error in self.error_memory[-10:])
    
    def _parse_improvements(self, response: str) -> Dict[str, List[Dict]]:
        """Parse les améliorations suggérées"""
        
        improvements = []
        
        lines = response.split('\n')
        current_improvement = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('AGENT:'):
                if current_improvement:
                    improvements.append(current_improvement)
                current_improvement = {"agent": line.split(':', 1)[1].strip()}
            
            elif line.startswith('AMÉLIORATION:'):
                current_improvement["improvement"] = line.split(':', 1)[1].strip()
            
            elif line.startswith('PROMPT_ADJUSTMENT:'):
                current_improvement["prompt_adjustment"] = line.split(':', 1)[1].strip()
            
            elif line.startswith('PRIORITÉ:'):
                current_improvement["priority"] = line.split(':', 1)[1].strip()
        
        # Ajouter le dernier
        if current_improvement:
            improvements.append(current_improvement)
        
        return {"improvements": improvements, "count": len(improvements)}
    
    def memorize_error(self, error: str):
        """Mémorise une erreur à ne plus répéter"""
        if error not in self.error_memory:
            self.error_memory.append(error)
            self.logger.info(f"🧠 Erreur mémorisée: {error[:100]}")
    
    def get_learned_improvements(self) -> List[str]:
        """Retourne les améliorations apprises"""
        return self.learned_improvements
