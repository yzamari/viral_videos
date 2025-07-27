# ViralAI System Instructions

## Core Principles

### 1. Centralized Decision Framework
- ALL decisions must be made upfront via `DecisionFramework` before any generation
- No component should make its own decisions during generation
- Use `CoreDecisions` object to pass decisions to all components
- Always trace decision sources and reasoning

### 2. Session Management
- Every operation must be tracked in a session
- Use `SessionContext` for all file operations
- Maintain complete audit trail of all operations
- Save decisions, discussions, and artifacts to session directories

### 3. AI Agent System
- Use the 22-agent system for comprehensive discussions
- Professional mode: All 22 agents with 7 discussion topics
- Enhanced mode: 7 core agents with focused discussions
- Simple mode: Minimal AI for fast generation

### 4. Code Quality
- Always find the root cause for issues and make sure there are no linter errors
- Follow the centralized architecture patterns
- Use proper error handling and logging
- Maintain clean separation of concerns

### 5. Configuration System
- ALL hardcoded values must be moved to `src/config/video_config.py`
- Use configuration methods instead of hardcoding values
- Access configuration through the global `video_config` instance
- Platform-aware configuration is automatically applied
- Never hardcode: FPS, dimensions, font sizes, colors, text, durations

### 6. AI Provider System (NEW!)
- Use `AIServiceManager` to access AI services
- Never directly instantiate AI clients
- Always use the unified interface methods
- Handle provider-specific errors gracefully
- Support automatic fallback to alternative providers

## Architecture Guidelines

### Decision Making Flow
```
CLI Input → AI Provider Init → DecisionFramework.make_all_decisions() → CoreDecisions → All Components
```

### Component Responsibilities
- `DecisionFramework`: Makes all strategic decisions
- `WorkingOrchestrator`: Coordinates generation using decisions
- `MultiAgentDiscussion`: Handles AI agent collaboration
- `VideoGenerator`: Assembles final video using decisions
- `SessionManager`: Tracks all operations and files

### Key Classes
- `CoreDecisions`: Contains all system decisions
- `SessionContext`: Manages session files and directories
- `GeneratedVideoConfig`: Legacy config (being phased out)
- `VeoClientFactory`: Manages video generation models
- `VideoGenerationConfig`: Master configuration for all video parameters
- `VideoEncodingConfig`: Platform-specific encoding settings
- `TextOverlayConfig`: Text styling and appearance
- `AnimationTimingConfig`: Animation and transition timings
- `DefaultTextConfig`: Platform-specific default texts
- `LayoutConfig`: Positioning and layout parameters
- `AIServiceManager`: Central manager for all AI services (NEW!)
- `AIServiceFactory`: Factory for creating AI service instances (NEW!)
- `UniversalAIProviderInterface`: Unified interface for AI providers (NEW!)

## Development Rules

### 1. Always Use Sessions
- Create or use existing session for all operations
- Track all generated files in session
- Use session context for file paths
- Save comprehensive metadata

### 2. Duration Consistency
- Use centralized duration from `CoreDecisions`
- No hardcoded duration defaults in components
- Log duration at every critical point
- Ensure consistency across all generation stages

### 3. Error Handling
- Always find root cause of issues
- Use proper error recovery mechanisms
- Log errors with context
- Maintain session integrity on failures

### 4. Documentation
- Keep documentation current with implementation
- Document all architectural decisions
- Maintain clear flow diagrams
- Update README with new features

### 5. Configuration Usage
- Always use configuration system for parameters
- Never hardcode values that could be configured
- Use platform-aware methods like `get_fps()`, `get_font_size()`
- Test configuration changes with all platforms
- Document any new configuration parameters

## Implementation Guidelines

### Creating New Components
1. Accept `CoreDecisions` or `SessionContext` as parameters
2. Use decisions rather than making own choices
3. Track all operations in session
4. Follow logging patterns
5. Implement proper error handling
6. Use `video_config` for all configurable parameters
7. Never hardcode values - add to configuration instead
8. Use `AIServiceManager` for all AI operations
9. Implement provider-agnostic interfaces

### Modifying Existing Components
1. Check if component uses centralized decisions
2. Remove any hardcoded defaults - move to configuration
3. Ensure session tracking is implemented
4. Update logging to match patterns
5. Test with all generation modes
6. Replace hardcoded values with configuration lookups
7. Use platform-aware configuration methods

### Testing
1. Use `--cheap full` mode for development
2. Test with all generation modes (simple/enhanced/professional)
3. Verify session tracking works correctly
4. Check decision traceability
5. Ensure no duration conflicts

## Current System Status

### ✅ Implemented
- Centralized decision framework
- 22 AI agents system
- Professional mode discussions
- Session management
- Duration flow consistency
- VEO-2/VEO-3 generation
- Instagram auto-posting
- Comprehensive configuration system (NO hardcoded values)
- Platform-aware video encoding
- Dynamic text sizing and positioning
- AI model configuration (gemini-2.5-flash-lite default)
- Mission-based system (replaced all "topic" references)
- Character description extraction from missions
- Enhanced script processing without duplication
- Content and visual continuity flags
- Universal AI Provider Interface (NEW!)
- Multi-provider support: Gemini, Vertex AI, OpenAI, Anthropic (NEW!)
- Automatic provider fallback and error handling (NEW!)

### 🔄 In Progress
- Testing full Israeli PM series generation
- Performance optimization
- Enhanced error handling
- ElevenLabs speech synthesis integration
- Additional AI provider integrations

### 📋 Architecture Files
- `README.md` - User guide and quick start
- `SYSTEM_ARCHITECTURE.md` - Technical architecture
- `CURRENT_FLOW.md` - Detailed system flow
- `CLAUDE.md` - This file (system instructions)
- `docs/CONFIGURATION_GUIDE.md` - Complete configuration documentation
- `src/config/video_config.py` - Master configuration module

## Important Notes

### Series Creation
- Use consistent `--character` parameter for same face across episodes
- Use consistent `--voice` parameter for same narrator
- Use `--style-template` for visual consistency
- Use `--theme` for branding consistency
- Use meaningful `--session-id` for organization (e.g., "series_ep1", "series_ep2")
- See [Series Creation Guide](docs/SERIES_CREATION_GUIDE.md) for detailed instructions

### Fixed Issues (July 2025)
- **cheap_mode_level bug**: Fixed logic to only use cheap mode when explicitly enabled with `--cheap`
- **Audio-subtitle sync**: Fixed by excluding pause files from subtitle segment counting
- **Script duration**: Provide detailed narrative content, not just visual descriptions
- **VEO generation**: Remove `--cheap` flag to enable VEO video generation
- **Provider switching**: Implemented Universal AI Provider Interface for seamless provider changes
- **Configuration system**: Eliminated all hardcoded values throughout the codebase

### Duration Management
- Duration is decided once in `DecisionFramework`
- Flows to all components via `CoreDecisions`
- No component should have duration defaults
- Log duration at every generation stage

### Agent System
- 22 agents total (7 core + 15 professional)
- Professional mode uses all 22 agents
- Enhanced mode uses 7 core agents
- Simple mode uses minimal AI

### Session Organization
```
outputs/session_YYYYMMDD_HHMMSS/
├── decisions/           # All decisions made
├── discussions/         # AI agent discussions
├── scripts/            # Script versions
├── audio/              # Audio files
├── video_clips/        # Generated clips
├── final_output/       # Final video
├── hashtags/           # Generated hashtags
├── logs/               # Comprehensive logs
└── metadata/           # Session metadata
```

### Code Quality Standards
- Find root cause for all issues
- Ensure no linter errors
- Follow centralized patterns
- Maintain session integrity
- Use proper error handling
- Document architectural decisions
- NO HARDCODED VALUES - use configuration system
- Platform-aware code using configuration methods
- Test with both cheap mode and VEO generation
- Verify audio-subtitle sync with pause files

### Generation Segment Guidelines
- Audio segment, subtitles segment should be of one sentence

### Configuration Guidelines
- Import configuration: `from src.config.video_config import video_config`
- Get platform settings: `fps = video_config.get_fps(platform)`
- Calculate font sizes: `size = video_config.get_font_size('title', width)`
- Access default text: `hook = video_config.get_default_hook(platform)`
- Modify settings: `video_config.encoding.fps_by_platform['youtube'] = 60`
- Add new parameters to configuration instead of hardcoding

### Configuration Best Practices
1. **Never hardcode these values:**
   - Frame rates (use `get_fps()`)
   - Video dimensions (use `PlatformDimensions`)
   - Font sizes (use `get_font_size()`)
   - Colors (use configuration properties)
   - Default text (use `get_default_hook()`, `get_default_cta()`)
   - Timing values (use configuration properties)

2. **Always use platform-aware methods:**
   ```python
   # Good
   fps = video_config.get_fps(platform)
   
   # Bad
   fps = 30
   ```

3. **Add new parameters to configuration:**
   ```python
   # If you need a new parameter, add it to the appropriate config class
   # Don't hardcode it in the component
   ```

### AI Provider Best Practices
1. **Always use AIServiceManager:**
   ```python
   # Good
   manager = AIServiceManager()
   text_service = manager.get_service(AIServiceType.TEXT_GENERATION)
   
   # Bad
   client = GeminiTextClient()  # Don't instantiate directly
   ```

2. **Handle provider failures gracefully:**
   ```python
   try:
       response = await text_service.generate_text(request)
   except Exception as e:
       # Provider will automatically fallback
       logger.warning(f"Provider failed, using fallback: {e}")
   ```

3. **Use unified interfaces:**
   - Same request/response models for all providers
   - Provider-specific features via optional parameters
   - Consistent error handling across providers

## Generation Order
- The video generation order is: video generation -> image generation -> colored fallback (this is the fallbacks order)

This system provides a robust, scalable, and maintainable architecture for AI-powered video generation with comprehensive social media integration, ZERO hardcoded values, and seamless AI provider switching.