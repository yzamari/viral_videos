# Universal AI Provider Interface Implementation Plan

## Executive Summary

This document outlines a comprehensive plan to refactor the ViralAI system to support pluggable AI providers through a universal interface architecture. The plan includes integration with ComfyUI for local generation capabilities and ensures easy replacement of any AI component.

**UPDATE (January 2025)**: The codebase has already implemented Phase 1 of the AI service abstraction layer with a factory pattern, service manager, and text generation interface. This plan has been updated to build upon the existing foundation rather than recreating it.

## Current Status (Updated January 2025)

### ✅ Already Implemented
- **Base AI Interface Structure** (`/src/ai/interfaces/base.py`)
  - `AIProvider` enum (GEMINI, OPENAI, ANTHROPIC, COHERE, LOCAL)
  - `AIServiceConfig` dataclass
  - Abstract `AIService` base class
- **Text Generation Interface** (`/src/ai/interfaces/text_generation.py`)
  - `TextGenerationService` with proper request/response models
  - Implemented by `GeminiTextService`
- **Core Service Interfaces** (`/src/core/interfaces/services.py`)
  - `VideoGenerationService` - Abstract interface for video generation
  - `ScriptGenerationService` - Abstract interface for script generation
  - `AudioGenerationService` - Abstract interface for audio generation
- **Factory Pattern** (`/src/ai/factory.py`)
  - Service registry with support for VIDEO_GENERATION, AUDIO_GENERATION, IMAGE_GENERATION
  - Dynamic provider registration
- **Service Manager** (`/src/ai/manager.py`)
  - Dependency injection
  - Fallback chain support
- **Base VEO Client** (`/src/generators/base_veo_client.py`)
  - Abstract base class for VEO providers
  - Implemented by `VertexAIVeo2Client` and `VertexAIVeo3Client`
- **AI Voice Provider Interface** (`/src/generators/ai_voice_generator.py`)
  - `AIVoiceProvider` abstract base class
  - Implemented by `ElevenLabsProvider`, `OpenAIVoiceProvider`

### ❌ Missing Interfaces
- **Image Generation Interface**
  - No dedicated interface in `/src/ai/interfaces/`
  - Direct usage of `GeminiImageClient` and `VertexImagenClient`
- **Speech Synthesis Interface**
  - `GoogleTTSClient` used directly without interface
  - Should unify all TTS providers

### 🚨 Components Not Using Interfaces
- **VideoGenerator** (`/src/generators/video_generator.py`)
  - Creates clients directly instead of using service interfaces
- **CharacterReferenceManager** (`/src/utils/character_reference_manager.py`)
  - Direct `VertexImagenClient` instantiation
- **WorkingOrchestrator** (`/src/agents/working_orchestrator.py`)
  - Calls generators directly without service abstraction

## Goals

1. **Interface Everywhere**: ALL AI operations MUST go through interfaces - no direct client usage
2. **Provider Agnostic**: Any AI provider (OpenAI, Google, Anthropic, local models) can be plugged in
3. **Easy Replacement**: Swap providers through configuration without code changes
4. **ComfyUI Integration**: Support local generation through ComfyUI workflows
5. **Unified Interface**: Single interface pattern for all AI operations (video, audio, image, text)
6. **Backward Compatible**: Existing functionality remains intact during migration
7. **Leverage Existing**: Build upon the current AI interface foundation
8. **Complete Coverage**: Video, Audio, Image, and Text generation all use interfaces

## Architecture Overview

### Core Principles

1. **Interface Segregation**: Separate interfaces for different AI capabilities
2. **Dependency Injection**: Providers injected at runtime based on configuration
3. **Factory Pattern**: Centralized provider creation and management
4. **Strategy Pattern**: Different providers implement same interface differently
5. **Health Monitoring**: Automatic failover between providers

### Layer Architecture

```
┌─────────────────────────────────────────────────┐
│           Application Layer (CLI/API)            │
├─────────────────────────────────────────────────┤
│         Decision Framework Layer                 │
│    (CoreDecisions, SessionContext)              │
├─────────────────────────────────────────────────┤
│      AI Service Management Layer                 │
│   (AIServiceManager, AIServiceFactory)          │ 
├─────────────────────────────────────────────────┤
│         Interface Layer (ABC)                    │
│   (AIService + Video/Image/Audio/LLM)           │
├─────────────────────────────────────────────────┤
│        Implementation Layer                      │
│ (Existing: VEO, Gemini, Vertex, Google TTS)     │
│ (New: ComfyUI, OpenAI, Anthropic, Local)        │
└─────────────────────────────────────────────────┘
```

### Existing Architecture Integration

The system already has:
1. **VEO Client Factory** (`/src/generators/veo_client_factory.py`) - Factory pattern for video generation
2. **Base VEO Client** (`/src/generators/base_veo_client.py`) - Abstract base for VEO providers
3. **Decision Framework** (`/src/core/decision_framework.py`) - Centralized decision making
4. **Session Management** (`/src/utils/session_context.py`) - Operation tracking
5. **AI Service Foundation** (`/src/ai/`) - Phase 1 implementation

## Week-by-Week Implementation Plan

### Phase 1: Complete Interface Implementation (Week 1)

#### Priority 1: Create Missing Interfaces
- **Day 1**: Create image generation interface
  ```python
  # src/ai/interfaces/image_generation.py
  from src.ai.interfaces.base import AIService
  
  @dataclass
  class ImageGenerationRequest:
      prompt: str
      style: Optional[str] = None
      aspect_ratio: Optional[str] = "1:1"
      negative_prompt: Optional[str] = None
      num_images: int = 1
  
  class ImageGenerationService(AIService):
      @abstractmethod
      async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse
      @abstractmethod
      async def generate_batch(self, requests: List[ImageGenerationRequest]) -> List[ImageGenerationResponse]
  ```

- **Day 2**: Create speech synthesis interface
  ```python
  # src/ai/interfaces/speech_synthesis.py
  class SpeechSynthesisService(AIService):
      @abstractmethod
      async def synthesize(self, request: SpeechRequest) -> SpeechResponse
      @abstractmethod
      async def get_voices(self) -> List[Voice]
      @abstractmethod
      async def synthesize_multilingual(self, request: MultilingualSpeechRequest) -> SpeechResponse
  ```

- **Day 3**: Align video interface with existing core interface
  ```python
  # src/ai/interfaces/video_generation.py
  # Should extend/wrap existing VideoGenerationService from core/interfaces/services.py
  class AIVideoGenerationService(AIService):
      @abstractmethod
      async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse
      @abstractmethod
      async def check_status(self, job_id: str) -> JobStatus
  ```

- **Day 4-5**: Update all components to use interfaces
  - Refactor VideoGenerator to accept service interfaces
  - Update CharacterReferenceManager to use image service
  - Modify WorkingOrchestrator to use service manager

### Phase 2: Adapt Existing Implementations (Week 2)

#### Create Service Adapters for All Providers
- **Day 1**: Image service adapters
  ```python
  # src/ai/providers/gemini_image_generation.py
  class GeminiImageService(ImageGenerationService):
      def __init__(self, config: AIServiceConfig):
          super().__init__(config)
          self.client = GeminiImageClient()  # Wrap existing client
      
      async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
          # Adapt existing client to new interface
          result = await self.client.generate_image(
              prompt=request.prompt,
              style=request.style
          )
          return ImageGenerationResponse(...)
  
  # src/ai/providers/vertex_image_generation.py
  class VertexImagenService(ImageGenerationService):
      # Similar adapter for VertexImagenClient
  ```

- **Day 2**: Video service adapters
  ```python
  # src/ai/providers/veo_video_generation.py
  class VEOVideoService(AIVideoGenerationService):
      def __init__(self, config: AIServiceConfig):
          super().__init__(config)
          self.veo_factory = VeoClientFactory()
  ```

- **Day 3**: Audio/TTS service adapters
  ```python
  # src/ai/providers/google_tts_service.py
  class GoogleTTSService(SpeechSynthesisService):
      def __init__(self, config: AIServiceConfig):
          super().__init__(config)
          self.client = GoogleTTSClient()
  
  # src/ai/providers/elevenlabs_service.py
  class ElevenLabsService(SpeechSynthesisService):
      # Adapter for ElevenLabs
  ```

- **Day 4-5**: Register all adapters with factory
  ```python
  # src/ai/providers/__init__.py
  factory = AIServiceFactory.get_instance()
  
  # Register image providers
  factory.register(AIServiceType.IMAGE_GENERATION, AIProvider.GEMINI, GeminiImageService)
  factory.register(AIServiceType.IMAGE_GENERATION, AIProvider.VERTEX, VertexImagenService)
  
  # Register video providers
  factory.register(AIServiceType.VIDEO_GENERATION, AIProvider.GEMINI, VEOVideoService)
  
  # Register speech providers
  factory.register(AIServiceType.SPEECH_SYNTHESIS, AIProvider.GOOGLE, GoogleTTSService)
  factory.register(AIServiceType.SPEECH_SYNTHESIS, AIProvider.ELEVENLABS, ElevenLabsService)
  ```

### Phase 3: Refactor Components to Use Interfaces (Week 3)

#### Replace Direct Client Usage
- **Day 1**: Update VideoGenerator
  ```python
  # src/generators/video_generator.py
  class VideoGenerator:
      def __init__(self, 
                   image_service: ImageGenerationService,
                   video_service: VideoGenerationService,
                   session_context: SessionContext):
          self.image_service = image_service
          self.video_service = video_service
          # Remove direct client instantiation
  ```

- **Day 2**: Update CharacterReferenceManager
  ```python
  # src/utils/character_reference_manager.py
  class CharacterReferenceManager:
      def __init__(self, image_service: ImageGenerationService):
          self.image_service = image_service
          # Replace direct VertexImagenClient usage
  ```

- **Day 3**: Update WorkingOrchestrator
  ```python
  # src/agents/working_orchestrator.py
  class WorkingOrchestrator:
      def __init__(self, service_manager: AIServiceManager):
          self.service_manager = service_manager
          # Use service manager for all AI operations
  ```

- **Day 4-5**: Update all other components
  - BaseVEOClient image fallback
  - Any remaining direct client usage
  - Test all refactored components

### Phase 4: ComfyUI Integration (Weeks 4-5)

#### Week 3: ComfyUI Integration Foundation
- **Day 1-2**: Design ComfyUI workflow interface
  ```python
  # src/providers/comfyui/workflow.py
  class ComfyUIWorkflow:
      def load_workflow(self, path: str)
      def set_parameters(self, params: Dict)
      def execute(self) -> WorkflowResult
  ```

- **Day 3-4**: Implement ComfyUI client
  ```python
  # src/providers/comfyui/client.py
  class ComfyUIClient:
      async def connect(self, url: str)
      async def queue_prompt(self, workflow: Dict)
      async def get_result(self, prompt_id: str)
  ```

- **Day 5**: Create workflow templates for video/image/audio

#### Week 4: ComfyUI Provider Implementation
- **Day 1-2**: Implement ComfyUI video provider
  ```python
  # src/ai/providers/comfyui_video_generation.py
  class ComfyUIVideoGenerationService(VideoGenerationService):
      def __init__(self, config: AIServiceConfig, workflow_path: str):
          super().__init__(config)
          self.client = ComfyUIClient(config.custom_config.get('endpoint'))
          self.workflow_path = workflow_path
  ```

- **Day 3-4**: Implement ComfyUI image/audio providers
- **Day 5**: Test ComfyUI integration with existing system

### Phase 3: Provider Implementations (Weeks 5-7)

#### Week 5: Additional Provider Implementations
- **Day 1-2**: Add OpenAI providers (GPT-4, DALL-E 3, TTS)
- **Day 3-4**: Add Anthropic Claude provider
- **Day 5**: Add Runway/Stability AI providers

#### Week 6: Local Model Support
- **Day 1-2**: Implement Ollama provider for local LLMs
- **Day 3-4**: Add LMStudio support
- **Day 5**: Create local model management system

#### Week 7: Health Monitoring & Fallback
- **Day 1-2**: Implement provider health monitoring
  ```python
  # src/ai/health_monitor.py
  class AIHealthMonitor:
      async def check_provider_health(self, service: AIService) -> bool
      async def get_healthy_provider(self, service_type: AIServiceType) -> AIService
  ```
- **Day 3-4**: Enhance fallback chain with health checks
- **Day 5**: Add provider metrics and monitoring

### Phase 4: AI Agent System Integration (Weeks 8-9)

#### Week 8: Agent System Refactoring
- **Day 1-2**: Update MultiAgentDiscussion to use AIServiceManager
  ```python
  # src/ai_agents/multi_agent_discussion.py
  class MultiAgentDiscussion:
      def __init__(self, service_manager: AIServiceManager):
          self.llm_service = service_manager.get_service(AIServiceType.TEXT_GENERATION)
  ```
- **Day 3-4**: Update all 22 agents to support provider switching
- **Day 5**: Test agent system with multiple providers

#### Week 9: Session & Decision Integration
- **Day 1-2**: Integrate provider decisions into SessionContext
- **Day 3-4**: Add provider usage tracking to session metadata
- **Day 5**: Update DecisionFramework to include provider selection logic

### Phase 5: Integration & Migration (Weeks 10-11)

#### Week 10: System Integration
- **Day 1-2**: Update WorkingOrchestrator to use AIServiceManager
- **Day 3-4**: Integrate with existing VeoClientFactory pattern
- **Day 5**: Update VideoGenerator to use new interfaces

#### Week 11: Configuration & Management
- **Day 1-2**: Extend AIConfiguration for all providers
  ```python
  # src/ai/config.py updates
  ai_config:
    providers:
      video:
        default: "veo"
        fallback: ["comfyui", "runway"]
      image:
        default: "gemini"
        fallback: ["vertex", "comfyui"]
  ```
- **Day 3-4**: Create provider switching CLI commands
- **Day 5**: Build compatibility layer for gradual migration

### Phase 6: Testing & Documentation (Weeks 12-13)

#### Week 12: Testing Framework
- **Day 1-2**: Create provider testing framework
  ```python
  # tests/ai/test_providers.py
  class AIProviderTestCase:
      async def test_interface_compliance(self, service: AIService)
      async def test_error_handling(self, service: AIService)
      async def test_performance(self, service: AIService)
  ```
- **Day 3-4**: Write tests for all providers
- **Day 5**: Integration tests with existing workflows

#### Week 13: Documentation & Release
- **Day 1-2**: Update documentation for new provider system
- **Day 3-4**: Create provider development guide
- **Day 5**: Performance benchmarking and optimization

## Implementation Details

### 1. Interface Definitions for ALL Services

```python
# src/ai/interfaces/image_generation.py
from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from src.ai.interfaces.base import AIService, AIServiceConfig

@dataclass
class ImageGenerationRequest:
    prompt: str
    style: Optional[str] = None
    aspect_ratio: str = "1:1"
    negative_prompt: Optional[str] = None
    num_images: int = 1
    width: Optional[int] = None
    height: Optional[int] = None
    session_context: Optional[Any] = None

@dataclass
class ImageGenerationResponse:
    image_paths: List[str]
    metadata: Dict[str, Any]
    provider_used: str
    generation_time: float

class ImageGenerationService(AIService):
    @abstractmethod
    async def generate_image(self, request: ImageGenerationRequest) -> ImageGenerationResponse:
        """Generate image from prompt"""
        pass
    
    @abstractmethod
    async def generate_batch(self, requests: List[ImageGenerationRequest]) -> List[ImageGenerationResponse]:
        """Generate multiple images in batch"""
        pass
```

```python
# src/ai/interfaces/speech_synthesis.py
@dataclass
class SpeechSynthesisRequest:
    text: str
    voice_id: Optional[str] = None
    language: str = "en"
    speed: float = 1.0
    pitch: float = 0.0
    session_context: Optional[Any] = None

@dataclass
class SpeechSynthesisResponse:
    audio_path: str
    duration: float
    metadata: Dict[str, Any]
    provider_used: str

class SpeechSynthesisService(AIService):
    @abstractmethod
    async def synthesize(self, request: SpeechSynthesisRequest) -> SpeechSynthesisResponse:
        """Synthesize speech from text"""
        pass
    
    @abstractmethod
    async def get_voices(self) -> List[Voice]:
        """Get available voices"""
        pass
```

### 2. Adapter Pattern for Existing Clients

```python
# src/ai/providers/veo_video_generation.py
from src.ai.interfaces.video_generation import VideoGenerationService, VideoGenerationRequest, VideoGenerationResponse
from src.generators.veo_client_factory import VeoClientFactory
from src.ai.interfaces.base import AIProvider

class VEOVideoGenerationService(VideoGenerationService):
    def __init__(self, config: AIServiceConfig):
        super().__init__(config)
        self.veo_factory = VeoClientFactory()
        self.cheap_mode = config.custom_config.get('cheap_mode', False)
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        # Get appropriate VEO client
        client = self.veo_factory.get_client(
            prefer_veo2=self.config.custom_config.get('prefer_veo2', False)
        )
        
        # Adapt request to existing VEO interface
        result = await client.generate_video_from_prompt(
            prompt=request.prompt,
            duration=request.duration,
            aspect_ratio=request.aspect_ratio
        )
        
        return VideoGenerationResponse(
            video_path=result['video_path'],
            metadata=result,
            provider_used=f"veo_{client.model_version}",
            generation_time=result.get('generation_time', 0)
        )
```

### 3. ComfyUI Integration Architecture

```python
# src/ai/providers/comfyui_video_generation.py
class ComfyUIVideoGenerationService(VideoGenerationService):
    def __init__(self, config: AIServiceConfig):
        super().__init__(config)
        self.endpoint = config.custom_config.get('endpoint', 'http://localhost:8188')
        self.workflow_path = config.custom_config.get('workflow_path')
        self.client = ComfyUIClient(self.endpoint)
    
    async def generate_video(self, request: VideoGenerationRequest) -> VideoGenerationResponse:
        # Load and configure workflow
        workflow = self.load_workflow(self.workflow_path)
        workflow = self.inject_parameters(workflow, {
            'prompt': request.prompt,
            'duration': request.duration,
            'fps': video_config.get_fps(request.platform or 'youtube'),
            'width': video_config.get_dimensions(request.platform or 'youtube')[0],
            'height': video_config.get_dimensions(request.platform or 'youtube')[1]
        })
        
        # Execute workflow
        result = await self.client.queue_prompt(workflow)
        output = await self.wait_for_result(result.prompt_id)
        
        return VideoGenerationResponse(
            video_path=output['video_path'],
            metadata=output,
            provider_used='comfyui',
            generation_time=output.get('execution_time', 0)
        )
```

### 4. Integration with Decision Framework

```python
# Update src/core/decision_framework.py
@dataclass
class CoreDecisions:
    # ... existing fields ...
    
    # Provider decisions
    video_provider: str = "veo"
    image_provider: str = "gemini"
    audio_provider: str = "google_tts"
    llm_provider: str = "gemini"
    
    # Provider fallback chains
    video_fallback_chain: List[str] = field(default_factory=lambda: ["veo", "comfyui"])
    image_fallback_chain: List[str] = field(default_factory=lambda: ["gemini", "vertex", "comfyui"])
    
    def get_provider_config(self, service_type: str) -> Dict[str, Any]:
        """Get provider configuration for a service type"""
        return {
            'primary': getattr(self, f"{service_type}_provider"),
            'fallback': getattr(self, f"{service_type}_fallback_chain", [])
        }
```

### 5. Session Integration

```python
# Update src/utils/session_context.py
class SessionContext:
    # ... existing code ...
    
    def track_provider_usage(self, service_type: str, provider: str, success: bool, duration: float):
        """Track provider usage in session"""
        if 'provider_usage' not in self.metadata:
            self.metadata['provider_usage'] = {}
        
        key = f"{service_type}_{provider}"
        if key not in self.metadata['provider_usage']:
            self.metadata['provider_usage'][key] = {
                'attempts': 0,
                'successes': 0,
                'total_duration': 0
            }
        
        usage = self.metadata['provider_usage'][key]
        usage['attempts'] += 1
        if success:
            usage['successes'] += 1
        usage['total_duration'] += duration
        
        self.save_metadata()
```

## Testing Strategy

### 1. Unit Tests
- Test each provider interface implementation
- Mock external API calls
- Verify error handling and retries

### 2. Integration Tests
- Test provider switching
- Verify fallback mechanisms
- Test ComfyUI workflow execution

### 3. Performance Tests
- Benchmark provider response times
- Test concurrent request handling
- Measure resource usage

### 4. Compatibility Tests
- Ensure backward compatibility
- Test migration scripts
- Verify existing functionality

## Mandatory Interface Usage Examples

### ❌ FORBIDDEN - Direct Client Usage
```python
# NEVER DO THIS - Direct client instantiation
from src.generators.gemini_image_client import GeminiImageClient
from src.generators.google_tts_client import GoogleTTSClient

class VideoGenerator:
    def __init__(self):
        self.image_client = GeminiImageClient()  # ❌ FORBIDDEN
        self.tts_client = GoogleTTSClient()      # ❌ FORBIDDEN
```

### ✅ REQUIRED - Interface Usage
```python
# ALWAYS DO THIS - Use service interfaces
from src.ai.manager import AIServiceManager
from src.ai.interfaces.base import AIServiceType

class VideoGenerator:
    def __init__(self, service_manager: AIServiceManager):
        self.service_manager = service_manager
        self.image_service = service_manager.get_service(AIServiceType.IMAGE_GENERATION)
        self.audio_service = service_manager.get_service(AIServiceType.SPEECH_SYNTHESIS)
        self.video_service = service_manager.get_service(AIServiceType.VIDEO_GENERATION)
    
    async def generate_thumbnail(self, prompt: str):
        request = ImageGenerationRequest(prompt=prompt, aspect_ratio="16:9")
        response = await self.image_service.generate_image(request)
        return response.image_paths[0]
```

### Configuration for Interface-Based System
```yaml
# config/ai_config.yaml
ai_services:
  image_generation:
    default_provider: GEMINI
    fallback_chain:
      - GEMINI
      - VERTEX
      - LOCAL
    provider_configs:
      GEMINI:
        model: "imagen-3"
        quality: "high"
      VERTEX:
        project_id: ${GCP_PROJECT_ID}
        location: "us-central1"
      LOCAL:
        endpoint: "http://localhost:8188"
        workflow: "workflows/sdxl_image.json"
  
  speech_synthesis:
    default_provider: GOOGLE
    fallback_chain:
      - GOOGLE
      - ELEVENLABS
    provider_configs:
      GOOGLE:
        voice: "en-US-Neural2-J"
        speed: 1.0
      ELEVENLABS:
        api_key: ${ELEVENLABS_API_KEY}
        voice_id: "default"
  
  video_generation:
    default_provider: GEMINI  # VEO
    fallback_chain:
      - GEMINI  # VEO-3
      - LOCAL   # ComfyUI
    provider_configs:
      GEMINI:
        prefer_veo2: false
        disable_veo3: false
      LOCAL:
        endpoint: "http://localhost:8188"
        workflow: "workflows/animatediff_video.json"
```

### ComfyUI Workflow Example
```json
{
  "workflow": {
    "name": "video_generation",
    "nodes": {
      "text_encoder": {
        "type": "CLIPTextEncode",
        "inputs": {
          "text": "${prompt}",
          "clip": ["clip_loader", 0]
        }
      },
      "video_model": {
        "type": "AnimateDiff",
        "inputs": {
          "positive": ["text_encoder", 0],
          "model": ["model_loader", 0],
          "frames": "${frames}",
          "fps": "${fps}"
        }
      },
      "video_output": {
        "type": "VideoOutput",
        "inputs": {
          "video": ["video_model", 0],
          "filename_prefix": "viralai_"
        }
      }
    }
  }
}
```

## Migration Guide

### Step 1: Update Existing Code
```python
# Before
from src.generators.veo_client_factory import VeoClientFactory
veo_factory = VeoClientFactory()
client = veo_factory.get_client()
video = client.generate_video_from_prompt(prompt)

# After
from src.ai.manager import AIServiceManager
from src.ai.interfaces.video_generation import VideoGenerationRequest

service_manager = AIServiceManager()
video_service = service_manager.get_service(AIServiceType.VIDEO_GENERATION)
request = VideoGenerationRequest(prompt=prompt, duration=duration)
response = await video_service.generate_video(request)
video = response.video_path
```

### Step 2: Register Providers
```python
# src/ai/providers/__init__.py
from src.ai.factory import AIServiceFactory
from src.ai.providers.veo_video_generation import VEOVideoGenerationService
from src.ai.providers.comfyui_video_generation import ComfyUIVideoGenerationService

# Register providers
factory = AIServiceFactory.get_instance()
factory.register(AIServiceType.VIDEO_GENERATION, AIProvider.GEMINI, VEOVideoGenerationService)
factory.register(AIServiceType.VIDEO_GENERATION, AIProvider.LOCAL, ComfyUIVideoGenerationService)
```

### Step 3: Update Configuration
```yaml
# config/ai_config.yaml
ai_services:
  video_generation:
    default_provider: GEMINI  # Uses VEO
    fallback_chain:
      - GEMINI  # VEO
      - LOCAL   # ComfyUI
    provider_configs:
      GEMINI:
        prefer_veo2: false
        disable_veo3: false
      LOCAL:
        endpoint: "http://localhost:8188"
        workflow_path: "workflows/video_generation.json"
```

### Step 4: Test Migration
```bash
# Run AI provider tests
pytest tests/ai/

# Test provider switching
python -m src.tools.test_ai_providers

# Benchmark providers
python -m src.tools.benchmark_ai_providers --service=video_generation
```

## Benefits

1. **Flexibility**: Easily switch between cloud and local providers
2. **Cost Optimization**: Use cheaper providers when possible
3. **Reliability**: Automatic fallback on provider failures
4. **Performance**: Choose providers based on speed requirements
5. **Privacy**: Use local ComfyUI for sensitive content
6. **Experimentation**: A/B test different providers
7. **Future-Proof**: Easy to add new providers as they emerge

## Success Metrics

1. **Provider Switching Time**: < 100ms
2. **Fallback Success Rate**: > 95%
3. **Code Coverage**: > 90%
4. **Performance Overhead**: < 5%
5. **Migration Success**: 100% backward compatibility

## Risks and Mitigation

1. **Risk**: Breaking existing functionality
   - **Mitigation**: Comprehensive test suite and gradual migration

2. **Risk**: Performance degradation
   - **Mitigation**: Benchmark and optimize critical paths

3. **Risk**: Complex configuration
   - **Mitigation**: Sensible defaults and configuration validation

4. **Risk**: Provider API changes
   - **Mitigation**: Version pinning and adapter pattern

## Critical Requirements for Interface Implementation

### 1. No Direct Client Usage
- **FORBIDDEN**: `client = GeminiImageClient()` 
- **REQUIRED**: `service = service_manager.get_service(AIServiceType.IMAGE_GENERATION)`
- **Apply to ALL**: Video, Audio, Image, Text generation

### 2. Complete Interface Coverage
| Service Type | Interface | Current Implementations | Status |
|--------------|-----------|-------------------------|---------|
| Text Generation | `TextGenerationService` | Gemini | ✅ Implemented |
| Video Generation | `VideoGenerationService` + `AIVideoGenerationService` | VEO-2, VEO-3 | ⚠️ Partial |
| Image Generation | `ImageGenerationService` | Gemini, Vertex Imagen | ❌ Missing |
| Speech Synthesis | `SpeechSynthesisService` | Google TTS, ElevenLabs | ❌ Missing |

### 3. Refactoring Priority
1. **VideoGenerator** - Uses 3 different direct clients
2. **CharacterReferenceManager** - Direct Vertex Imagen usage
3. **BaseVEOClient** - Direct Gemini image fallback
4. **WorkingOrchestrator** - Must use service manager

### 4. Implementation Timeline
- **Week 1**: Create all missing interfaces
- **Week 2**: Implement adapters for all existing clients
- **Week 3**: Refactor all components to use interfaces
- **Week 4-5**: ComfyUI integration
- **Week 6-7**: Testing and migration

## Next Steps

1. **Immediate Actions**:
   - Create video/image/audio interfaces extending AIService
   - Implement VEO adapter using existing VeoClientFactory
   - Register adapters with AIServiceFactory

2. **Quick Wins**:
   - Provider switching through configuration
   - Session tracking of provider usage
   - Fallback chains for reliability

3. **Future Enhancements**:
   - ComfyUI integration for local generation
   - Health monitoring and auto-failover
   - A/B testing between providers

## Conclusion

This updated plan builds upon the solid foundation already implemented in the ViralAI codebase. By leveraging the existing AI service abstraction layer, factory pattern, and service manager, we can achieve provider agnosticism faster and with less disruption.

The integration with ComfyUI opens up possibilities for local generation, custom workflows, and reduced costs, while maintaining compatibility with the current architecture. The system will be prepared for the rapidly evolving AI landscape while preserving the centralized decision-making and session management that are core to ViralAI's design.