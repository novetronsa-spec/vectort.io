"""
Agent Self-Healing (Agent 12)
Agent qui peut auto-réparer et améliorer la plateforme Vectort.io
"""

import logging
import os
import ast
from typing import Dict, List, Optional
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)


class SelfHealingAgent:
    """
    Agent 12 - Self-Healing & Auto-Amélioration
    
    Responsabilités CRITIQUES:
    - Détecter bugs et problèmes dans Vectort.io
    - Proposer corrections de code
    - Améliorer performances du système
    - Optimiser l'architecture
    - S'adapter aux nouveaux besoins
    - Maintenir l'équilibre parfait du système
    """
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.logger = logging.getLogger("Agent-SelfHealing")
        self.detected_issues = []
        self.applied_fixes = []
    
    async def diagnose_system(self, system_metrics: Dict) -> Dict:
        """
        Diagnostic complet du système Vectort.io
        
        Args:
            system_metrics: Métriques système (performance, erreurs, etc.)
        
        Returns:
            Rapport de diagnostic avec problèmes détectés
        """
        
        self.logger.info("🔧 Agent Self-Healing: Diagnostic système")
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id="self-healing-diagnostic",
            system_message=self._get_diagnostic_system_message()
        )
        
        prompt = self._build_diagnostic_prompt(system_metrics)
        
        try:
            response = await chat.with_model("openai", "gpt-4o").send_message(
                UserMessage(text=prompt)
            )
            
            # Parser les problèmes détectés
            issues = self._parse_issues(response)
            
            self.detected_issues.extend(issues)
            
            self.logger.info(f"✅ Diagnostic: {len(issues)} problèmes détectés")
            
            return {
                "issues": issues,
                "severity_high": len([i for i in issues if i.get("severity") == "high"]),
                "severity_medium": len([i for i in issues if i.get("severity") == "medium"]),
                "severity_low": len([i for i in issues if i.get("severity") == "low"]),
                "recommendations": [i.get("recommendation") for i in issues]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Diagnostic erreur: {e}")
            return {"issues": [], "error": str(e)}
    
    async def propose_fixes(self, issues: List[Dict]) -> List[Dict]:
        """
        Propose des corrections pour les problèmes détectés
        
        Args:
            issues: Liste des problèmes à corriger
        
        Returns:
            Liste de corrections proposées avec code
        """
        
        self.logger.info(f"🔧 Agent Self-Healing: Proposition de {len(issues)} corrections")
        
        fixes = []
        
        for issue in issues:
            if issue.get("severity") in ["high", "medium"]:
                fix = await self._generate_fix(issue)
                if fix:
                    fixes.append(fix)
        
        self.logger.info(f"✅ {len(fixes)} corrections proposées")
        
        return fixes
    
    async def _generate_fix(self, issue: Dict) -> Optional[Dict]:
        """Génère une correction pour un problème spécifique"""
        
        chat = LlmChat(
            api_key=self.api_key,
            session_id=f"fix-{issue.get('id', 'unknown')}",
            system_message=self._get_fix_system_message()
        )
        
        prompt = f"""GÉNÈRE UNE CORRECTION pour ce problème:

PROBLÈME:
Type: {issue.get('type')}
Sévérité: {issue.get('severity')}
Description: {issue.get('description')}
Fichier affecté: {issue.get('file')}
Ligne: {issue.get('line')}

CONTEXTE:
{issue.get('context', 'Aucun contexte')}

MISSION:
Fournis le code de correction EXACT à appliquer.

Format de réponse:
FICHIER: chemin/vers/fichier.py
LIGNE: numéro
ANCIEN_CODE:
```python
# code actuel
```

NOUVEAU_CODE:
```python
# code corrigé
```

EXPLICATION: Pourquoi cette correction résout le problème"""
        
        try:
            response = await chat.with_model("openai", "gpt-4o").send_message(
                UserMessage(text=prompt)
            )
            
            # Parser la correction
            fix = self._parse_fix(response, issue)
            
            if fix:
                self.logger.info(f"✅ Correction générée pour: {issue.get('type')}")
                return fix
            
        except Exception as e:
            self.logger.error(f"❌ Erreur génération correction: {e}")
        
        return None
    
    def _get_diagnostic_system_message(self) -> str:
        """System message pour diagnostic"""
        
        return """Tu es l'Agent Self-Healing (Agent 12) - Le MÉDECIN du système.

Ton rôle CRITIQUE:
1. Diagnostiquer les problèmes dans Vectort.io
2. Détecter bugs, erreurs, inefficacités
3. Identifier opportunités d'amélioration
4. Analyser la santé globale du système
5. Garantir l'équilibre parfait

Tu analyses:
- Performance (temps de réponse, charge)
- Erreurs et exceptions
- Qualité du code
- Architecture
- Sécurité
- Évolutivité

Tu catégorises par sévérité:
- HIGH: Bug critique, erreur bloquante
- MEDIUM: Performance dégradée, code non optimal
- LOW: Amélioration possible, optimisation mineure

Tu fournis des diagnostics PRÉCIS et ACTIONNABLES."""
    
    def _get_fix_system_message(self) -> str:
        """System message pour génération de corrections"""
        
        return """Tu es l'Agent Self-Healing - Expert en CORRECTION DE CODE.

Ton rôle:
1. Générer des corrections EXACTES et TESTÉES
2. Code production-ready sans bugs
3. Respecter l'architecture existante
4. Améliorer la performance si possible
5. Maintenir la cohérence du système

Principes de correction:
- Minimal et ciblé (ne change que le nécessaire)
- Testé mentalement (pas de nouvelles erreurs)
- Documenté (explique le pourquoi)
- Backward compatible
- Performance optimale

Tu génères du code Python/JavaScript EXACT et FONCTIONNEL."""
    
    def _build_diagnostic_prompt(self, system_metrics: Dict) -> str:
        """Construit le prompt de diagnostic"""
        
        error_rate = system_metrics.get("error_rate", 0)
        avg_response_time = system_metrics.get("avg_response_time", 0)
        system_load = system_metrics.get("system_load", 0)
        recent_errors = system_metrics.get("recent_errors", [])
        
        prompt = f"""DIAGNOSTIC SYSTÈME VECTORT.IO

MÉTRIQUES ACTUELLES:
- Taux d'erreur: {error_rate:.2%}
- Temps de réponse moyen: {avg_response_time:.2f}s
- Charge système: {system_load:.1f}%

ERREURS RÉCENTES ({len(recent_errors)}):
{self._format_errors(recent_errors)}

OBJECTIFS:
- Taux d'erreur: <1%
- Temps réponse: <90s
- Charge: <80%
- Score qualité: 100/100

MISSION:
Analyse ces métriques et identifie TOUS les problèmes.

Format de réponse pour chaque problème:
PROBLÈME:
Type: [performance|bug|security|architecture|other]
Sévérité: [high|medium|low]
Description: Description claire du problème
Fichier: chemin/vers/fichier si applicable
Ligne: numéro de ligne si applicable
Impact: Impact sur le système (1-10)
Recommendation: Action recommandée

Analyse COMPLÈTE maintenant."""
        
        return prompt
    
    def _format_errors(self, errors: List[str]) -> str:
        """Formate les erreurs pour affichage"""
        if not errors:
            return "Aucune erreur récente"
        
        return "\n".join(f"- {error[:100]}" for error in errors[:10])
    
    def _parse_issues(self, response: str) -> List[Dict]:
        """Parse les problèmes détectés"""
        
        issues = []
        
        lines = response.split('\n')
        current_issue = {}
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('PROBLÈME:'):
                if current_issue:
                    issues.append(current_issue)
                current_issue = {"id": len(issues) + 1}
            
            elif ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                
                if key in ['type', 'sévérité', 'severity', 'description', 'fichier', 'file', 'ligne', 'line', 'impact', 'recommendation']:
                    current_issue[key] = value
        
        # Ajouter le dernier
        if current_issue:
            issues.append(current_issue)
        
        return issues
    
    def _parse_fix(self, response: str, issue: Dict) -> Optional[Dict]:
        """Parse une correction proposée"""
        
        import re
        
        # Extraire fichier
        file_match = re.search(r'FICHIER:\s*([^\n]+)', response)
        file_path = file_match.group(1).strip() if file_match else issue.get('file')
        
        # Extraire ancien code
        old_code_match = re.search(r'ANCIEN_CODE:\s*```(?:python|javascript)?\n(.*?)```', response, re.DOTALL)
        old_code = old_code_match.group(1).strip() if old_code_match else None
        
        # Extraire nouveau code
        new_code_match = re.search(r'NOUVEAU_CODE:\s*```(?:python|javascript)?\n(.*?)```', response, re.DOTALL)
        new_code = new_code_match.group(1).strip() if new_code_match else None
        
        # Extraire explication
        explanation_match = re.search(r'EXPLICATION:\s*([^\n]+(?:\n(?!FICHIER:|ANCIEN_CODE:|NOUVEAU_CODE:).+)*)', response)
        explanation = explanation_match.group(1).strip() if explanation_match else ""
        
        if file_path and new_code:
            return {
                "issue_id": issue.get("id"),
                "file": file_path,
                "old_code": old_code,
                "new_code": new_code,
                "explanation": explanation,
                "auto_apply": issue.get("severity") == "high"  # Auto-appliquer si critique
            }
        
        return None
    
    async def apply_fix(self, fix: Dict, dry_run: bool = True) -> Dict:
        """
        Applique une correction (avec dry-run par défaut pour sécurité)
        
        Args:
            fix: Correction à appliquer
            dry_run: Si True, simule sans appliquer réellement
        
        Returns:
            Résultat de l'application
        """
        
        if dry_run:
            self.logger.info(f"🔍 DRY-RUN: Simulation de correction pour {fix['file']}")
            return {
                "success": True,
                "dry_run": True,
                "message": "Correction simulée avec succès",
                "fix": fix
            }
        
        # En production, on NE modifie PAS automatiquement
        # On génère un rapport pour review humaine
        self.logger.info(f"⚠️ Correction nécessite review humaine: {fix['file']}")
        
        self.applied_fixes.append({
            "fix": fix,
            "status": "pending_review",
            "timestamp": "now"
        })
        
        return {
            "success": False,
            "dry_run": False,
            "message": "Correction en attente de review humaine",
            "fix": fix
        }
    
    def get_system_health_score(self, system_metrics: Dict) -> float:
        """
        Calcule un score de santé du système /100
        
        Formule mathématique optimale:
        Health = (performance * 0.3) + (reliability * 0.3) + (security * 0.2) + (efficiency * 0.2)
        """
        
        # Performance (0-100)
        avg_time = system_metrics.get("avg_response_time", 90)
        performance = max(0, 100 - (avg_time / 90 * 50))  # 90s = target
        
        # Fiabilité (0-100)
        error_rate = system_metrics.get("error_rate", 0)
        reliability = max(0, 100 - (error_rate * 1000))  # <1% erreurs
        
        # Sécurité (0-100)
        security_issues = len([i for i in self.detected_issues if i.get("type") == "security"])
        security = max(0, 100 - (security_issues * 20))
        
        # Efficacité (0-100)
        system_load = system_metrics.get("system_load", 50)
        efficiency = max(0, 100 - (system_load / 80 * 100))  # <80% load optimal
        
        # Score pondéré
        health_score = (
            performance * 0.3 +
            reliability * 0.3 +
            security * 0.2 +
            efficiency * 0.2
        )
        
        self.logger.info(f"📊 Score santé système: {health_score:.1f}/100")
        
        return health_score
