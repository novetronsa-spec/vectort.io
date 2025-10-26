"""
Caching utilities for LLM responses
"""

import hashlib
import json
from functools import lru_cache
from typing import Optional, Dict, Any

def generate_cache_key(description: str, framework: str, project_type: str, advanced_mode: bool = False) -> str:
    """
    Generate a deterministic cache key for AI generation requests
    
    Args:
        description: Project description
        framework: Framework (react, vue, etc.)
        project_type: Type of project
        advanced_mode: Whether advanced mode is enabled
    
    Returns:
        SHA256 hash of the normalized request
    """
    cache_data = {
        "description": description.lower().strip(),
        "framework": framework.lower() if framework else "react",
        "type": project_type.lower(),
        "advanced": advanced_mode
    }
    
    # Create deterministic JSON string
    cache_string = json.dumps(cache_data, sort_keys=True)
    
    # Generate SHA256 hash
    return hashlib.sha256(cache_string.encode()).hexdigest()


# In-memory LRU cache for recent generations (1000 items)
@lru_cache(maxsize=1000)
def get_cached_generation_key(cache_key: str) -> Optional[str]:
    """
    LRU cache decorator for cache keys
    Returns the cache key if it exists in memory
    """
    return cache_key


def sanitize_prompt(prompt: str, max_length: int = 5000) -> str:
    """
    Sanitize user prompt to prevent injection attacks
    
    Args:
        prompt: Raw user input
        max_length: Maximum allowed length
    
    Returns:
        Sanitized prompt
    """
    # Limit length
    if len(prompt) > max_length:
        prompt = prompt[:max_length]
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # Scripts
        r'javascript:',  # JS execution
        r'on\w+\s*=',  # Event handlers
        r'eval\s*\(',  # Eval
        r'exec\s*\(',  # Exec
    ]
    
    import re
    for pattern in dangerous_patterns:
        prompt = re.sub(pattern, '', prompt, flags=re.IGNORECASE | re.DOTALL)
    
    # Basic HTML escape
    prompt = prompt.replace('<', '&lt;').replace('>', '&gt;')
    
    return prompt.strip()


def estimate_llm_cost(model: str, tokens: int) -> float:
    """
    Estimate LLM API cost
    
    Args:
        model: Model name (gpt-5, claude-4, etc.)
        tokens: Estimated tokens used
    
    Returns:
        Estimated cost in USD
    """
    # Pricing per 1K tokens (approximate)
    pricing = {
        "gpt-5": 0.03,  # $0.03 per 1K tokens
        "gpt-4": 0.02,
        "claude-4": 0.025,
        "claude-sonnet-4": 0.025,
        "gemini-2.5-pro": 0.015,
    }
    
    # Default pricing if model not found
    default_price = 0.02
    
    # Get price per 1K tokens
    price_per_1k = pricing.get(model, default_price)
    
    # Calculate cost
    cost = (tokens / 1000) * price_per_1k
    
    return round(cost, 4)


__all__ = [
    'generate_cache_key',
    'get_cached_generation_key',
    'sanitize_prompt',
    'estimate_llm_cost'
]
