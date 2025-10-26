"""
Project Iteration System
Allows users to chat with AI to improve their projects iteratively
"""

from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime


class ChatMessage(BaseModel):
    """Single message in project chat"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.utcnow()


class ProjectIteration(BaseModel):
    """Represents one iteration of a project"""
    iteration_number: int
    user_request: str  # What user asked for
    changes_made: List[str]  # List of changes AI made
    code_snapshot: Dict[str, str]  # Full code at this iteration
    timestamp: datetime = datetime.utcnow()


class IterationRequest(BaseModel):
    """Request to iterate/improve a project"""
    instruction: str  # User's improvement request
    context: Optional[str] = None  # Additional context


class RegenerateRequest(BaseModel):
    """Request to completely regenerate project"""
    new_description: str
    keep_context: bool = True  # Keep conversation history


async def create_iteration_prompt(
    original_description: str,
    current_code: Dict[str, str],
    chat_history: List[ChatMessage],
    new_instruction: str
) -> str:
    """
    Create a prompt for iterating on existing code
    
    Args:
        original_description: Original project description
        current_code: Current code structure
        chat_history: Previous conversation
        new_instruction: New improvement request
    
    Returns:
        Formatted prompt for LLM
    """
    
    # Build context from chat history
    history_context = "\n".join([
        f"{msg.role.upper()}: {msg.content}"
        for msg in chat_history[-5:]  # Last 5 messages
    ])
    
    # Extract code summary
    code_summary = []
    if current_code.get("react_code"):
        code_summary.append(f"- React code: {len(current_code['react_code'])} characters")
    if current_code.get("html_code"):
        code_summary.append(f"- HTML: {len(current_code['html_code'])} characters")
    if current_code.get("css_code"):
        code_summary.append(f"- CSS: {len(current_code['css_code'])} characters")
    if current_code.get("backend_code"):
        code_summary.append(f"- Backend: {len(current_code['backend_code'])} characters")
    
    code_info = "\n".join(code_summary)
    
    prompt = f"""Tu es un expert en développement qui améliore un projet existant.

## PROJET ACTUEL

**Description originale:**
{original_description}

**Code actuel:**
{code_info}

**Historique de conversation:**
{history_context if history_context else "Aucune conversation précédente"}

## NOUVELLE DEMANDE

{new_instruction}

## INSTRUCTIONS

1. Analyse le code actuel et la demande
2. Identifie les modifications nécessaires
3. Génère le code amélioré COMPLET (pas de snippets)
4. Maintiens la cohérence avec le code existant
5. Explique les changements apportés

**IMPORTANT:** 
- Fournis TOUT le code modifié, pas juste les changements
- Garde la même structure de projet
- Assure-toi que tout fonctionne ensemble
- Si tu ajoutes des features, update aussi le CSS/backend si nécessaire

Retourne le code dans ce format JSON:
{{
    "html_code": "...",
    "css_code": "...",
    "js_code": "...",
    "react_code": "...",
    "backend_code": "...",
    "changes_made": [
        "Ajout de la fonctionnalité X",
        "Amélioration du style Y",
        "Fix du bug Z"
    ],
    "explanation": "Résumé des modifications..."
}}
"""
    
    return prompt


def extract_changes_from_response(response: str) -> List[str]:
    """
    Extract list of changes from AI response
    """
    import json
    import re
    
    try:
        # Try to parse as JSON first
        data = json.loads(response)
        if "changes_made" in data:
            return data["changes_made"]
    except:
        pass
    
    # Fallback: extract from text
    changes = []
    
    # Look for bullet points or numbered lists
    patterns = [
        r'[-*]\s*(.+)',  # - item or * item
        r'\d+\.\s*(.+)',  # 1. item
        r'(?:Added|Changed|Fixed|Improved|Updated):\s*(.+)',  # Action: description
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, response, re.MULTILINE)
        changes.extend(matches)
    
    # Clean up
    changes = [c.strip() for c in changes if c.strip()]
    
    # If still empty, create generic message
    if not changes:
        changes = ["Code amélioré selon vos instructions"]
    
    return changes[:10]  # Max 10 items


__all__ = [
    'ChatMessage',
    'ProjectIteration',
    'IterationRequest',
    'RegenerateRequest',
    'create_iteration_prompt',
    'extract_changes_from_response'
]
