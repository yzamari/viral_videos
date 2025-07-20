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

## Architecture Guidelines

### Decision Making Flow
```
CLI Input → DecisionFramework.make_all_decisions() → CoreDecisions → All Components
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

## Implementation Guidelines

### Creating New Components
1. Accept `CoreDecisions` or `SessionContext` as parameters
2. Use decisions rather than making own choices
3. Track all operations in session
4. Follow logging patterns
5. Implement proper error handling

### Modifying Existing Components
1. Check if component uses centralized decisions
2. Remove any hardcoded defaults
3. Ensure session tracking is implemented
4. Update logging to match patterns
5. Test with all generation modes

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

### 🔄 In Progress
- Testing centralized decision flow
- Performance optimization
- Enhanced error handling

### 📋 Architecture Files
- `README.md` - User guide and quick start
- `SYSTEM_ARCHITECTURE.md` - Technical architecture
- `CURRENT_FLOW.md` - Detailed system flow
- `CLAUDE.md` - This file (system instructions)

## Important Notes

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

This system provides a robust, scalable, and maintainable architecture for AI-powered video generation with comprehensive social media integration.