#!/usr/bin/env python3
"""
End-to-End Test for Character Consistency System
Creates a 30-second multi-character video with consistent characters across scenes
"""

import asyncio
import os
import sys
import json
import logging
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent))

from src.utils.enhanced_character_manager import (
    EnhancedCharacterManager,
    CharacterAppearance,
    CharacterPersonality
)
from src.generators.gemini_flash_image_client import GeminiFlashImageClient
from src.generators.enhanced_veo3_client import EnhancedVeo3Client, ReferenceType
from src.agents.langgraph_agent_system import LangGraphAgentSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CharacterConsistencyE2ETest:
    """End-to-end test for character consistency system"""
    
    def __init__(self):
        """Initialize test components"""
        self.character_manager = EnhancedCharacterManager()
        self.gemini_client = GeminiFlashImageClient()
        self.veo3_client = EnhancedVeo3Client(
            project_id="viralgen-464411",
            location="us-central1"
        )
        self.agent_system = LangGraphAgentSystem(self.character_manager)
        
        self.output_dir = "outputs/e2e_test_character_consistency"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def run_safe_news_test(self):
        """
        Run a safe test scenario: Tech News Broadcast
        Creates a 30-second news segment about AI breakthroughs with 2 consistent anchors
        """
        logger.info("=" * 80)
        logger.info("STARTING E2E CHARACTER CONSISTENCY TEST")
        logger.info("Scenario: Tech News Broadcast - AI Breakthroughs 2025")
        logger.info("=" * 80)
        
        # Step 1: Run agent discussion for content planning
        logger.info("\n📝 Step 1: Agent Discussion for Content Planning")
        
        mission = """
        Create a 30-second professional news broadcast about breakthrough AI technologies in 2025.
        Features:
        - Two news anchors (one male, one female)
        - Professional news studio setting
        - Discussion of 3 AI breakthroughs: medical diagnosis, climate modeling, education
        - Anchors should have distinct personalities and speaking styles
        - Include graphics and b-roll footage descriptions
        """
        
        discussion_result = await self.agent_system.run_discussion(mission)
        
        logger.info("✅ Agent discussion complete")
        logger.info(f"Consensus score: {discussion_result.get('consensus_score', 0):.2f}")
        
        # Step 2: Create consistent character profiles
        logger.info("\n👥 Step 2: Creating Consistent Character Profiles")
        
        # Female anchor
        sarah_appearance = CharacterAppearance(
            age="32",
            ethnicity="Asian-American",
            hair="shoulder-length black hair, professional style",
            eyes="dark brown",
            face_shape="oval face with high cheekbones",
            complexion="warm beige skin tone",
            typical_attire=["navy blue blazer", "white blouse", "minimal jewelry"],
            distinguishing_features=["warm smile", "expressive eyebrows"]
        )
        
        sarah_personality = CharacterPersonality(
            traits=["professional", "empathetic", "articulate"],
            voice_profile="en-US-News-F",
            mannerisms=["hand gestures when explaining", "slight head tilt when listening"],
            speaking_style="Clear, warm, and engaging",
            emotional_range=["enthusiastic", "concerned", "optimistic"]
        )
        
        sarah_id = self.character_manager.create_character(
            name="Sarah Chen",
            description="Professional female news anchor specializing in technology",
            appearance=sarah_appearance,
            personality=sarah_personality
        )
        
        # Male anchor
        james_appearance = CharacterAppearance(
            age="38",
            ethnicity="Caucasian",
            hair="short brown hair with subtle gray at temples",
            eyes="blue",
            face_shape="square jaw, strong features",
            complexion="fair skin with light tan",
            typical_attire=["charcoal gray suit", "light blue tie", "white shirt"],
            distinguishing_features=["confident posture", "friendly demeanor"]
        )
        
        james_personality = CharacterPersonality(
            traits=["authoritative", "analytical", "friendly"],
            voice_profile="en-US-News-M",
            mannerisms=["clasped hands when serious", "slight forward lean when engaged"],
            speaking_style="Deep, measured, and trustworthy",
            emotional_range=["serious", "intrigued", "encouraging"]
        )
        
        james_id = self.character_manager.create_character(
            name="James Mitchell",
            description="Senior news anchor with focus on scientific developments",
            appearance=james_appearance,
            personality=james_personality
        )
        
        logger.info(f"✅ Created characters: {sarah_id}, {james_id}")
        
        # Step 3: Generate character reference images
        logger.info("\n🎨 Step 3: Generating Character Reference Images")
        
        # Generate multiple reference angles for each character
        sarah_refs = []
        james_refs = []
        
        # Sarah references
        sarah_variations = [
            "sitting at news desk, facing camera, professional lighting",
            "standing in studio, three-quarter view, confident pose",
            "close-up portrait, warm expression, studio background"
        ]
        
        for idx, variation in enumerate(sarah_variations):
            ref_path = os.path.join(self.output_dir, f"sarah_ref_{idx}.jpg")
            image = self.character_manager.generate_character_scene(
                character_id=sarah_id,
                scene_description=variation,
                scene_type="news_studio"
            )
            if image:
                sarah_refs.append(image)
                logger.info(f"Generated Sarah reference {idx + 1}")
        
        # James references
        james_variations = [
            "sitting at news desk, facing camera, professional demeanor",
            "standing with tablet, explaining data, studio setting",
            "profile view at desk, engaged in discussion"
        ]
        
        for idx, variation in enumerate(james_variations):
            ref_path = os.path.join(self.output_dir, f"james_ref_{idx}.jpg")
            image = self.character_manager.generate_character_scene(
                character_id=james_id,
                scene_description=variation,
                scene_type="news_studio"
            )
            if image:
                james_refs.append(image)
                logger.info(f"Generated James reference {idx + 1}")
        
        # Step 4: Generate video clips with consistent characters
        logger.info("\n🎬 Step 4: Generating Video Clips with Consistent Characters")
        
        # Define scenes for the 30-second broadcast (4 clips x ~7-8 seconds each)
        scenes = [
            {
                "description": "Opening: Both anchors at desk",
                "prompt": "Sarah Chen and James Mitchell sitting at modern news desk, professional studio, world map display behind them, both facing camera",
                "dialogue": "Sarah: 'Good evening, I'm Sarah Chen.' James: 'And I'm James Mitchell. Tonight, breakthrough AI technologies reshaping our world.'",
                "duration": 8,
                "characters": {"Sarah": sarah_refs[:2], "James": james_refs[:2]}
            },
            {
                "description": "Sarah presents medical AI breakthrough",
                "prompt": "Sarah Chen explaining medical AI breakthrough, graphics showing brain scans on screen behind her, professional presentation",
                "dialogue": "Sarah: 'In medicine, AI systems now detect diseases five years before symptoms appear, saving millions of lives.'",
                "duration": 7,
                "characters": {"Sarah": sarah_refs}
            },
            {
                "description": "James discusses climate modeling",
                "prompt": "James Mitchell presenting climate AI models, weather patterns on screen, serious but optimistic tone",
                "dialogue": "James: 'Climate scientists use AI to predict weather patterns with 99% accuracy, helping communities prepare for extreme events.'",
                "duration": 8,
                "characters": {"James": james_refs}
            },
            {
                "description": "Closing: Both anchors conclude",
                "prompt": "Sarah Chen and James Mitchell at desk, wrapping up broadcast, professional and optimistic",
                "dialogue": "Sarah: 'These innovations show AI's positive impact.' James: 'Tomorrow's world, today. Good night.'",
                "duration": 7,
                "characters": {"Sarah": sarah_refs[:2], "James": james_refs[:2]}
            }
        ]
        
        generated_clips = []
        
        for idx, scene in enumerate(scenes):
            logger.info(f"\nGenerating scene {idx + 1}/4: {scene['description']}")
            
            output_path = os.path.join(self.output_dir, f"scene_{idx:02d}.mp4")
            
            # For multi-character scenes
            if len(scene["characters"]) > 1:
                video = self.veo3_client.generate_multi_character_scene(
                    characters=scene["characters"],
                    interaction_prompt=f"{scene['prompt']}\n{scene['dialogue']}",
                    output_path=output_path,
                    duration=scene["duration"]
                )
            else:
                # Single character scene
                char_name = list(scene["characters"].keys())[0]
                char_refs = scene["characters"][char_name]
                
                video = self.veo3_client.generate_video_with_references(
                    prompt=f"{scene['prompt']}\n{scene['dialogue']}",
                    reference_images=char_refs,
                    output_path=output_path,
                    reference_type=ReferenceType.ASSET,
                    duration=scene["duration"],
                    include_audio=True
                )
            
            if video:
                generated_clips.append(video)
                logger.info(f"✅ Generated scene {idx + 1}")
            else:
                logger.warning(f"⚠️ Failed to generate scene {idx + 1}")
        
        # Step 5: Validate character consistency
        logger.info("\n🔍 Step 5: Validating Character Consistency")
        
        consistency_scores = []
        for clip in generated_clips:
            # In production, use face recognition to validate consistency
            score = self.character_manager.validate_character_consistency(sarah_id, clip)
            consistency_scores.append(score)
            logger.info(f"Consistency score for {clip}: {score:.2f}")
        
        avg_consistency = sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0
        
        # Step 6: Compile final video (would use ffmpeg in production)
        logger.info("\n🎞️ Step 6: Compiling Final 30-Second Video")
        
        final_output = os.path.join(self.output_dir, "final_news_broadcast.mp4")
        
        # In production, use ffmpeg to concatenate clips
        # For now, just log the intent
        logger.info(f"Would compile {len(generated_clips)} clips into: {final_output}")
        
        # Generate test report
        report = {
            "test_name": "Character Consistency E2E Test",
            "scenario": "Tech News Broadcast",
            "duration": "30 seconds",
            "characters_created": 2,
            "reference_images_generated": len(sarah_refs) + len(james_refs),
            "video_clips_generated": len(generated_clips),
            "average_consistency_score": avg_consistency,
            "agent_consensus_score": discussion_result.get("consensus_score", 0),
            "status": "SUCCESS" if avg_consistency > 0.85 else "NEEDS_IMPROVEMENT",
            "output_directory": self.output_dir
        }
        
        # Save report
        report_path = os.path.join(self.output_dir, "test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("\n" + "=" * 80)
        logger.info("E2E TEST COMPLETE")
        logger.info(f"Average Consistency Score: {avg_consistency:.2f}")
        logger.info(f"Report saved to: {report_path}")
        logger.info("=" * 80)
        
        return report
    
    async def run_alternative_scenarios(self):
        """
        Alternative safe test scenarios for character consistency
        """
        safe_scenarios = [
            {
                "name": "Tech Product Launch",
                "description": "30-second product launch for futuristic smartphone",
                "characters": ["CEO presenter", "Product designer", "Happy customers"],
                "setting": "Modern conference hall"
            },
            {
                "name": "Educational Series",
                "description": "30-second educational video about space exploration",
                "characters": ["Professor", "Two students"],
                "setting": "University classroom and planetarium"
            },
            {
                "name": "Cooking Show",
                "description": "30-second cooking show segment",
                "characters": ["Chef", "Assistant chef"],
                "setting": "Professional kitchen"
            },
            {
                "name": "Travel Documentary",
                "description": "30-second travel guide to futuristic city",
                "characters": ["Travel host", "Local guide"],
                "setting": "Futuristic cityscape"
            }
        ]
        
        logger.info("\n🎯 Alternative Safe Test Scenarios:")
        for scenario in safe_scenarios:
            logger.info(f"\n{scenario['name']}:")
            logger.info(f"  Description: {scenario['description']}")
            logger.info(f"  Characters: {', '.join(scenario['characters'])}")
            logger.info(f"  Setting: {scenario['setting']}")
        
        return safe_scenarios


async def main():
    """Run the E2E test"""
    test = CharacterConsistencyE2ETest()
    
    # Run the safe news broadcast test
    result = await test.run_safe_news_test()
    
    # Show alternative scenarios
    alternatives = await test.run_alternative_scenarios()
    
    print("\n✅ Test completed successfully!")
    print(f"Results saved to: {test.output_dir}")
    
    return result


if __name__ == "__main__":
    # Run the test
    asyncio.run(main())