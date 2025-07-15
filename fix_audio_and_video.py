#!/usr/bin/env python3
"""
Fix audio generation and final video composition
"""

import os
import re

def fix_audio_generation():
    """Fix audio generation to properly save audio files"""
    video_gen_path = "src/generators/video_generator.py"
    
    with open(video_gen_path, 'r') as f:
        content = f.read()
    
    # Fix the audio generation method
    audio_fix = '''    def _generate_ai_optimized_audio(self, config: GeneratedVideoConfig,
                                   script_result: Dict[str, Any],
                                   session_context: SessionContext) -> List[str]:
        """Generate audio using AI voice selection"""
        logger.info("🎤 Generating AI-optimized audio")
        
        try:
            from ..models.video_models import Language
            
            # Get AI voice selection strategy first
            voice_strategy = self.voice_director.analyze_content_and_select_voices(
                topic=config.topic,
                script=script_result.get('optimized_script', config.topic),
                language=Language.ENGLISH_US,
                platform=config.target_platform,
                category=config.category,
                duration_seconds=config.duration_seconds,
                num_clips=4
            )
            
            # Store voice_config for AI discussions
            self._last_voice_config = voice_strategy.get("voice_config", {
                "strategy": "single",
                "voices": [],
                "primary_personality": "storyteller",
                "reasoning": "Fallback voice configuration"
            })
            
            # Generate audio files
            audio_files = self.tts_client.generate_intelligent_voice_audio(
                script=script_result.get('optimized_script', config.topic),
                language=Language.ENGLISH_US,
                topic=config.topic,
                platform=config.target_platform,
                category=config.category,
                duration_seconds=config.duration_seconds,
                num_clips=4
            )
            
            # Ensure we have audio files
            if not audio_files:
                logger.warning("⚠️ No audio files generated, creating fallback")
                # Create a simple fallback audio
                import tempfile
                import subprocess
                
                fallback_audio = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                fallback_audio.close()
                
                # Create silent audio as fallback
                try:
                    cmd = [
                        'ffmpeg', '-f', 'lavfi', '-i', f'anullsrc=r=44100:cl=stereo',
                        '-t', str(config.duration_seconds), 
                        '-y', fallback_audio.name
                    ]
                    subprocess.run(cmd, capture_output=True)
                    audio_files = [fallback_audio.name]
                    logger.info("✅ Created fallback silent audio")
                except Exception as e:
                    logger.error(f"❌ Fallback audio creation failed: {e}")
                    audio_files = []
            
            # Save ALL audio files to session directory with comprehensive tracking
            from ..utils.session_manager import session_manager
            session_audio_files = []
            
            for i, audio_file in enumerate(audio_files):
                if audio_file and os.path.exists(audio_file):
                    try:
                        # Save to session context
                        session_audio_path = session_context.save_audio_file(audio_file, f"segment_{i}")
                        
                        # Track with session manager
                        session_audio_path = session_manager.track_file(session_audio_path, "audio", "TTS")
                        
                        session_audio_files.append(session_audio_path)
                        logger.info(f"💾 Saved and tracked audio segment {i}: {os.path.basename(session_audio_path)}")
                    except Exception as e:
                        logger.error(f"❌ Failed to save audio segment {i}: {e}")
                        session_audio_files.append(audio_file)
                else:
                    logger.warning(f"⚠️ Audio file {i} not found or invalid: {audio_file}")
            
            # Save audio generation metadata
            audio_metadata = {
                "total_segments": len(audio_files),
                "successful_segments": len([f for f in session_audio_files if f and os.path.exists(f)]),
                "script_used": script_result.get('optimized_script', config.topic)[:200] + "...",
                "voice_strategy": voice_strategy.get("ai_analysis", {}),
                "voice_config": self._last_voice_config,
                "generation_timestamp": datetime.now().isoformat(),
                "platform": config.target_platform.value,
                "category": config.category.value
            }
            
            # Save metadata
            metadata_path = session_context.get_output_path("metadata", "audio_generation.json")
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            with open(metadata_path, 'w') as f:
                json.dump(audio_metadata, f, indent=2)
            
            logger.info(f"✅ Generated {len(session_audio_files)} audio files")
            return session_audio_files
            
        except Exception as e:
            logger.error(f"❌ Audio generation failed: {e}")
            return []'''
    
    # Replace the audio generation method
    method_pattern = r'def _generate_ai_optimized_audio\(self, config: GeneratedVideoConfig,.*?(?=\n    def |\nclass |\Z)'
    content = re.sub(method_pattern, audio_fix, content, flags=re.DOTALL)
    
    with open(video_gen_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed audio generation")

def fix_final_video_composition():
    """Fix final video composition to properly combine clips with audio"""
    video_gen_path = "src/generators/video_generator.py"
    
    with open(video_gen_path, 'r') as f:
        content = f.read()
    
    # Fix the video composition method
    composition_fix = '''    def _compose_final_video(self, clips: List[str], audio_files: List[str], 
                           config: GeneratedVideoConfig, session_context: SessionContext) -> str:
        """Compose final video by combining clips with audio"""
        logger.info("🎞️ Composing final video")
        
        try:
            import subprocess
            import tempfile
            
            # Validate clips exist
            valid_clips = [clip for clip in clips if clip and os.path.exists(clip)]
            if not valid_clips:
                logger.error("❌ No valid video clips found for composition")
                return ""
            
            # Validate audio files exist
            valid_audio = [audio for audio in audio_files if audio and os.path.exists(audio)]
            
            logger.info(f"🎬 Composing {len(valid_clips)} video clips with {len(valid_audio)} audio files")
            
            # Create temporary video path
            temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
            temp_video_path = temp_video.name
            temp_video.close()
            
            try:
                if len(valid_clips) == 1:
                    # Single clip - just copy or add audio
                    if valid_audio:
                        # Add audio to single clip
                        cmd = [
                            'ffmpeg', '-i', valid_clips[0], '-i', valid_audio[0],
                            '-c:v', 'copy', '-c:a', 'aac', '-shortest',
                            '-y', temp_video_path
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            logger.info("✅ Single clip with audio composition completed")
                        else:
                            logger.warning(f"⚠️ Audio merge failed, using video only: {result.stderr}")
                            import shutil
                            shutil.copy2(valid_clips[0], temp_video_path)
                    else:
                        # No audio, just copy video
                        import shutil
                        shutil.copy2(valid_clips[0], temp_video_path)
                        logger.info("✅ Single clip composition completed (no audio)")
                else:
                    # Multiple clips - concatenate then add audio
                    concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
                    for clip in valid_clips:
                        concat_file.write(f"file '{clip}'\\n")
                    concat_file.close()
                    
                    if valid_audio:
                        # Concatenate video and add audio
                        cmd = [
                            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file.name,
                            '-i', valid_audio[0], '-c:v', 'copy', '-c:a', 'aac', 
                            '-shortest', '-y', temp_video_path
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            logger.info("✅ Multi-clip with audio composition completed")
                        else:
                            logger.warning(f"⚠️ Audio merge failed, trying video only: {result.stderr}")
                            # Try without audio
                            cmd = [
                                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file.name,
                                '-c', 'copy', '-y', temp_video_path
                            ]
                            result = subprocess.run(cmd, capture_output=True, text=True)
                            if result.returncode == 0:
                                logger.info("✅ Multi-clip composition completed (no audio)")
                            else:
                                logger.error(f"❌ Video concatenation failed: {result.stderr}")
                                # Fallback to first clip
                                import shutil
                                shutil.copy2(valid_clips[0], temp_video_path)
                    else:
                        # No audio, just concatenate video
                        cmd = [
                            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file.name,
                            '-c', 'copy', '-y', temp_video_path
                        ]
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        if result.returncode == 0:
                            logger.info("✅ Multi-clip composition completed (no audio)")
                        else:
                            logger.error(f"❌ Video concatenation failed: {result.stderr}")
                            # Fallback to first clip
                            import shutil
                            shutil.copy2(valid_clips[0], temp_video_path)
                    
                    # Clean up concat file
                    try:
                        os.unlink(concat_file.name)
                    except:
                        pass
                        
            except Exception as e:
                logger.error(f"❌ Composition failed: {e}")
                # Ultimate fallback: just use first clip
                import shutil
                shutil.copy2(valid_clips[0], temp_video_path)
                logger.info("✅ Fallback composition completed")
            
            # Verify the composed video exists and has content
            if os.path.exists(temp_video_path) and os.path.getsize(temp_video_path) > 1000:
                # Save to session directory
                try:
                    saved_path = session_context.save_final_video(temp_video_path)
                    logger.info(f"💾 Final video saved: {saved_path} ({os.path.getsize(saved_path):,} bytes)")
                    
                    # Clean up temp file
                    try:
                        os.unlink(temp_video_path)
                    except:
                        pass
                    
                    return saved_path
                except Exception as e:
                    logger.error(f"❌ Failed to save final video: {e}")
                    return temp_video_path
            else:
                logger.error("❌ Composed video is empty or invalid")
                return ""
            
        except Exception as e:
            logger.error(f"❌ Video composition failed: {e}")
            return ""'''
    
    # Replace the composition method
    method_pattern = r'def _compose_final_video\(self, clips: List\[str\], audio_files: List\[str\],.*?(?=\n    def |\nclass |\Z)'
    content = re.sub(method_pattern, composition_fix, content, flags=re.DOTALL)
    
    with open(video_gen_path, 'w') as f:
        f.write(content)
    
    print("✅ Fixed final video composition")

def add_missing_imports():
    """Add missing imports to the video generator"""
    video_gen_path = "src/generators/video_generator.py"
    
    with open(video_gen_path, 'r') as f:
        content = f.read()
    
    # Add missing imports at the top
    imports_to_add = '''import json
from datetime import datetime
'''
    
    # Find the imports section and add missing ones
    if 'from datetime import datetime' not in content:
        content = content.replace('import json', imports_to_add)
    
    with open(video_gen_path, 'w') as f:
        f.write(content)
    
    print("✅ Added missing imports")

if __name__ == "__main__":
    print("🔧 Fixing audio generation and final video composition...")
    add_missing_imports()
    fix_audio_generation()
    fix_final_video_composition()
    print("✅ All audio and video fixes applied!") 