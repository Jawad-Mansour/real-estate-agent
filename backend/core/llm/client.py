"""
LLM Client - Abstraction for Groq and OpenAI APIs

Supports multiple providers with fallback:
- Primary: Groq (free, fast, Llama 3 70B)
- Fallback: OpenAI (if Groq rate limits or fails)
"""

import os
import time
import random
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Unified client for LLM interactions.
    Automatically falls back to OpenAI if Groq fails.
    """
    
    _instance = None
    _groq_client = None
    _openai_client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMClient, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize clients if API keys are available"""
        # Try Groq
        groq_api_key = os.getenv('GROQ_API_KEY')
        if groq_api_key:
            try:
                from groq import Groq
                self._groq_client = Groq(api_key=groq_api_key)
                logger.info("Groq client initialized")
            except ImportError:
                logger.warning("Groq package not installed")
            except Exception as e:
                logger.warning(f"Groq initialization failed: {e}")
        else:
            logger.warning("GROQ_API_KEY not found in .env")
        
        # Try OpenAI (fallback)
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key:
            try:
                from openai import OpenAI
                self._openai_client = OpenAI(api_key=openai_api_key)
                logger.info("OpenAI client initialized (fallback)")
            except ImportError:
                logger.warning("OpenAI package not installed")
            except Exception as e:
                logger.warning(f"OpenAI initialization failed: {e}")
    
    def get_groq_client(self):
        """Get Groq client if available"""
        return self._groq_client
    
    def get_openai_client(self):
        """Get OpenAI client if available"""
        return self._openai_client
    
    def has_groq(self) -> bool:
        """Check if Groq is available"""
        return self._groq_client is not None
    
    def has_openai(self) -> bool:
        """Check if OpenAI is available"""
        return self._openai_client is not None
    
    @classmethod
    def get_instance(cls) -> "LLMClient":
        """Get singleton instance"""
        return cls()
    
    @classmethod
    def chat_completion(cls, prompt: str, system_prompt: str = None, temperature: float = 0.1, max_tokens: int = 2000, max_retries: int = 3) -> Optional[str]:
        """
        Get chat completion from LLM (Groq primary, OpenAI fallback)
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system instructions
            temperature: Randomness (0 = deterministic, 1 = creative)
            max_tokens: Maximum response length
            max_retries: Number of retry attempts for rate limiting
        
        Returns:
            LLM response text or None if both fail
        """
        instance = cls.get_instance()
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        def _is_rate_limit_error(exc: Exception) -> bool:
            message = str(exc).lower()
            return '429' in message or 'too many requests' in message or 'rate limit' in message

        def _retry_request(callable_func, provider: str) -> Optional[Any]:
            for attempt in range(1, max_retries + 1):
                try:
                    return callable_func()
                except Exception as exc:
                    if _is_rate_limit_error(exc):
                        wait_seconds = (2 ** (attempt - 1)) + random.uniform(0.1, 0.5)
                        logger.warning(
                            f"{provider} rate limited on attempt {attempt}/{max_retries}. "
                            f"Waiting {wait_seconds:.1f}s before retry. Error: {exc}"
                        )
                        if attempt == max_retries:
                            logger.error(f"{provider} rate limit exceeded after {max_retries} retries")
                            return None
                        time.sleep(wait_seconds)
                        continue
                    logger.error(f"{provider} API error: {exc}")
                    return None
            return None

        # Try Groq first
        if instance.has_groq():
            client = instance.get_groq_client()
            if client is not None:
                def groq_request():
                    return client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                response = _retry_request(groq_request, 'Groq')
                if response is not None:
                    logger.info("Groq response received")
                    return response.choices[0].message.content
                logger.warning("Groq request failed or exhausted retries")
        
        # Fallback to OpenAI
        if instance.has_openai():
            client = instance.get_openai_client()
            if client is not None:
                def openai_request():
                    return client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )

                response = _retry_request(openai_request, 'OpenAI')
                if response is not None:
                    logger.info("OpenAI fallback response received")
                    return response.choices[0].message.content
                logger.warning("OpenAI request failed or exhausted retries")

        logger.error("No LLM client available or all requests failed")
        return None
