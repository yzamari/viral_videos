# 🤖 AI Agent Modes Breakdown

## Complete Agent List by Mode

### 🟢 **SIMPLE Mode** (3 Agents)
Perfect for quick tests and cheap generation

| Agent | Role | Responsibility |
|-------|------|----------------|
| 🎬 **Director** | Creative Vision | Visual storytelling, scene composition, creative direction |
| ✍️ **Script Writer** | Narrative | Script optimization, dialogue, pacing, narrative flow |
| 🎥 **Video Generator** | VEO Prompts | Prompt engineering for VEO, visual descriptions |

**Use Case**: Quick prototypes, testing, cheap mode generation

---

### 🔵 **ENHANCED Mode** (7 Agents) - DEFAULT
Balanced approach with core team + optimization

| Agent | Role | Responsibility |
|-------|------|----------------|
| 🎬 **Director** | Creative Vision | Visual storytelling, scene composition |
| ✍️ **Script Writer** | Narrative | Script optimization, dialogue, pacing |
| 🎥 **Video Generator** | VEO Prompts | Prompt engineering for VEO models |
| 🎵 **Soundman** | Audio Design | Voice selection, music, sound effects |
| ✂️ **Editor** | Post-Production | Timing, transitions, final polish |
| 🎯 **Orchestrator** | Coordination | Workflow management, agent synchronization |
| 🧠 **Neuroscientist** | Brain Engagement | Dopamine triggers, attention hooks, memory encoding |

**Use Case**: Most content creation, good balance of quality and speed

---

### 🟣 **ADVANCED Mode** (15 Agents)
Professional quality with specialized expertise

**Core Creative Team (7):**
- All Enhanced mode agents

**Additional Specialists (8):**

| Agent | Role | Responsibility |
|-------|------|----------------|
| 💹 **Engagement Optimizer** | Retention | Maximizing viewer retention and watch time |
| 🚀 **Viral Specialist** | Virality | Viral mechanics, shareability factors |
| 📊 **Trend Analyst** | Trends | Current trends, pattern recognition |
| 🎯 **Platform Specialist** | Platform Optimization | Platform-specific features and algorithms |
| 🎨 **Creative Strategist** | Creative Direction | Innovation, creative concepts |
| 🏢 **Brand Strategist** | Brand Alignment | Brand consistency, messaging |
| 📝 **Content Strategist** | Content Planning | Content structure, series planning |
| 📣 **Marketing Specialist** | Marketing | Promotion strategy, audience targeting |

**Use Case**: High-value content, brand campaigns, viral attempts

---

### 🔴 **PROFESSIONAL Mode** (19-22 Agents)
Maximum quality with full team collaboration

**All Advanced agents (15) plus:**

| Agent | Role | Responsibility |
|-------|------|----------------|
| 🧠 **Audience Psychologist** | Psychology | Viewer psychology, behavioral triggers |
| 🎨 **Designer** | Visual Design | Aesthetics, visual hierarchy, composition |
| ✍️ **Copywriter** | Copy Optimization | Headlines, hooks, CTAs, messaging |
| 📈 **Data Analyst** | Analytics | Performance metrics, data-driven insights |

**Note**: Some agents referenced in code but not fully implemented:
- Marketing Strategist
- Social Media Expert
- Analytics Expert
- Visual Designer
- Motion Graphics
- Color Specialist
- Typography Expert
- Platform Optimizer
- Audience Researcher
- Thumbnail Designer

**Use Case**: Premium content, major campaigns, maximum viral potential

---

## 🎯 Discussion Topics by Mode

### Simple Mode
- **Duration Validation** only (mandatory)

### Enhanced Mode (5 Topics)
1. **Content Optimization** - Script, visuals, narrative
2. **Visual Storytelling** - Scene composition, style
3. **Audio Strategy** - Voice, music, effects
4. **Platform Optimization** - Platform-specific features
5. **Duration Validation** - Timing constraints

### Advanced Mode (7 Topics)
All Enhanced topics plus:
6. **Viral Mechanics** - Shareability factors
7. **Audience Psychology** - Behavioral triggers

### Professional Mode (10+ Topics)
All Advanced topics plus:
- **Brand Strategy** - Brand alignment
- **Marketing Strategy** - Promotion planning
- **Design Strategy** - Visual hierarchy
- **Engagement Strategy** - Retention optimization
- **Data-Driven Insights** - Analytics-based decisions
- **Neurological Optimization** - Brain engagement
- **Copy Optimization** - Messaging refinement

---

## 💡 When to Use Each Mode

### Use **SIMPLE** when:
- Testing new features
- Running in cheap mode
- Need quick results
- Limited computational resources

### Use **ENHANCED** when:
- Creating standard content
- Need good quality without excessive processing
- Default for most use cases
- Balance of speed and quality

### Use **ADVANCED** when:
- Creating viral content attempts
- Brand campaigns
- Need specialized expertise
- Platform-specific optimization crucial

### Use **PROFESSIONAL** when:
- Maximum quality required
- High-value content
- Complex multi-faceted campaigns
- Need comprehensive analysis
- Budget allows for maximum AI usage

---

## 🔄 LangGraph Integration

When LangGraph is available, discussions follow this flow:
```
Initialize → Propose → Critique → Synthesize → Vote → Consensus Check → Finalize
```

**Benefits per Mode:**
- **Simple**: Basic consensus on duration
- **Enhanced**: Structured 5-topic discussions with synthesis
- **Advanced**: Deep 7-topic analysis with voting
- **Professional**: Comprehensive 10+ topic orchestration with full state management

---

## 📊 Agent Interaction Matrix

### Simple Mode
```
Director ↔ Script Writer ↔ Video Generator
```

### Enhanced Mode
```
        Director
       ↗        ↘
Script Writer   Video Generator
       ↓            ↓
   Soundman ← → Editor
        ↘        ↙
      Orchestrator
           ↓
     Neuroscientist
```

### Professional Mode
- Full mesh network: All agents can interact
- LangGraph manages state between all agents
- Consensus building across 19+ agents
- Multi-round discussions with memory

---

## 🎮 Command Examples

```bash
# Simple mode (3 agents)
python main.py generate --mode simple --cheap

# Enhanced mode (7 agents) - DEFAULT
python main.py generate --mode enhanced

# Advanced mode (15 agents)
python main.py generate --mode advanced

# Professional mode (19+ agents)
python main.py generate --mode professional --discussions deep

# With LangGraph for better discussions
python main.py generate --mode professional --langgraph
```

---

## 📈 Performance Impact

| Mode | Agents | API Calls | Time | Cost | Quality |
|------|--------|-----------|------|------|---------|
| Simple | 3 | ~10-20 | 1-2 min | $ | ⭐⭐ |
| Enhanced | 7 | ~30-50 | 2-4 min | $$ | ⭐⭐⭐ |
| Advanced | 15 | ~60-100 | 4-6 min | $$$ | ⭐⭐⭐⭐ |
| Professional | 19+ | ~100-200 | 6-10 min | $$$$ | ⭐⭐⭐⭐⭐ |

---

*Note: Actual agent availability depends on implementation status. Some agents are planned but not yet fully implemented.*