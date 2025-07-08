#!/usr/bin/env python3
"""
AI-Powered Topic Generation System
==================================

This module provides intelligent topic generation through multi-agent discussions.
Given a high-level idea or goal, AI agents will discuss and craft optimal video topics.
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import google.generativeai as genai

from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class TopicGenerationAgent:
    """Individual AI agent for topic generation discussions"""
    
    def __init__(self, role: str, expertise: str, api_key: str):
        self.role = role
        self.expertise = expertise
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        
    def discuss_topic(self, idea: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate topic suggestion based on idea and context"""
        try:
            prompt = f"""
You are {self.role}, an expert in {self.expertise}.

TASK: Generate a specific, actionable video topic based on this high-level idea:
"{idea}"

CONTEXT:
- Target Platform: {context.get('platform', 'YouTube')}
- Target Audience: {context.get('audience', 'General')}
- Content Style: {context.get('style', 'Engaging')}
- Duration: {context.get('duration', 30)} seconds
- Category: {context.get('category', 'Educational')}

REQUIREMENTS:
1. Create a SPECIFIC video topic (not generic)
2. Ensure it's ACTIONABLE and VIRAL-WORTHY
3. Consider ethical implications and platform guidelines
4. Make it ENGAGING and SHAREABLE
5. Provide clear REASONING for your choice

RESPONSE FORMAT:
{{
    "topic": "Specific video topic here",
    "reasoning": "Why this topic will be effective",
    "target_emotion": "Primary emotion to evoke",
    "key_message": "Core message to convey",
    "viral_potential": "Why this could go viral (1-10 scale)",
    "ethical_considerations": "Any concerns or safeguards needed"
}}

Focus on creating content that is persuasive but ethical, engaging but responsible.
"""
            
            response = self.model.generate_content(prompt)
            
            # Parse JSON response
            try:
                result = json.loads(response.text.strip())
                result['agent_role'] = self.role
                result['agent_expertise'] = self.expertise
                return result
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    "topic": f"Engaging content about {idea}",
                    "reasoning": response.text[:200],
                    "target_emotion": "Interest",
                    "key_message": "Educational content",
                    "viral_potential": "7",
                    "ethical_considerations": "Standard content guidelines",
                    "agent_role": self.role,
                    "agent_expertise": self.expertise
                }
                
        except Exception as e:
            logger.error(f"❌ Topic generation failed for {self.role}: {e}")
            return {
                "topic": f"Content about {idea}",
                "reasoning": f"Fallback topic due to error: {e}",
                "target_emotion": "Interest",
                "key_message": "General content",
                "viral_potential": "5",
                "ethical_considerations": "Standard guidelines",
                "agent_role": self.role,
                "agent_expertise": self.expertise,
                "error": str(e)
            }

class TopicGeneratorSystem:
    """AI-powered topic generation system with multi-agent discussions"""
    
    def __init__(self, api_key: str, output_dir: str = "outputs"):
        self.api_key = api_key
        self.output_dir = output_dir
        self.session_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Initialize Gemini
        genai.configure(api_key=api_key)
        
        # Define specialized agents for topic generation
        self.agents = [
            TopicGenerationAgent("ContentStrategist", "viral content strategy and audience engagement", api_key),
            TopicGenerationAgent("PsychologyExpert", "human psychology and persuasion techniques", api_key),
            TopicGenerationAgent("EthicsAdvisor", "content ethics and responsible messaging", api_key),
            TopicGenerationAgent("PlatformSpecialist", "social media platform optimization", api_key),
            TopicGenerationAgent("TrendAnalyst", "viral trends and content patterns", api_key),
            TopicGenerationAgent("CommunicationExpert", "effective messaging and storytelling", api_key)
        ]
        
        logger.info(f"🤖 TopicGenerator initialized with {len(self.agents)} specialized agents")
    
    def generate_topic(self, idea: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate an optimal video topic through AI agent discussions
        
        Args:
            idea: High-level idea or goal (e.g., "convince Israelis to protest")
            context: Additional context (platform, audience, etc.)
            
        Returns:
            Dict containing the final topic and discussion results
        """
        if context is None:
            context = {
                'platform': 'YouTube',
                'audience': 'General',
                'style': 'Engaging',
                'duration': 30,
                'category': 'Educational'
            }
        
        logger.info(f"🎯 Starting topic generation for idea: '{idea}'")
        
        # Create session directory
        session_dir = os.path.join(self.output_dir, f"topic_session_{self.session_id}")
        os.makedirs(session_dir, exist_ok=True)
        
        try:
            # Phase 1: Individual agent topic suggestions
            agent_suggestions = []
            for agent in self.agents:
                logger.info(f"💭 Getting suggestion from {agent.role}...")
                suggestion = agent.discuss_topic(idea, context)
                agent_suggestions.append(suggestion)
                time.sleep(1)  # Rate limiting
            
            # Save individual suggestions
            suggestions_file = os.path.join(session_dir, "individual_suggestions.json")
            with open(suggestions_file, 'w') as f:
                json.dump(agent_suggestions, f, indent=2)
            
            # Phase 2: Multi-agent discussion to reach consensus
            logger.info("🗣️ Starting multi-agent discussion for consensus...")
            
            # Prepare discussion context
            discussion_context = {
                "original_idea": idea,
                "context": context,
                "agent_suggestions": agent_suggestions,
                "goal": "Select and refine the best topic for maximum viral potential while maintaining ethics"
            }
            
            # Conduct discussion using simplified consensus
            discussion_result = self._conduct_consensus_discussion(discussion_context, session_dir)
            
            # Phase 3: Generate final topic with context
            final_topic = self._finalize_topic(discussion_result, agent_suggestions, context)
            
            # Save complete results
            results = {
                "session_id": self.session_id,
                "original_idea": idea,
                "input_context": context,
                "agent_suggestions": agent_suggestions,
                "discussion_result": discussion_result,
                "final_topic": final_topic,
                "generation_timestamp": datetime.now().isoformat(),
                "session_directory": session_dir
            }
            
            results_file = os.path.join(session_dir, "topic_generation_results.json")
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"✅ Topic generation complete!")
            logger.info(f"🎯 Final Topic: {final_topic['topic']}")
            logger.info(f"📁 Results saved to: {session_dir}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Topic generation failed: {e}")
            # Return fallback result
            fallback_topic = {
                "topic": f"Engaging content about {idea}",
                "reasoning": f"Fallback topic due to system error: {e}",
                "context_for_agents": f"Create content that addresses: {idea}",
                "viral_potential": "5",
                "ethical_considerations": "Standard content guidelines",
                "error": str(e)
            }
            
            return {
                "session_id": self.session_id,
                "original_idea": idea,
                "final_topic": fallback_topic,
                "error": str(e)
            }
    
    def _conduct_consensus_discussion(self, context: Dict[str, Any], session_dir: str) -> Dict[str, Any]:
        """Conduct multi-agent discussion to reach consensus on best topic"""
        try:
            # Create discussion prompt
            suggestions_summary = "\n".join([
                f"- {s['agent_role']}: '{s['topic']}' (Viral Potential: {s['viral_potential']}/10)"
                for s in context['agent_suggestions']
            ])
            
            discussion_prompt = f"""
TOPIC GENERATION CONSENSUS DISCUSSION

Original Idea: {context['original_idea']}
Platform: {context['context']['platform']}
Target Audience: {context['context']['audience']}

AGENT SUGGESTIONS:
{suggestions_summary}

TASK: Discuss and reach consensus on the BEST topic that:
1. Effectively addresses the original idea
2. Has maximum viral potential
3. Maintains ethical standards
4. Is optimized for the target platform
5. Will engage the target audience

Consider combining elements from different suggestions or creating a refined version.
Focus on specificity, actionability, and viral potential.
"""
            
            # Use simplified discussion system
            consensus_agents = ['ContentStrategist', 'PsychologyExpert', 'EthicsAdvisor', 'TrendAnalyst']
            
            discussion_result = {
                "consensus_topic": None,
                "reasoning": "",
                "participants": consensus_agents,
                "rounds": 1
            }
            
            # Get consensus from primary agents
            try:
                model = genai.GenerativeModel("gemini-2.5-flash")
                consensus_prompt = f"""
{discussion_prompt}

As a consensus of expert agents, provide the FINAL OPTIMAL TOPIC:

RESPONSE FORMAT:
{{
    "final_topic": "Specific, actionable video topic",
    "reasoning": "Why this topic is optimal",
    "viral_elements": ["element1", "element2", "element3"],
    "ethical_safeguards": ["safeguard1", "safeguard2"],
    "platform_optimization": "How it's optimized for the platform",
    "expected_engagement": "High/Medium/Low with explanation"
}}
"""
                
                response = model.generate_content(consensus_prompt)
                
                try:
                    consensus_result = json.loads(response.text.strip())
                    discussion_result["consensus_topic"] = consensus_result
                    discussion_result["reasoning"] = consensus_result.get("reasoning", "")
                except json.JSONDecodeError:
                    discussion_result["consensus_topic"] = {
                        "final_topic": f"Optimized content about {context['original_idea']}",
                        "reasoning": response.text[:300],
                        "viral_elements": ["engaging", "relevant", "shareable"],
                        "ethical_safeguards": ["responsible messaging"],
                        "platform_optimization": "Standard optimization",
                        "expected_engagement": "Medium"
                    }
                
            except Exception as e:
                logger.warning(f"Consensus discussion failed: {e}")
                # Use best individual suggestion as fallback
                best_suggestion = max(context['agent_suggestions'], 
                                    key=lambda x: int(x.get('viral_potential', '5')))
                discussion_result["consensus_topic"] = {
                    "final_topic": best_suggestion['topic'],
                    "reasoning": best_suggestion['reasoning'],
                    "viral_elements": ["engaging"],
                    "ethical_safeguards": [best_suggestion.get('ethical_considerations', '')],
                    "platform_optimization": "Standard",
                    "expected_engagement": "Medium"
                }
            
            # Save discussion result
            discussion_file = os.path.join(session_dir, "consensus_discussion.json")
            with open(discussion_file, 'w') as f:
                json.dump(discussion_result, f, indent=2)
            
            return discussion_result
            
        except Exception as e:
            logger.error(f"Discussion failed: {e}")
            return {"error": str(e), "consensus_topic": None}
    
    def _finalize_topic(self, discussion_result: Dict[str, Any], 
                       agent_suggestions: List[Dict[str, Any]], 
                       context: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize the topic with context for other AI agents"""
        
        try:
            if discussion_result.get("consensus_topic"):
                consensus = discussion_result["consensus_topic"]
                final_topic = consensus["final_topic"]
                reasoning = consensus.get("reasoning", "")
            else:
                # Fallback to best individual suggestion
                best_suggestion = max(agent_suggestions, 
                                    key=lambda x: int(x.get('viral_potential', '5')))
                final_topic = best_suggestion['topic']
                reasoning = best_suggestion['reasoning']
            
            # Create context for other AI agents
            agent_context = f"""
TOPIC GENERATION CONTEXT:
This topic was generated through multi-agent discussion to address: "{context.get('original_idea', 'content creation')}"

The AI agents considered:
- Viral potential and engagement factors
- Ethical implications and responsible messaging  
- Platform-specific optimization
- Target audience psychology
- Current trends and patterns

STRATEGIC CONTEXT FOR VIDEO CREATION:
{reasoning}

This topic is designed to be compelling, shareable, and ethically responsible.
"""
            
            return {
                "topic": final_topic,
                "reasoning": reasoning,
                "context_for_agents": agent_context,
                "viral_potential": consensus.get("expected_engagement", "Medium") if discussion_result.get("consensus_topic") else "Medium",
                "ethical_considerations": "; ".join(consensus.get("ethical_safeguards", [])) if discussion_result.get("consensus_topic") else "Standard guidelines",
                "platform_optimization": consensus.get("platform_optimization", "Standard") if discussion_result.get("consensus_topic") else "Standard",
                "generation_method": "multi_agent_consensus",
                "confidence": "High" if discussion_result.get("consensus_topic") else "Medium"
            }
            
        except Exception as e:
            logger.error(f"Topic finalization failed: {e}")
            return {
                "topic": f"Engaging content about {context.get('original_idea', 'the topic')}",
                "reasoning": f"Fallback topic due to error: {e}",
                "context_for_agents": "Create engaging, ethical content",
                "viral_potential": "Medium",
                "ethical_considerations": "Standard content guidelines",
                "error": str(e)
            } 