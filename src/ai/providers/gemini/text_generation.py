"""
Google Gemini Text Generation Implementation
"""
import google.generativeai as genai
import asyncio
import logging
from typing import List, Dict, Any
from ...interfaces.text_generation import (
    TextGenerationService, 
    TextGenerationRequest, 
    TextGenerationResponse
)
from ...interfaces.base import AIProvider

logger = logging.getLogger(__name__)

class GeminiTextService(TextGenerationService):
    """Google Gemini implementation of text generation"""
    
    def validate_config(self) -> None:
        if not self.config.api_key:
            raise ValueError("Gemini API key required")
        genai.configure(api_key=self.config.api_key)
        self.model = genai.GenerativeModel(self.config.model_name)
    
    async def generate(self, request: TextGenerationRequest) -> TextGenerationResponse:
        try:
            # Build generation config
            generation_config = {
                "temperature": request.temperature,
                "top_p": request.top_p,
            }
            
            if request.max_tokens:
                generation_config["max_output_tokens"] = request.max_tokens
            
            # Add system prompt if provided
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n{request.prompt}"
            
            # Generate response (sync call wrapped in async)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
            )
            
            # Check if response has valid content
            if not response.candidates or not response.candidates[0].content.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else "unknown"
                raise RuntimeError(f"Gemini blocked response (finish_reason: {finish_reason})")
            
            # Handle usage metadata - it may not exist in older API versions
            usage_data = {}
            cost = 0.0
            
            if hasattr(response, 'usage_metadata'):
                # New API version with usage_metadata
                usage_data = {
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count
                }
                cost = self.estimate_cost(
                    input_tokens=response.usage_metadata.prompt_token_count,
                    output_tokens=response.usage_metadata.candidates_token_count
                )
            else:
                # Fallback for older API versions - estimate from text length
                prompt_tokens = len(request.prompt.split()) * 1.3  # Rough estimate
                completion_tokens = len(response.text.split()) * 1.3  # Rough estimate
                usage_data = {
                    "prompt_tokens": int(prompt_tokens),
                    "completion_tokens": int(completion_tokens),
                    "total_tokens": int(prompt_tokens + completion_tokens)
                }
                cost = self.estimate_cost(
                    input_tokens=int(prompt_tokens),
                    output_tokens=int(completion_tokens)
                )
                logger.debug("Using estimated token counts - usage_metadata not available")
            
            return TextGenerationResponse(
                text=response.text,
                usage=usage_data,
                model=self.config.model_name,
                provider="gemini",
                cost_estimate=cost
            )
            
        except Exception as e:
            raise RuntimeError(f"Gemini generation failed: {e}")
    
    async def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation for JSON mode
        request = TextGenerationRequest(
            prompt=f"{prompt}\n\nReturn a valid JSON object matching this schema: {schema}",
            response_format="json"
        )
        response = await self.generate(request)
        
        import json
        return json.loads(response.text)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> TextGenerationResponse:
        # Convert messages to single prompt for Gemini
        prompt_parts = []
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        
        full_prompt = "\n\n".join(prompt_parts)
        
        request = TextGenerationRequest(
            prompt=full_prompt,
            **kwargs
        )
        return await self.generate(request)
    
    def estimate_cost(self, input_tokens: int = 0, output_tokens: int = 0) -> float:
        # Gemini pricing (example rates per 1M tokens)
        pricing = {
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
            "gemini-2.5-flash": {"input": 0.075, "output": 0.30}
        }
        
        rates = pricing.get(self.config.model_name, pricing["gemini-1.5-flash"])
        return ((input_tokens * rates["input"]) + (output_tokens * rates["output"])) / 1_000_000