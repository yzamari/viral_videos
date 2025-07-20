# AI Service Abstraction Layer Plan

## Executive Summary

This document outlines a comprehensive plan to refactor the ViralAI codebase to use an abstraction layer for all AI services. This will enable easy swapping of AI providers (Google Gemini, OpenAI, Anthropic, VEO, etc.) without changing the core business logic.

## Current State Analysis

### Problems with Current Implementation
1. **Tight Coupling**: AI service calls are scattered throughout the codebase
2. **Vendor Lock-in**: Switching providers requires extensive code changes
3. **No Unified Interface**: Each AI service has different calling patterns
4. **Difficult Testing**: Can't easily mock AI services for testing
5. **Cost Management**: Hard to track and optimize AI usage across providers

### Current AI Service Usage
- **Text Generation**: Google Gemini (hardcoded throughout)
- **Video Generation**: VEO-2/VEO-3 (partially abstracted via VeoClientFactory)
- **Audio/TTS**: Google Cloud TTS (direct calls)
- **Image Generation**: Not currently implemented
- **Embeddings**: Not currently implemented

## Proposed Architecture

### Core Design Principles
1. **Interface Segregation**: Separate interfaces for each AI capability
2. **Dependency Injection**: Services receive AI providers through constructor
3. **Provider Agnostic**: Business logic doesn't know which provider is being used
4. **Configuration Driven**: Provider selection via configuration, not code
5. **Graceful Degradation**: Fallback providers for critical services

### Layer Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│              (Business Logic & Workflows)                    │
├─────────────────────────────────────────────────────────────┤
│                  AI Service Interfaces                       │
│   (Abstract base classes defining contracts)                 │
├─────────────────────────────────────────────────────────────┤
│                 AI Service Implementations                   │
│  (Concrete implementations for each provider)                │
├─────────────────────────────────────────────────────────────┤
│                    Provider Adapters                         │
│        (Handle provider-specific API calls)                  │
├─────────────────────────────────────────────────────────────┤
│                   External AI Services                       │
│     (Gemini, GPT-4, Claude, VEO, ElevenLabs, etc.)         │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Design

### 1. Base Interfaces

#### 1.1 Core AI Service Interface
```python
# src/ai/interfaces/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class AIProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    LOCAL = "local"

@dataclass
class AIServiceConfig:
    provider: AIProvider
    api_key: Optional[str]
    model_name: str
    max_retries: int = 3
    timeout: int = 60
    custom_config: Dict[str, Any] = None

class AIService(ABC):
    """Base interface for all AI services"""
    
    def __init__(self, config: AIServiceConfig):
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self) -> None:
        """Validate provider-specific configuration"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Return human-readable provider name"""
        pass
    
    @abstractmethod
    def estimate_cost(self, **kwargs) -> float:
        """Estimate cost for the operation"""
        pass
```

#### 1.2 Text Generation Interface
```python
# src/ai/interfaces/text_generation.py
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .base import AIService

@dataclass
class TextGenerationRequest:
    prompt: str
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    top_p: float = 0.9
    stop_sequences: Optional[List[str]] = None
    system_prompt: Optional[str] = None
    response_format: Optional[str] = None  # "text" or "json"
    
@dataclass
class TextGenerationResponse:
    text: str
    usage: Dict[str, int]  # tokens used, etc.
    model: str
    provider: str
    cost_estimate: float
    metadata: Dict[str, Any] = None

class TextGenerationService(AIService):
    """Interface for text generation services"""
    
    @abstractmethod
    async def generate(self, request: TextGenerationRequest) -> TextGenerationResponse:
        """Generate text based on prompt"""
        pass
    
    @abstractmethod
    async def generate_structured(self, 
                                prompt: str, 
                                schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured output matching schema"""
        pass
    
    @abstractmethod
    async def chat(self, 
                  messages: List[Dict[str, str]], 
                  **kwargs) -> TextGenerationResponse:
        """Chat-based generation with message history"""
        pass
```

#### 1.3 Video Generation Interface
```python
# src/ai/interfaces/video_generation.py
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .base import AIService

@dataclass
class VideoGenerationRequest:
    prompt: str
    duration: float  # seconds
    resolution: str = "720p"
    aspect_ratio: str = "16:9"
    style: Optional[str] = None
    reference_image: Optional[str] = None  # path or URL
    motion_intensity: float = 0.5
    
@dataclass
class VideoGenerationResponse:
    video_path: str
    actual_duration: float
    resolution: str
    provider: str
    generation_time: float
    cost_estimate: float
    metadata: Dict[str, Any] = None

class VideoGenerationService(AIService):
    """Interface for video generation services"""
    
    @abstractmethod
    async def generate(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        """Generate video from prompt"""
        pass
    
    @abstractmethod
    async def generate_batch(self, 
                           requests: List[VideoGenerationRequest]) -> List[VideoGenerationResponse]:
        """Batch video generation for efficiency"""
        pass
    
    @abstractmethod
    def get_max_duration(self) -> float:
        """Get maximum supported duration"""
        pass
    
    @abstractmethod
    def get_supported_resolutions(self) -> List[str]:
        """Get list of supported resolutions"""
        pass
```

#### 1.4 Audio Generation Interface
```python
# src/ai/interfaces/audio_generation.py
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .base import AIService

@dataclass
class TTSRequest:
    text: str
    voice_id: str
    language: str = "en-US"
    speed: float = 1.0
    pitch: float = 0.0
    emotion: Optional[str] = None
    output_format: str = "mp3"
    
@dataclass
class TTSResponse:
    audio_path: str
    duration: float
    voice_id: str
    provider: str
    cost_estimate: float
    metadata: Dict[str, Any] = None

class AudioGenerationService(AIService):
    """Interface for audio generation services"""
    
    @abstractmethod
    async def text_to_speech(self, request: TTSRequest) -> TTSResponse:
        """Convert text to speech"""
        pass
    
    @abstractmethod
    async def get_available_voices(self, language: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of available voices"""
        pass
    
    @abstractmethod
    async def clone_voice(self, audio_samples: List[str]) -> str:
        """Clone voice from audio samples, return voice_id"""
        pass
```

#### 1.5 Image Generation Interface
```python
# src/ai/interfaces/image_generation.py
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from .base import AIService

@dataclass
class ImageGenerationRequest:
    prompt: str
    negative_prompt: Optional[str] = None
    width: int = 1024
    height: int = 1024
    num_images: int = 1
    style: Optional[str] = None
    seed: Optional[int] = None
    
@dataclass
class ImageGenerationResponse:
    image_paths: List[str]
    width: int
    height: int
    provider: str
    generation_time: float
    cost_estimate: float
    metadata: Dict[str, Any] = None

class ImageGenerationService(AIService):
    """Interface for image generation services"""
    
    @abstractmethod
    async def generate(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate images from prompt"""
        pass
    
    @abstractmethod
    async def edit(self, 
                  image_path: str, 
                  prompt: str, 
                  mask_path: Optional[str] = None) -> ImageGenerationResponse:
        """Edit existing image with prompt"""
        pass
    
    @abstractmethod
    async def upscale(self, image_path: str, scale: int = 2) -> str:
        """Upscale image resolution"""
        pass
```

### 2. Provider Implementations

#### 2.1 Gemini Text Implementation
```python
# src/ai/providers/gemini/text_generation.py
import google.generativeai as genai
from typing import List, Dict, Any
from ...interfaces.text_generation import (
    TextGenerationService, 
    TextGenerationRequest, 
    TextGenerationResponse
)

class GeminiTextService(TextGenerationService):
    """Google Gemini implementation of text generation"""
    
    def _validate_config(self) -> None:
        if not self.config.api_key:
            raise ValueError("Gemini API key required")
        genai.configure(api_key=self.config.api_key)
        self.model = genai.GenerativeModel(self.config.model_name)
    
    def get_provider_name(self) -> str:
        return f"Google Gemini ({self.config.model_name})"
    
    async def generate(self, request: TextGenerationRequest) -> TextGenerationResponse:
        try:
            # Build generation config
            generation_config = {
                "temperature": request.temperature,
                "top_p": request.top_p,
                "max_output_tokens": request.max_tokens,
            }
            
            # Add system prompt if provided
            full_prompt = request.prompt
            if request.system_prompt:
                full_prompt = f"{request.system_prompt}\n\n{request.prompt}"
            
            # Generate response
            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=generation_config
            )
            
            # Calculate cost estimate
            cost = self.estimate_cost(
                input_tokens=response.usage_metadata.prompt_token_count,
                output_tokens=response.usage_metadata.candidates_token_count
            )
            
            return TextGenerationResponse(
                text=response.text,
                usage={
                    "prompt_tokens": response.usage_metadata.prompt_token_count,
                    "completion_tokens": response.usage_metadata.candidates_token_count,
                    "total_tokens": response.usage_metadata.total_token_count
                },
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
    
    def estimate_cost(self, input_tokens: int = 0, output_tokens: int = 0) -> float:
        # Gemini pricing (example rates)
        pricing = {
            "gemini-1.5-flash": {"input": 0.00001, "output": 0.00002},
            "gemini-1.5-pro": {"input": 0.00003, "output": 0.00006}
        }
        
        rates = pricing.get(self.config.model_name, pricing["gemini-1.5-flash"])
        return (input_tokens * rates["input"]) + (output_tokens * rates["output"])
```

#### 2.2 OpenAI Text Implementation
```python
# src/ai/providers/openai/text_generation.py
from openai import AsyncOpenAI
from typing import List, Dict, Any
from ...interfaces.text_generation import (
    TextGenerationService, 
    TextGenerationRequest, 
    TextGenerationResponse
)

class OpenAITextService(TextGenerationService):
    """OpenAI implementation of text generation"""
    
    def _validate_config(self) -> None:
        if not self.config.api_key:
            raise ValueError("OpenAI API key required")
        self.client = AsyncOpenAI(api_key=self.config.api_key)
    
    def get_provider_name(self) -> str:
        return f"OpenAI ({self.config.model_name})"
    
    async def generate(self, request: TextGenerationRequest) -> TextGenerationResponse:
        try:
            messages = []
            if request.system_prompt:
                messages.append({"role": "system", "content": request.system_prompt})
            messages.append({"role": "user", "content": request.prompt})
            
            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
                stop=request.stop_sequences
            )
            
            # Calculate cost
            cost = self.estimate_cost(
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens
            )
            
            return TextGenerationResponse(
                text=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                model=response.model,
                provider="openai",
                cost_estimate=cost
            )
            
        except Exception as e:
            raise RuntimeError(f"OpenAI generation failed: {e}")
    
    def estimate_cost(self, input_tokens: int = 0, output_tokens: int = 0) -> float:
        # OpenAI pricing
        pricing = {
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015}
        }
        
        rates = pricing.get(self.config.model_name, pricing["gpt-3.5-turbo"])
        return (input_tokens * rates["input"] / 1000) + (output_tokens * rates["output"] / 1000)
```

### 3. Service Factory & Registry

```python
# src/ai/factory.py
from typing import Dict, Type, Optional
from enum import Enum
from .interfaces.base import AIService, AIProvider, AIServiceConfig
from .interfaces.text_generation import TextGenerationService
from .interfaces.video_generation import VideoGenerationService
from .interfaces.audio_generation import AudioGenerationService
from .interfaces.image_generation import ImageGenerationService

# Provider implementations
from .providers.gemini.text_generation import GeminiTextService
from .providers.openai.text_generation import OpenAITextService
from .providers.anthropic.text_generation import AnthropicTextService
from .providers.veo.video_generation import VeoVideoService
from .providers.google_cloud.tts import GoogleCloudTTSService
from .providers.elevenlabs.tts import ElevenLabsTTSService

class AIServiceType(Enum):
    TEXT_GENERATION = "text_generation"
    VIDEO_GENERATION = "video_generation"
    AUDIO_GENERATION = "audio_generation"
    IMAGE_GENERATION = "image_generation"

class AIServiceFactory:
    """Factory for creating AI service instances"""
    
    # Registry of available implementations
    _registry: Dict[AIServiceType, Dict[AIProvider, Type[AIService]]] = {
        AIServiceType.TEXT_GENERATION: {
            AIProvider.GEMINI: GeminiTextService,
            AIProvider.OPENAI: OpenAITextService,
            AIProvider.ANTHROPIC: AnthropicTextService,
        },
        AIServiceType.VIDEO_GENERATION: {
            AIProvider.GEMINI: VeoVideoService,  # VEO is part of Google
        },
        AIServiceType.AUDIO_GENERATION: {
            AIProvider.GEMINI: GoogleCloudTTSService,
            AIProvider.OPENAI: ElevenLabsTTSService,  # Example mapping
        },
        AIServiceType.IMAGE_GENERATION: {
            AIProvider.OPENAI: OpenAIImageService,
            AIProvider.STABILITY: StabilityImageService,
        }
    }
    
    @classmethod
    def create(cls, 
               service_type: AIServiceType, 
               config: AIServiceConfig) -> AIService:
        """Create an AI service instance"""
        
        if service_type not in cls._registry:
            raise ValueError(f"Unknown service type: {service_type}")
        
        providers = cls._registry[service_type]
        if config.provider not in providers:
            raise ValueError(
                f"Provider {config.provider} not available for {service_type}. "
                f"Available providers: {list(providers.keys())}"
            )
        
        service_class = providers[config.provider]
        return service_class(config)
    
    @classmethod
    def register(cls, 
                service_type: AIServiceType, 
                provider: AIProvider, 
                implementation: Type[AIService]):
        """Register a new implementation"""
        if service_type not in cls._registry:
            cls._registry[service_type] = {}
        cls._registry[service_type][provider] = implementation
    
    @classmethod
    def get_available_providers(cls, service_type: AIServiceType) -> List[AIProvider]:
        """Get list of available providers for a service type"""
        if service_type not in cls._registry:
            return []
        return list(cls._registry[service_type].keys())
```

### 4. Configuration Management

```python
# src/ai/config.py
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
import os
import json
from .factory import AIServiceType, AIProvider
from .interfaces.base import AIServiceConfig

@dataclass
class AIConfiguration:
    """Central AI configuration"""
    
    # Default providers for each service type
    default_providers: Dict[AIServiceType, AIProvider] = field(default_factory=dict)
    
    # Service-specific configurations
    service_configs: Dict[str, AIServiceConfig] = field(default_factory=dict)
    
    # API keys (can be overridden by environment variables)
    api_keys: Dict[AIProvider, str] = field(default_factory=dict)
    
    # Global settings
    enable_fallbacks: bool = True
    enable_caching: bool = True
    enable_cost_tracking: bool = True
    max_retries: int = 3
    
    @classmethod
    def from_file(cls, config_path: str) -> 'AIConfiguration':
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            data = json.load(f)
        
        config = cls()
        
        # Load default providers
        for service_type, provider in data.get('default_providers', {}).items():
            config.default_providers[AIServiceType(service_type)] = AIProvider(provider)
        
        # Load API keys (with env var override)
        for provider, key in data.get('api_keys', {}).items():
            env_key = f"{provider.upper()}_API_KEY"
            config.api_keys[AIProvider(provider)] = os.getenv(env_key, key)
        
        # Load service configs
        for name, cfg in data.get('service_configs', {}).items():
            config.service_configs[name] = AIServiceConfig(**cfg)
        
        return config
    
    def get_service_config(self, 
                          service_type: AIServiceType, 
                          provider: Optional[AIProvider] = None) -> AIServiceConfig:
        """Get configuration for a service"""
        
        # Use specified provider or default
        if provider is None:
            provider = self.default_providers.get(service_type)
            if provider is None:
                raise ValueError(f"No default provider configured for {service_type}")
        
        # Build config
        config_key = f"{service_type.value}_{provider.value}"
        
        if config_key in self.service_configs:
            return self.service_configs[config_key]
        
        # Create default config
        return AIServiceConfig(
            provider=provider,
            api_key=self.api_keys.get(provider),
            model_name=self._get_default_model(service_type, provider),
            max_retries=self.max_retries
        )
    
    def _get_default_model(self, service_type: AIServiceType, provider: AIProvider) -> str:
        """Get default model for provider and service type"""
        defaults = {
            (AIServiceType.TEXT_GENERATION, AIProvider.GEMINI): "gemini-1.5-flash",
            (AIServiceType.TEXT_GENERATION, AIProvider.OPENAI): "gpt-4-turbo",
            (AIServiceType.TEXT_GENERATION, AIProvider.ANTHROPIC): "claude-3-opus",
            (AIServiceType.VIDEO_GENERATION, AIProvider.GEMINI): "veo-2",
            # Add more defaults
        }
        return defaults.get((service_type, provider), "default")
```

### 5. Service Manager (Dependency Injection)

```python
# src/ai/manager.py
from typing import Dict, Optional, TypeVar, Type
from .factory import AIServiceFactory, AIServiceType
from .config import AIConfiguration
from .interfaces.base import AIService
from .interfaces.text_generation import TextGenerationService
from .interfaces.video_generation import VideoGenerationService
from .interfaces.audio_generation import AudioGenerationService
from .interfaces.image_generation import ImageGenerationService

T = TypeVar('T', bound=AIService)

class AIServiceManager:
    """Central manager for all AI services with dependency injection"""
    
    def __init__(self, config: Optional[AIConfiguration] = None):
        self.config = config or AIConfiguration()
        self._services: Dict[str, AIService] = {}
        self._fallback_chains: Dict[AIServiceType, List[AIProvider]] = {}
    
    def get_text_service(self, provider: Optional[AIProvider] = None) -> TextGenerationService:
        """Get text generation service"""
        return self._get_service(AIServiceType.TEXT_GENERATION, TextGenerationService, provider)
    
    def get_video_service(self, provider: Optional[AIProvider] = None) -> VideoGenerationService:
        """Get video generation service"""
        return self._get_service(AIServiceType.VIDEO_GENERATION, VideoGenerationService, provider)
    
    def get_audio_service(self, provider: Optional[AIProvider] = None) -> AudioGenerationService:
        """Get audio generation service"""
        return self._get_service(AIServiceType.AUDIO_GENERATION, AudioGenerationService, provider)
    
    def get_image_service(self, provider: Optional[AIProvider] = None) -> ImageGenerationService:
        """Get image generation service"""
        return self._get_service(AIServiceType.IMAGE_GENERATION, ImageGenerationService, provider)
    
    def _get_service(self, 
                    service_type: AIServiceType, 
                    service_class: Type[T], 
                    provider: Optional[AIProvider] = None) -> T:
        """Get or create a service instance"""
        
        # Build cache key
        cache_key = f"{service_type.value}_{provider.value if provider else 'default'}"
        
        # Check cache
        if cache_key in self._services:
            return self._services[cache_key]
        
        # Get configuration
        config = self.config.get_service_config(service_type, provider)
        
        # Create service
        service = AIServiceFactory.create(service_type, config)
        
        # Cache and return
        self._services[cache_key] = service
        return service
    
    def set_fallback_chain(self, 
                          service_type: AIServiceType, 
                          providers: List[AIProvider]):
        """Set fallback provider chain for resilience"""
        self._fallback_chains[service_type] = providers
    
    async def execute_with_fallback(self, 
                                   service_type: AIServiceType, 
                                   operation: str, 
                                   *args, 
                                   **kwargs):
        """Execute operation with automatic fallback"""
        
        providers = self._fallback_chains.get(service_type, [])
        if not providers:
            # Use default provider only
            service = self._get_service(service_type, AIService)
            method = getattr(service, operation)
            return await method(*args, **kwargs)
        
        # Try each provider in order
        last_error = None
        for provider in providers:
            try:
                service = self._get_service(service_type, AIService, provider)
                method = getattr(service, operation)
                return await method(*args, **kwargs)
            except Exception as e:
                last_error = e
                continue
        
        # All providers failed
        raise RuntimeError(f"All providers failed for {operation}: {last_error}")
```

### 6. Migration Strategy

#### 6.1 Phase 1: Create Abstraction Layer (Week 1-2)
1. Implement all interfaces
2. Create Gemini implementations (current provider)
3. Set up factory and configuration
4. Write comprehensive tests

#### 6.2 Phase 2: Gradual Migration (Week 3-4)
1. Identify all AI service calls in codebase
2. Create migration checklist
3. Start with low-risk components:
   - Hashtag generator
   - Script processor
   - Voice director
4. Replace direct calls with service manager

#### 6.3 Phase 3: High-Risk Components (Week 5-6)
1. Video generator (VEO calls)
2. Multi-agent discussions
3. Working orchestrator
4. Mission planning agent

#### 6.4 Phase 4: Add Alternative Providers (Week 7-8)
1. Implement OpenAI provider
2. Implement Anthropic provider
3. Add ElevenLabs for TTS
4. Add Stability AI for images

### 7. Usage Examples

#### 7.1 Before (Current Code)
```python
# Scattered throughout codebase
import google.generativeai as genai

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content(prompt)
```

#### 7.2 After (With Abstraction)
```python
# In any service that needs AI
from src.ai.manager import AIServiceManager
from src.ai.interfaces.text_generation import TextGenerationRequest

class MyService:
    def __init__(self, ai_manager: AIServiceManager):
        self.ai_manager = ai_manager
    
    async def process(self):
        # Get text service (uses configured default provider)
        text_service = self.ai_manager.get_text_service()
        
        # Generate text
        request = TextGenerationRequest(
            prompt="Generate a video script",
            max_tokens=500,
            temperature=0.8
        )
        response = await text_service.generate(request)
        
        # Use response
        script = response.text
        cost = response.cost_estimate
```

### 8. Configuration Example

```json
{
  "default_providers": {
    "text_generation": "gemini",
    "video_generation": "gemini",
    "audio_generation": "gemini",
    "image_generation": "openai"
  },
  "api_keys": {
    "gemini": "${GEMINI_API_KEY}",
    "openai": "${OPENAI_API_KEY}",
    "anthropic": "${ANTHROPIC_API_KEY}"
  },
  "service_configs": {
    "text_generation_gemini": {
      "provider": "gemini",
      "model_name": "gemini-1.5-flash",
      "max_retries": 3,
      "timeout": 30
    },
    "text_generation_openai": {
      "provider": "openai",
      "model_name": "gpt-4-turbo",
      "max_retries": 2,
      "timeout": 60
    }
  },
  "fallback_chains": {
    "text_generation": ["gemini", "openai", "anthropic"],
    "video_generation": ["gemini"],
    "audio_generation": ["gemini", "elevenlabs"]
  }
}
```

### 9. Testing Strategy

#### 9.1 Unit Tests
```python
# tests/ai/test_text_generation.py
import pytest
from unittest.mock import Mock, AsyncMock
from src.ai.interfaces.text_generation import TextGenerationRequest, TextGenerationResponse
from src.ai.providers.gemini.text_generation import GeminiTextService

class TestTextGeneration:
    @pytest.mark.asyncio
    async def test_gemini_generation(self, mock_genai):
        # Mock the Gemini API
        mock_genai.GenerativeModel.return_value.generate_content_async = AsyncMock(
            return_value=Mock(
                text="Generated text",
                usage_metadata=Mock(
                    prompt_token_count=10,
                    candidates_token_count=20,
                    total_token_count=30
                )
            )
        )
        
        # Create service
        config = AIServiceConfig(
            provider=AIProvider.GEMINI,
            api_key="test-key",
            model_name="gemini-1.5-flash"
        )
        service = GeminiTextService(config)
        
        # Test generation
        request = TextGenerationRequest(prompt="Test prompt")
        response = await service.generate(request)
        
        assert response.text == "Generated text"
        assert response.provider == "gemini"
        assert response.usage["total_tokens"] == 30
```

#### 9.2 Integration Tests
```python
# tests/ai/test_integration.py
class TestAIServiceIntegration:
    @pytest.mark.asyncio
    async def test_fallback_mechanism(self, ai_manager):
        # Configure fallback chain
        ai_manager.set_fallback_chain(
            AIServiceType.TEXT_GENERATION,
            [AIProvider.GEMINI, AIProvider.OPENAI]
        )
        
        # Mock Gemini to fail
        with patch('gemini.generate_content_async', side_effect=Exception("API Error")):
            # Should fallback to OpenAI
            response = await ai_manager.execute_with_fallback(
                AIServiceType.TEXT_GENERATION,
                'generate',
                TextGenerationRequest(prompt="Test")
            )
            
            assert response.provider == "openai"
```

### 10. Monitoring & Observability

```python
# src/ai/monitoring.py
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
import json

@dataclass
class AIServiceMetrics:
    """Metrics for AI service usage"""
    timestamp: datetime
    service_type: str
    provider: str
    operation: str
    duration_ms: float
    success: bool
    error: Optional[str] = None
    tokens_used: Optional[int] = None
    cost_estimate: Optional[float] = None

class AIServiceMonitor:
    """Monitor AI service usage and performance"""
    
    def __init__(self):
        self.metrics: List[AIServiceMetrics] = []
    
    def record(self, metric: AIServiceMetrics):
        """Record a metric"""
        self.metrics.append(metric)
        
        # Log to file for analysis
        with open('ai_metrics.jsonl', 'a') as f:
            f.write(json.dumps({
                'timestamp': metric.timestamp.isoformat(),
                'service_type': metric.service_type,
                'provider': metric.provider,
                'operation': metric.operation,
                'duration_ms': metric.duration_ms,
                'success': metric.success,
                'error': metric.error,
                'tokens_used': metric.tokens_used,
                'cost_estimate': metric.cost_estimate
            }) + '\n')
    
    def get_cost_summary(self, 
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> Dict[str, float]:
        """Get cost summary by provider"""
        costs = {}
        for metric in self.metrics:
            if start_date and metric.timestamp < start_date:
                continue
            if end_date and metric.timestamp > end_date:
                continue
            if metric.cost_estimate:
                provider = metric.provider
                costs[provider] = costs.get(provider, 0) + metric.cost_estimate
        return costs
```

### 11. Benefits

1. **Provider Flexibility**: Switch providers with configuration change
2. **Cost Optimization**: Easy A/B testing of providers for cost/quality
3. **Resilience**: Automatic fallback when providers fail
4. **Testing**: Mock AI services for fast, deterministic tests
5. **Monitoring**: Centralized usage tracking and cost management
6. **Type Safety**: Clear contracts with type hints
7. **Future Proof**: Easy to add new providers or service types

### 12. Potential Challenges

1. **Initial Development Time**: Significant upfront investment
2. **Learning Curve**: Team needs to understand new abstractions
3. **Performance**: Additional layer might add minimal latency
4. **Complexity**: More code to maintain
5. **Provider Differences**: Some features might not map 1:1

### 13. Success Metrics

1. **Code Reduction**: Less duplicated AI calling code
2. **Provider Switching**: Time to add new provider < 1 day
3. **Test Coverage**: 90%+ coverage of AI interactions
4. **Cost Visibility**: Real-time cost tracking dashboard
5. **Reliability**: 99.9% uptime with fallbacks

## Conclusion

This abstraction layer will transform ViralAI from a tightly coupled system to a flexible, provider-agnostic platform. The investment in proper abstractions will pay dividends in maintainability, testability, and adaptability to the rapidly evolving AI landscape.