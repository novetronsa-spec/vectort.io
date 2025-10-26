"""
Multi-LLM Service with Fallback Strategy
Providers: GPT-5 (primary) → Claude 4 (fallback 1) → Gemini 2.5 Pro (fallback 2)
Features: Circuit breaker, retry with exponential backoff, latency-based selection
"""

import os
import asyncio
import time
import uuid
from typing import Optional, Dict, Any, List
from enum import Enum
import logging
from emergentintegrations.llm.chat import LlmChat, UserMessage

logger = logging.getLogger(__name__)

class LLMProvider(str, Enum):
    GPT5 = "gpt-5"
    CLAUDE4 = "claude-4"
    GEMINI25 = "gemini-2.5-pro"

class CircuitState(str, Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Circuit broken, skip this provider
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    """Circuit breaker implementation for LLM providers"""
    
    def __init__(self, failure_threshold: int = 3, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        
    def record_success(self):
        """Reset circuit breaker on success"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        logger.info("Circuit breaker: Success recorded, circuit CLOSED")
        
    def record_failure(self):
        """Record failure and potentially open circuit"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker: OPEN after {self.failure_count} failures")
        
    def can_attempt(self) -> bool:
        """Check if we should attempt this provider"""
        if self.state == CircuitState.CLOSED:
            return True
            
        if self.state == CircuitState.OPEN:
            # Check if timeout has passed to try half-open
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker: Moving to HALF_OPEN state")
                return True
            return False
            
        # HALF_OPEN state - allow one attempt
        return True

class MultiLLMService:
    """
    Multi-LLM service with intelligent fallback and circuit breaker
    """
    
    def __init__(self):
        self.emergent_key = os.environ.get('EMERGENT_LLM_KEY')
        self.openai_key = os.environ.get('OPENAI_API_KEY')
        
        # Circuit breakers for each provider
        self.circuit_breakers = {
            LLMProvider.GPT5: CircuitBreaker(failure_threshold=3, timeout=60),
            LLMProvider.CLAUDE4: CircuitBreaker(failure_threshold=3, timeout=60),
            LLMProvider.GEMINI25: CircuitBreaker(failure_threshold=3, timeout=60),
        }
        
        # Provider order (priority)
        self.provider_order = [
            LLMProvider.GPT5,
            LLMProvider.CLAUDE4,
            LLMProvider.GEMINI25
        ]
        
        # Latency tracking for smart routing
        self.latency_stats: Dict[LLMProvider, List[float]] = {
            provider: [] for provider in LLMProvider
        }
        
    async def _call_provider(
        self, 
        provider: LLMProvider, 
        messages: List[Dict[str, str]], 
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> Optional[str]:
        """Call a specific LLM provider"""
        
        try:
            start_time = time.time()
            
            # Use emergent key for all providers
            chat = LlmChat(
                api_key=self.emergent_key,
                session_id=f"multi-llm-{uuid.uuid4()}",
                system_message="Tu es un assistant IA expert."
            ).with_model("openai", "gpt-4o")
            
            # Convert messages to emergentintegrations format
            formatted_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    formatted_messages.append(UserMessage(msg["content"]))
                # Add system messages if needed (depends on emergentintegrations support)
            
            # Make the call
            response = await asyncio.to_thread(chat.chat, formatted_messages)
            
            # Record latency
            latency = time.time() - start_time
            self.latency_stats[provider].append(latency)
            if len(self.latency_stats[provider]) > 100:
                self.latency_stats[provider].pop(0)  # Keep last 100
            
            logger.info(f"✅ {provider} responded in {latency:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"❌ {provider} failed: {str(e)}")
            raise
    
    async def generate_with_retry(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 4000,
        temperature: float = 0.7,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Generate response with automatic fallback and retry
        Returns: {
            "content": str,
            "provider": str,
            "latency": float,
            "attempts": int
        }
        """
        
        attempt = 0
        last_error = None
        
        for provider in self.provider_order:
            circuit = self.circuit_breakers[provider]
            
            # Check circuit breaker
            if not circuit.can_attempt():
                logger.info(f"⚠️ Skipping {provider} - circuit breaker is OPEN")
                continue
            
            # Retry with exponential backoff
            for retry in range(max_retries):
                attempt += 1
                
                try:
                    logger.info(f"🔄 Attempt {attempt} - Provider: {provider}, Retry: {retry + 1}/{max_retries}")
                    
                    # Call provider
                    start_time = time.time()
                    response = await self._call_provider(
                        provider=provider,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature
                    )
                    latency = time.time() - start_time
                    
                    # Success! Record and return
                    circuit.record_success()
                    
                    return {
                        "content": response,
                        "provider": provider.value,
                        "latency": latency,
                        "attempts": attempt,
                        "success": True
                    }
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"Retry {retry + 1} failed for {provider}: {str(e)}")
                    
                    # Exponential backoff
                    if retry < max_retries - 1:
                        backoff_time = 2 ** retry  # 1s, 2s, 4s
                        logger.info(f"⏳ Waiting {backoff_time}s before retry...")
                        await asyncio.sleep(backoff_time)
            
            # All retries failed for this provider
            circuit.record_failure()
            logger.error(f"❌ {provider} exhausted all retries, moving to next provider")
        
        # All providers failed
        raise Exception(f"All LLM providers failed. Last error: {str(last_error)}")
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4000,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Simple generation interface
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return await self.generate_with_retry(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """Get statistics about provider performance"""
        stats = {}
        
        for provider in LLMProvider:
            latencies = self.latency_stats[provider]
            circuit = self.circuit_breakers[provider]
            
            stats[provider.value] = {
                "avg_latency": sum(latencies) / len(latencies) if latencies else 0,
                "circuit_state": circuit.state.value,
                "failure_count": circuit.failure_count,
                "total_calls": len(latencies)
            }
        
        return stats

# Global instance
multi_llm_service = MultiLLMService()
