"""
Vertex AI Helper for Gemini Models
Uses Vertex AI API instead of Google AI Studio to avoid quota issues
"""

import os
import json
import time
from typing import Optional, Dict, Any
import vertexai
from vertexai.generative_models import GenerativeModel, Content, Part
from google.oauth2 import service_account
from src.utils.logging_config import get_logger
from config.config import settings
from src.config.ai_model_config import DEFAULT_AI_MODEL, MODEL_CONFIGS

logger = get_logger(__name__)

class VertexAIHelper:
    """Helper class for using Gemini models through Vertex AI"""
    
    def __init__(self, project_id: Optional[str] = None, location: Optional[str] = None):
        """Initialize Vertex AI with project and location"""
        self.project_id = project_id or settings.google_cloud_project_id
        self.location = location or settings.google_cloud_location
        
        # Initialize Vertex AI
        try:
            vertexai.init(project=self.project_id, location=self.location)
            logger.info(f"Initialized Vertex AI with project: {self.project_id}, location: {self.location}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise
            
        self._models_cache = {}
        
    def get_model(self, model_name: Optional[str] = None) -> GenerativeModel:
        """Get a Gemini model instance through Vertex AI"""
        model_name = model_name or DEFAULT_AI_MODEL
        
        # Cache models to reuse connections
        if model_name not in self._models_cache:
            try:
                # Map model names to Vertex AI model IDs
                vertex_model_name = self._map_to_vertex_model(model_name)
                self._models_cache[model_name] = GenerativeModel(vertex_model_name)
                logger.info(f"Created Vertex AI model: {vertex_model_name}")
            except Exception as e:
                logger.error(f"Failed to create Vertex AI model {model_name}: {e}")
                raise
                
        return self._models_cache[model_name]
    
    def _map_to_vertex_model(self, model_name: str) -> str:
        """Map model names to Vertex AI model IDs"""
        # Vertex AI uses different model naming
        mapping = {
            "gemini-2.5-flash-lite": "gemini-2.0-flash-exp",  # Use flash-exp as lite alternative
            "gemini-2.5-flash": "gemini-1.5-flash-002",
            "gemini-2.5-pro": "gemini-1.5-pro-002",
            "gemini-1.5-flash": "gemini-1.5-flash-002",
            "gemini-2.0-flash-preview-image-generation": "gemini-pro-vision"
        }
        
        return mapping.get(model_name, "gemini-1.5-flash-002")  # Default to flash
    
    def generate_content(self, 
                        prompt: str, 
                        model_name: Optional[str] = None,
                        temperature: Optional[float] = None,
                        max_tokens: Optional[int] = None) -> str:
        """Generate content using Vertex AI Gemini model"""
        
        model = self.get_model(model_name)
        
        # Get model config
        model_config = MODEL_CONFIGS.get(model_name or DEFAULT_AI_MODEL, {})
        temperature = temperature or model_config.get("temperature", 0.7)
        max_tokens = max_tokens or model_config.get("max_tokens", 8192)
        
        try:
            # Generate with retries
            for attempt in range(3):
                try:
                    response = model.generate_content(
                        prompt,
                        generation_config={
                            "temperature": temperature,
                            "max_output_tokens": max_tokens,
                            "top_p": 0.95,
                        }
                    )
                    
                    if response.text:
                        return response.text
                    else:
                        logger.warning(f"Empty response from model on attempt {attempt + 1}")
                        
                except Exception as e:
                    logger.warning(f"Generation attempt {attempt + 1} failed: {e}")
                    if attempt < 2:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise
                        
            return ""  # Return empty string if all attempts fail
            
        except Exception as e:
            logger.error(f"Failed to generate content with Vertex AI: {e}")
            raise
    
    def count_tokens(self, text: str, model_name: Optional[str] = None) -> int:
        """Count tokens in text using Vertex AI model"""
        model = self.get_model(model_name)
        
        try:
            # Use the model's count_tokens method
            return model.count_tokens(text).total_tokens
        except Exception as e:
            logger.warning(f"Failed to count tokens: {e}")
            # Fallback to rough estimation
            return len(text.split()) * 2  # Rough approximation

# Global instance for easy access
vertex_ai_helper = VertexAIHelper()