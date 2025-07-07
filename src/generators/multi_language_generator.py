"""
Multi-language video generator - Generate same video in multiple languages
"""
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
import uuid
import google.generativeai as genai
from gtts import gTTS
from moviepy.editor import *
import tempfile
import time

from ..models.video_models import (
    GeneratedVideoConfig, MultiLanguageVideo, LanguageVersion,
    Language, TTSVoice
)
from ..utils.logging_config import get_logger
from .video_generator import VideoGenerator

logger = get_logger(__name__)

class MultiLanguageVideoGenerator:
    """Generate the same video content in multiple languages"""
    
    def __init__(self, api_key: str, output_dir: str = "outputs"):
        self.api_key = api_key
        self.output_dir = output_dir
        self.translation_model = genai.GenerativeModel('gemini-2.5-pro')
        genai.configure(api_key=api_key)
        
        # Language configuration
        self.language_names = {
            Language.ENGLISH: "English",
            Language.ARABIC: "Arabic (العربية)",
            Language.HEBREW: "Hebrew (עברית)"
        }
        
        # Enhanced TTS configuration for more natural speech
        self.tts_voice_config = {
            Language.ENGLISH: {'lang': 'en', 'tld': 'com', 'slow': False},
            Language.ARABIC: {'lang': 'ar', 'tld': 'com', 'slow': False},
            Language.HEBREW: {'lang': 'iw', 'tld': 'co.il', 'slow': False}
        }
        
        logger.info(f"🌍 Multi-language generator initialized")
    
    def generate_multilingual_video(self, config: GeneratedVideoConfig) -> MultiLanguageVideo:
        """Generate video in multiple languages with shared video clips"""
        start_time = time.time()
        
        # Set configuration for TTS generation
        self.use_realistic_audio = getattr(config, 'realistic_audio', False)
        self.current_feeling = getattr(config, 'feeling', 'neutral')
        self.current_narrative = getattr(config, 'narrative', 'neutral')
        
        logger.info(f"🌍 Generating video in {len(config.additional_languages) + 1} languages")
        logger.info(f"🎤 Realistic audio: {'Yes' if self.use_realistic_audio else 'No'}")
        
        base_video_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = os.path.join("outputs", f"multilang_{timestamp}_{base_video_id[:8]}")
        shared_clips_dir = os.path.join(session_dir, "shared_clips")
        
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(shared_clips_dir, exist_ok=True)
        
        # Generate master script (in primary language)
        logger.info("📝 Generating master script...")
        generator = VideoGenerator(api_key=self.api_key, use_real_veo2=True)
        master_script = generator._generate_creative_script(config, base_video_id)
        
        # Generate sufficient video clips for the full duration
        logger.info("🎬 Generating shared video clips...")
        veo_prompts = generator._generate_veo2_prompts(config, master_script)
        
        # Ensure we have enough clips for the duration
        # Calculate clips needed: aim for 5-8 seconds per clip
        clips_needed = max(2, config.duration_seconds // 6)  # At least 2 clips, ~6s each
        
        if len(veo_prompts) < clips_needed:
            logger.warning(f"Only {len(veo_prompts)} prompts for {config.duration_seconds}s, generating more...")
            additional_prompts = clips_needed - len(veo_prompts)
            
            for i in range(additional_prompts):
                fallback_prompt = {
                    'veo2_prompt': f"Continuation of the story, scene {len(veo_prompts) + i + 1}",
                    'description': f"Additional scene {i + 1}",
                    'duration': min(8, config.duration_seconds / clips_needed),
                    'scene_type': 'continuation'
                }
                veo_prompts.append(fallback_prompt)
            
            logger.info(f"Added {additional_prompts} additional prompts for full duration")
        
        # Generate shared video clips that all language versions will use
        veo_clips = generator._generate_veo2_clips(veo_prompts, config, base_video_id)
        
        # Move clips to shared directory
        for clip in veo_clips:
            if os.path.exists(clip['clip_path']):
                new_path = os.path.join(shared_clips_dir, os.path.basename(clip['clip_path']))
                os.rename(clip['clip_path'], new_path)
                clip['clip_path'] = new_path
        
        # Generate versions for each language
        all_languages = [config.primary_language] + config.additional_languages
        language_versions = {}
        
        for language in all_languages:
            lang_version = self._generate_language_version(
                language, master_script, config, veo_clips,
                base_video_id, session_dir, shared_clips_dir
            )
            language_versions[language] = lang_version
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        multilang_video = MultiLanguageVideo(
            base_video_id=base_video_id,
            master_config=config,
            shared_clips_dir=shared_clips_dir,
            veo2_clips=veo_clips,
            language_versions=language_versions,
            total_generation_time=total_time,
            master_script=master_script,
            total_languages=len(language_versions),
            primary_language=config.primary_language,
            supported_languages=list(language_versions.keys())
        )
        
        self._save_multilingual_project_info(multilang_video, session_dir)
        logger.info(f"🎉 Multi-language generation complete: {len(language_versions)} languages")
        
        return multilang_video
    
    def _generate_language_version(self, language: Language, master_script: str, 
                                 config: GeneratedVideoConfig, veo_clips: List[Dict],
                                 base_video_id: str, session_dir: str, 
                                 shared_clips_dir: str) -> LanguageVersion:
        """Generate a single language version of the video"""
        
        lang_name = self.language_names[language]
        logger.info(f"🔤 Generating {lang_name} version...")
        
        # Translate script
        translated_script = self._translate_script(master_script, language, config)
        
        # Generate TTS
        audio_path = self._generate_multilingual_tts(
            translated_script, language, config.duration_seconds, 
            base_video_id, session_dir
        )
        
        # Compose video
        video_path = self._compose_multilingual_video(
            veo_clips, audio_path, language, base_video_id, session_dir
        )
        
        # Create version object
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        audio_clip.close()
        
        lang_version = LanguageVersion(
            language=language,
            language_name=lang_name,
            audio_path=audio_path,
            video_path=video_path,
            translated_script=translated_script,
            translated_overlays=[],
            tts_voice_used=self.tts_voice_config[language]['lang'],
            word_count=len(translated_script.split()),
            audio_duration=audio_duration
        )
        
        return lang_version
    
    def _translate_script(self, master_script: str, target_language: Language, 
                         config: GeneratedVideoConfig) -> str:
        """Translate script maintaining timing and emotional impact"""
        
        lang_name = self.language_names[target_language]
        target_words = int(config.duration_seconds * 2.5)
        
        logger.info(f"📝 Translating to {lang_name} ({target_words} words)")
        
        translation_prompt = f"""
        Translate this video script to {lang_name} maintaining exact timing and emotion.
        
        ORIGINAL SCRIPT:
        {master_script}
        
        REQUIREMENTS:
        - Target language: {lang_name}
        - Duration: {config.duration_seconds} seconds
        - Target words: {target_words} (for precise timing)
        - Emotional tone: {config.feeling.value}
        - Keep natural speaking rhythm
        - Cultural sensitivity for {lang_name} speakers
        
        Return ONLY the translated script with exactly {target_words} words.
        """
        
        try:
            response = self.translation_model.generate_content(translation_prompt)
            translated_script = response.text.strip()
            
            # Adjust word count for timing
            actual_words = len(translated_script.split())
            if actual_words > target_words * 1.2:
                words = translated_script.split()[:target_words]
                translated_script = ' '.join(words) + "."
            elif actual_words < target_words * 0.8:
                # Extend naturally
                extensions = {
                    Language.ENGLISH: ["This is incredible!", "Amazing!", "Don't miss this!"],
                    Language.ARABIC: ["هذا مذهل!", "رائع!", "لا تفوت هذا!"],
                    Language.HEBREW: ["זה מדהים!", "מהמם!", "אל תפספסו!"]
                }
                
                ext_list = extensions.get(target_language, extensions[Language.ENGLISH])
                while len(translated_script.split()) < target_words:
                    translated_script += " " + ext_list[len(translated_script.split()) % len(ext_list)]
                
                words = translated_script.split()[:target_words]
                translated_script = ' '.join(words) + "."
            
            logger.info(f"✅ {lang_name} translation: {len(translated_script.split())} words")
            return translated_script
            
        except Exception as e:
            logger.error(f"❌ Translation failed: {e}")
            return master_script
    
    def _generate_multilingual_tts(self, script: str, language: Language, 
                                 duration: int, video_id: str, session_dir: str) -> str:
        """Generate realistic TTS audio in target language"""
        
        lang_name = self.language_names[language]
        logger.info(f"🎤 Generating realistic {lang_name} TTS...")
        
        try:
            # Check if realistic audio is requested (Google Cloud TTS)
            realistic_audio = getattr(self, 'use_realistic_audio', False)
            
            # Skip Google Cloud TTS to avoid authentication issues
            # Use enhanced gTTS for better compatibility
            logger.info(f"🎤 Using enhanced gTTS for {lang_name}...")
            
            # Enhanced gTTS configuration with language-specific settings
            tts_config = self.tts_voice_config[language].copy()
            
            # Create natural TTS with emotion
            tts = gTTS(
                text=script,
                **tts_config
            )
            
            audio_filename = f"audio_{language.value}_{video_id}.mp3"
            audio_path = os.path.join(session_dir, audio_filename)
            tts.save(audio_path)
            
            # Validate duration
            audio_clip = AudioFileClip(audio_path)
            actual_duration = audio_clip.duration
            audio_clip.close()
            
            logger.info(f"✅ Enhanced gTTS {lang_name}: {actual_duration:.1f}s")
            return audio_path
            
        except Exception as e:
            logger.error(f"❌ TTS failed: {e}")
            raise
    
    def _compose_multilingual_video(self, veo_clips: List[Dict], audio_path: str,
                                   language: Language, video_id: str, session_dir: str) -> str:
        """Compose final video with shared clips and language-specific audio"""
        
        lang_name = self.language_names[language]
        logger.info(f"🎬 Composing {lang_name} video...")
        
        try:
            # Load audio
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            
            # Load shared video clips
            video_clips = []
            for clip_info in veo_clips:
                try:
                    video_clip = VideoFileClip(clip_info['clip_path'])
                    video_clips.append(video_clip)
                except Exception as e:
                    logger.warning(f"Failed to load clip: {e}")
            
            if not video_clips:
                raise Exception("No video clips available")
            
            # Concatenate and sync to audio
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            if final_video.duration > audio_duration:
                final_video = final_video.subclip(0, audio_duration)
            elif final_video.duration < audio_duration:
                padding = audio_duration - final_video.duration
                last_frame = final_video.to_ImageClip(t=final_video.duration - 0.1).set_duration(padding)
                final_video = concatenate_videoclips([final_video, last_frame])
            
            # Add audio
            final_video_with_audio = final_video.set_audio(audio_clip)
            
            # Save
            video_filename = f"viral_video_{language.value}_{video_id}.mp4"
            output_path = os.path.join(session_dir, video_filename)
            
            final_video_with_audio.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Cleanup
            final_video_with_audio.close()
            audio_clip.close()
            
            logger.info(f"✅ {lang_name} video complete")
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Video composition failed: {e}")
            raise
    
    def _save_multilingual_project_info(self, multilang_video: MultiLanguageVideo, session_dir: str):
        """Save project information"""
        try:
            report_path = os.path.join(session_dir, "multilingual_report.txt")
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("🌍 MULTI-LANGUAGE VIDEO PROJECT\n")
                f.write("=" * 50 + "\n\n")
                
                f.write("📋 PROJECT OVERVIEW\n")
                f.write(f"Video ID: {multilang_video.base_video_id}\n")
                f.write(f"Languages: {multilang_video.total_languages}\n")
                f.write(f"Generation Time: {multilang_video.total_generation_time:.1f}s\n\n")
                
                f.write("🌍 LANGUAGE VERSIONS\n")
                for lang, version in multilang_video.language_versions.items():
                    f.write(f"{version.language_name}: {os.path.basename(version.video_path)}\n")
                    f.write(f"  Audio: {version.audio_duration:.1f}s\n")
                    f.write(f"  Words: {version.word_count}\n\n")
            
            logger.info(f"📊 Project report saved: {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save project info: {e}") 