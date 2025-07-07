#!/usr/bin/env python3
"""
Enhanced Custom video generator with multi-language support
"""
import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.video_generator import VideoGenerator
from src.generators.multi_language_generator import MultiLanguageVideoGenerator
from src.models.video_models import (
    GeneratedVideoConfig, Platform, VideoCategory, 
    Narrative, Feeling, Language
)
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

def create_enhanced_video_config(prompt: str, duration: int, style: str = "engaging", 
                               narrative: str = "neutral", feeling: str = "engaging",
                               languages: list = None) -> GeneratedVideoConfig:
    """Create enhanced video configuration with multi-language support"""
    
    try:
        import google.generativeai as genai
        import json
        import re
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-pro')
        
        # Enhanced content prompt for better realism
        content_prompt = f"""
        Create a comprehensive video specification for this topic that will be realistic and engaging:
        
        TOPIC: {prompt}
        DURATION: {duration} seconds
        STYLE: {style}
        NARRATIVE: {narrative}
        FEELING: {feeling}
        
        Generate a detailed JSON specification:
        {{
            "tone": "emotional tone for the video",
            "target_audience": "specific audience description",
            "hook": "compelling opening line for first 3 seconds",
            "main_content": [
                "content point 1",
                "content point 2", 
                "content point 3",
                "content point 4"
            ],
            "call_to_action": "engaging ending that encourages sharing",
            "visual_style": "description of visual approach that's realistic and authentic",
            "color_scheme": ["#color1", "#color2", "#color3"],
            "background_music_style": "music style that fits the {feeling} feeling",
            "voiceover_style": "natural, {feeling} and {narrative} speaking style",
            "sound_effects": ["relevant", "sound", "effects"],
            "predicted_viral_score": 0.85
        }}
        
        CRITICAL: Ensure all content is:
        - Culturally sensitive and authentic
        - Realistic and achievable with video generation
        - Appropriate for the {feeling} emotional tone
        - Suitable for {narrative} narrative perspective
        
        Return only valid JSON.
        """
        
        response = model.generate_content(content_prompt)
        json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
        
        if json_match:
            ai_spec = json.loads(json_match.group())
            
            # Determine languages
            primary_language = Language.ENGLISH
            additional_languages = []
            
            if languages:
                lang_map = {
                    'english': Language.ENGLISH,
                    'arabic': Language.ARABIC, 
                    'hebrew': Language.HEBREW
                }
                
                primary_language = lang_map.get(languages[0].lower(), Language.ENGLISH)
                for lang in languages[1:]:
                    if lang.lower() in lang_map:
                        additional_languages.append(lang_map[lang.lower()])
            
            config = GeneratedVideoConfig(
                target_platform=Platform.INSTAGRAM,
                category=VideoCategory.ENTERTAINMENT,
                duration_seconds=duration,
                narrative=Narrative(narrative),
                feeling=Feeling(feeling),
                primary_language=primary_language,
                additional_languages=additional_languages,
                topic=prompt,
                style=style,
                tone=ai_spec.get('tone', f'{feeling} and {narrative}'),
                target_audience=ai_spec.get('target_audience', 'social media users'),
                hook=ai_spec.get('hook', f'Amazing {prompt} content!'),
                main_content=ai_spec.get('main_content', [
                    f"Opening scene for {prompt}",
                    f"Main development",
                    f"Exciting moment",
                    f"Conclusion"
                ]),
                call_to_action=ai_spec.get('call_to_action', 'Follow for more!'),
                visual_style=ai_spec.get('visual_style', f'{feeling} visual style'),
                color_scheme=ai_spec.get('color_scheme', ["#FF6B6B", "#4ECDC4", "#FFFFFF"]),
                text_overlays=[],
                transitions=["fade", "zoom"],
                background_music_style=ai_spec.get('background_music_style', f'{feeling} music'),
                voiceover_style=ai_spec.get('voiceover_style', f'natural, {feeling} and {narrative}'),
                sound_effects=ai_spec.get('sound_effects', ["ambient", "emphasis"]),
                inspired_by_videos=[],
                predicted_viral_score=ai_spec.get('predicted_viral_score', 0.8)
            )
            
            return config
            
        else:
            raise ValueError("Could not parse AI response")
            
    except Exception as e:
        logger.error(f"Error creating config: {e}")
        # Fallback configuration
        return GeneratedVideoConfig(
            target_platform=Platform.INSTAGRAM,
            category=VideoCategory.ENTERTAINMENT,
            duration_seconds=duration,
            narrative=Narrative.NEUTRAL,
            feeling=Feeling.ENERGETIC,
            primary_language=Language.ENGLISH,
            topic=prompt,
            style=style,
            tone=feeling,
            target_audience="social media users",
            hook=f"Get ready for {prompt}!",
            main_content=[f"Content about {prompt}"],
            call_to_action="Follow for more!",
            visual_style=f"{feeling} content",
            color_scheme=["#FF6B6B", "#4ECDC4", "#FFFFFF"],
            text_overlays=[],
            transitions=["fade"],
            background_music_style=f"{feeling} music",
            voiceover_style=f"{feeling} voiceover",
            sound_effects=[],
            inspired_by_videos=[],
            predicted_viral_score=0.75
        )

def main():
    parser = argparse.ArgumentParser(description='🎬 Enhanced Viral Video Generator with Multi-Language Support')
    parser.add_argument('--duration', type=int, default=30, help='Video duration in seconds (default: 30)')
    parser.add_argument('--style', default='engaging', help='Video style (default: engaging)')
    parser.add_argument('--narrative', default='neutral', 
                       choices=['pro_american_government', 'pro_soccer', 'against_animal_abuse', 
                               'pro_environment', 'pro_technology', 'pro_health', 'pro_education', 
                               'pro_family', 'neutral'],
                       help='Narrative perspective (default: neutral)')
    parser.add_argument('--feeling', default='energetic',
                       choices=['serious', 'funny', 'cynical', 'inspirational', 'dramatic', 
                               'playful', 'emotional', 'energetic', 'calm'],
                       help='Emotional tone (default: energetic)')
    parser.add_argument('--languages', nargs='*', default=['english'], 
                        choices=['english', 'arabic', 'hebrew'],
                        help='Languages to generate (for multi-language videos)')
    parser.add_argument('--realistic-audio', action='store_true',
                        help='Use Google Cloud TTS for natural-sounding voices (requires setup)')
    parser.add_argument('--real-veo2', action='store_true', help='Use real Veo-2 for video generation')
    parser.add_argument('--image-only', action='store_true', help='Generate AI images instead of videos - creates 2 images per second')
    parser.add_argument('prompt', help='Video topic/prompt')
    
    args = parser.parse_args()
    
    # Enhanced logging
    print("🎬 Enhanced Viral Video Generator")
    print(f"📝 Prompt: {args.prompt}")
    print(f"⏱️  Duration: {args.duration} seconds")
    print(f"🎨 Style: {args.style}")
    print(f"📖 Narrative: {args.narrative}")
    print(f"🎭 Feeling: {args.feeling}")
    print(f"🌍 Languages: {', '.join(args.languages)}")
    print(f"🎤 Realistic Audio: {'Yes' if args.realistic_audio else 'No'}")
    print(f"🤖 Real Veo-2: {'Yes' if args.real_veo2 else 'No'}")
    print(f"🖼️ Image Only: {'Yes' if args.image_only else 'No'}")
    print("=" * 60)
    
    # Get API key
    google_api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not google_api_key:
        print("❌ Error: No API key found!")
        print("Please set GOOGLE_API_KEY or GEMINI_API_KEY in your .env file")
        return
    
    if os.getenv('GOOGLE_API_KEY') and os.getenv('GEMINI_API_KEY'):
        print("Both GOOGLE_API_KEY and GEMINI_API_KEY are set. Using GOOGLE_API_KEY.")
    
    try:
        # Create enhanced configuration
        config = create_enhanced_video_config(
            args.prompt, args.duration, args.style, 
            args.narrative, args.feeling, args.languages
        )
        
        # Generate video
        if len(args.languages) > 1:
            # Multi-language generation
            print(f"🌍 Generating multi-language video in {len(args.languages)} languages...")
            generator = MultiLanguageVideoGenerator(api_key=google_api_key)
            
            multilang_video = generator.generate_multilingual_video(config)
            
            print("✅ Multi-language video generation complete!")
            print(f"📁 Base ID: {multilang_video.base_video_id}")
            print(f"⏱️  Total time: {multilang_video.total_generation_time:.1f}s")
            
            print("\n🌍 Generated Videos:")
            for lang, version in multilang_video.language_versions.items():
                print(f"  {version.language_name}: {version.video_path}")
                print(f"    Audio: {version.audio_duration:.1f}s, Words: {version.word_count}")
        
        else:
            # Single language generation with enhanced TTS
            print(f"🎬 Generating single-language video...")
            generator = VideoGenerator(api_key=google_api_key, use_real_veo2=args.real_veo2)
            
            generated_video = generator.generate_video(config)
            
            print("✅ Video generated successfully!")
            print(f"📁 File: {generated_video.file_path}")
            print(f"📏 Size: {generated_video.file_size_mb:.2f} MB")
            print(f"⏱️  Duration: {args.duration} seconds")
            print(f"🎯 Predicted viral score: {config.predicted_viral_score:.2f}")
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        print(f"❌ Generation failed: {e}")

if __name__ == "__main__":
    main() 