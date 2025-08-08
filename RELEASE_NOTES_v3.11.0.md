# Release Notes - v3.11.0

## 🚀 New Features

### Professional Business Ads with Character References
- **Character Reference System**: Store and reuse professional photos for consistent character generation across videos
- **Business Information Overlays**: Automatic display of business contact information (name, phone, website, social media)
- **Enhanced & Professional Modes**: Support for both 7-agent (enhanced) and 19+ agent (professional) generation modes
- **Financial Advisor Ad Templates**: Optimized for creating engaging financial service advertisements

### AI Agent Enhancements
- **Neuroscientist Agent**: New specialized agent for brain engagement and dopamine optimization
- **LangGraph Orchestrator**: Advanced discussion orchestration system for better agent collaboration
- **Enhanced Multi-Agent Discussions**: Improved agent interaction patterns for all generation modes

### Visual & Content Improvements
- **Character Scene Generation**: Dynamic scene creation for stored characters with custom backgrounds
- **RTL Language Support**: Full Hebrew language support with proper right-to-left text handling
- **Professional Visual Styles**: Modern corporate themes with friendly, approachable tones

## 🛠️ Technical Improvements

### Agent System Architecture
- Introduced `langgraph_orchestrator.py` for advanced agent coordination
- Added `neuroscientist_agent.py` for cognitive psychology-based content optimization
- Enhanced `working_orchestrator.py` with LangGraph integration
- Improved `multi_agent_discussion.py` with neuroscientist role support

### Vertex AI Enhancements
- Updated `vertex_veo3_client.py` with improved error handling
- Better video generation stability and quality control
- Enhanced character reference processing

## 📊 Use Cases Demonstrated

### Matan Magen Financial Advisor Campaign
- Created professional Facebook/Instagram ads for financial services
- Demonstrated character reference storage and reuse
- Showcased both enhanced (7 agents) and professional (19+ agents) modes
- Included business information overlays and Hebrew language support

## 🔧 Configuration & Setup

### Character Storage
```bash
python3 main.py store-character /path/to/photo.jpg --name "Name" --description "Description"
```

### Ad Generation
```bash
python3 main.py generate \
  --mission "Your mission" \
  --character character_id \
  --scene "Scene description" \
  --mode enhanced/professional \
  --business-name "Business Name" \
  --business-phone "Phone" \
  --business-website "Website" \
  --languages he
```

## 🐛 Bug Fixes
- Fixed session context initialization issues
- Resolved LangGraph fallback handling
- Improved error handling in discussion systems
- Fixed RTL text processing for Hebrew content

## 📝 Documentation
- Added comprehensive agent mode breakdown documentation
- Updated command-line interface documentation
- Enhanced character reference system documentation

## 🎯 Impact
- Enables professional-quality business advertisements
- Supports multi-language international campaigns
- Provides consistent character representation across videos
- Delivers enterprise-grade content generation

## 🔮 Coming Next
- Extended character library management
- Advanced business template system
- Multi-character scene generation
- Enhanced analytics and performance tracking

---

**Version**: 3.11.0  
**Date**: August 8, 2025  
**Contributors**: Yahav Zamari, Claude

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>