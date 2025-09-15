"""
Laptop-Optimized Hollywood Pipeline
Resource-efficient 5-minute movie generation for local execution
"""

import os
import json
import logging
import asyncio
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import subprocess
import gc
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.generators.hollywood_veo_director import HollywoodVeoDirector, Scene, MovieScript, SceneType
from src.generators.gemini_scene_planner import GeminiScenePlanner, StoryArc
from src.generators.imagen4_continuity_engine import Imagen4ContinuityEngine, Imagen4Speed
from src.utils.session_context import SessionContext
from src.config.video_config import video_config

logger = logging.getLogger(__name__)


@dataclass
class LaptopOptimizationConfig:
    """Configuration for laptop-optimized generation"""
    
    # Resource management
    max_parallel_veo_calls: int = 2  # Limit parallel API calls
    veo_batch_size: int = 5  # Process scenes in small batches
    memory_cleanup_interval: int = 10  # Clean memory every N scenes
    
    # Quality vs Speed tradeoffs
    use_imagen4_fast: bool = True  # Use 10x faster Imagen 4
    veo_resolution: Tuple[int, int] = (1920, 1080)  # 1080p instead of 4K
    intermediate_quality: int = 85  # JPEG quality for intermediates
    
    # Caching
    enable_aggressive_caching: bool = True
    cache_references: bool = True
    reuse_similar_scenes: bool = True
    
    # API throttling
    api_delay_seconds: float = 1.0  # Delay between API calls
    max_retries: int = 3
    retry_delay: float = 5.0


class LaptopHollywoodPipeline:
    """
    Optimized Hollywood pipeline for laptop execution
    Implements smart batching, caching, and resource management
    """
    
    def __init__(self,
                 project_id: str = "viralgen-464411",
                 gcp_email: str = "admin@al-ai.net"):
        """
        Initialize laptop-optimized pipeline
        
        Args:
            project_id: GCP project ID
            gcp_email: GCP account email
        """
        self.project_id = project_id
        self.gcp_email = gcp_email
        self.config = LaptopOptimizationConfig()
        
        # Initialize session
        self.session = SessionContext.get_or_create_session()
        
        # Setup directories
        self.cache_dir = self.session.get_path("hollywood_cache")
        self.temp_dir = self.session.get_path("temp")
        self.output_dir = self.session.get_path("hollywood_output")
        
        for dir_path in [self.cache_dir, self.temp_dir, self.output_dir]:
            os.makedirs(dir_path, exist_ok=True)
        
        # Component initialization (lazy loading)
        self._veo_director = None
        self._scene_planner = None
        self._continuity_engine = None
        
        logger.info("💻 Laptop-optimized Hollywood pipeline initialized")
    
    async def setup_gcp_auth(self):
        """Setup GCP authentication"""
        try:
            # Check if already authenticated
            result = subprocess.run(
                ["gcloud", "config", "get-value", "account"],
                capture_output=True,
                text=True
            )
            
            if self.gcp_email not in result.stdout:
                logger.info(f"🔐 Setting up GCP auth for {self.gcp_email}")
                # Note: Password should be handled securely in production
                # This is just for demonstration
                subprocess.run([
                    "gcloud", "auth", "login", "--brief",
                    "--account", self.gcp_email
                ], check=False)
            
            # Set project
            subprocess.run([
                "gcloud", "config", "set", "project", self.project_id
            ], check=True)
            
            logger.info(f"✅ GCP authenticated as {self.gcp_email}")
            
        except Exception as e:
            logger.warning(f"GCP auth setup failed: {e}")
            logger.info("Using existing authentication")
    
    @property
    def veo_director(self):
        """Lazy load VEO director"""
        if not self._veo_director:
            self._veo_director = HollywoodVeoDirector(
                project_id=self.project_id,
                session_context=self.session
            )
        return self._veo_director
    
    @property
    def scene_planner(self):
        """Lazy load scene planner"""
        if not self._scene_planner:
            self._scene_planner = GeminiScenePlanner()
        return self._scene_planner
    
    @property
    def continuity_engine(self):
        """Lazy load continuity engine"""
        if not self._continuity_engine:
            self._continuity_engine = Imagen4ContinuityEngine(
                project_id=self.project_id,
                cache_dir=self.cache_dir
            )
        return self._continuity_engine
    
    async def generate_5_minute_movie(self,
                                     concept: str,
                                     genre: str = "drama",
                                     style: str = "cinematic",
                                     test_mode: bool = False) -> str:
        """
        Generate 5-minute Hollywood movie optimized for laptop
        
        Args:
            concept: Movie concept/story
            genre: Movie genre
            style: Visual style
            test_mode: Use minimal resources for testing
            
        Returns:
            Path to final movie file
        """
        
        logger.info(f"🎬 Generating 5-minute {genre} movie on laptop")
        logger.info(f"   Concept: {concept}")
        logger.info(f"   Optimization: Laptop mode enabled")
        
        start_time = time.time()
        
        try:
            # Step 1: Plan movie with Gemini (low resource)
            logger.info("📝 Planning movie structure...")
            movie_plan = await self._plan_movie_efficiently(
                concept, genre, style, test_mode
            )
            
            # Step 2: Generate character references (cached)
            logger.info("🎭 Creating character references...")
            character_refs = await self._generate_character_refs_cached(
                movie_plan, test_mode
            )
            
            # Step 3: Generate scenes in batches
            logger.info("🎥 Generating scenes in batches...")
            scene_clips = await self._generate_scenes_batched(
                movie_plan, character_refs, test_mode
            )
            
            # Step 4: Generate music (lightweight)
            logger.info("🎵 Creating soundtrack...")
            music_track = await self._generate_music_efficiently(
                movie_plan, test_mode
            )
            
            # Step 5: Assemble movie
            logger.info("🎞️ Assembling final movie...")
            final_movie = await self._assemble_movie_efficiently(
                scene_clips, music_track, movie_plan
            )
            
            elapsed = time.time() - start_time
            logger.info(f"✅ Movie completed in {elapsed/60:.1f} minutes")
            logger.info(f"📁 Output: {final_movie}")
            
            return final_movie
            
        except Exception as e:
            logger.error(f"Movie generation failed: {e}")
            raise
    
    async def _plan_movie_efficiently(self,
                                     concept: str,
                                     genre: str,
                                     style: str,
                                     test_mode: bool) -> MovieScript:
        """Plan movie with resource optimization"""
        
        if test_mode:
            # Use simplified planning for testing
            return self._create_test_movie_plan(concept, genre)
        
        # Check cache first
        cache_key = f"{concept}_{genre}_{style}".replace(" ", "_")
        cached_plan = self._load_cached_plan(cache_key)
        
        if cached_plan:
            logger.info("📚 Using cached movie plan")
            return cached_plan
        
        # Generate new plan
        blueprint = await self.scene_planner.plan_hollywood_movie(
            concept=concept,
            genre=genre,
            style=style,
            story_arc=StoryArc.THREE_ACT
        )
        
        # Convert to MovieScript format
        scenes = []
        for scene_plan in blueprint.scenes[:45]:  # Limit to 45 scenes
            scene = Scene(
                scene_id=scene_plan.scene_number,
                scene_type=self._map_scene_type(scene_plan),
                duration=scene_plan.duration,
                description=scene_plan.description,
                dialogue=scene_plan.dialogue_snippets[0] if scene_plan.dialogue_snippets else None,
                characters=scene_plan.characters_present,
                audio_cues=scene_plan.ambient_sounds
            )
            scenes.append(scene)
        
        movie_script = MovieScript(
            title=blueprint.title,
            genre=genre,
            total_duration=300.0,
            scenes=scenes,
            characters={"protagonist": blueprint.protagonist},
            music_style=blueprint.music_theme,
            target_emotion="dramatic"
        )
        
        # Cache the plan
        self._save_cached_plan(cache_key, movie_script)
        
        return movie_script
    
    def _create_test_movie_plan(self, concept: str, genre: str) -> MovieScript:
        """Create minimal test movie plan"""
        
        # Create just 10 scenes for testing (30 seconds)
        scenes = []
        for i in range(10):
            scene = Scene(
                scene_id=i,
                scene_type=self._get_test_scene_type(i),
                duration=3.0,  # 3 seconds each
                description=f"Test scene {i}: {concept}",
                characters=["TestCharacter"]
            )
            scenes.append(scene)
        
        return MovieScript(
            title="Test Movie",
            genre=genre,
            total_duration=30.0,
            scenes=scenes,
            characters={"TestCharacter": {"name": "Test"}},
            music_style="ambient",
            target_emotion="neutral"
        )
    
    async def _generate_character_refs_cached(self,
                                             movie_plan: MovieScript,
                                             test_mode: bool) -> Dict:
        """Generate character references with caching"""
        
        character_refs = {}
        
        for char_name, char_data in movie_plan.characters.items():
            # Check cache
            cache_path = os.path.join(self.cache_dir, f"char_{char_name}.jpg")
            
            if os.path.exists(cache_path) and self.config.cache_references:
                logger.info(f"📚 Using cached reference for {char_name}")
                character_refs[char_name] = cache_path
            else:
                # Generate new reference
                if not test_mode:
                    ref = await self.continuity_engine.create_character_reference(
                        character_id=char_name,
                        description=char_data.get("description", char_name),
                        speed=Imagen4Speed.FAST if self.config.use_imagen4_fast else Imagen4Speed.STANDARD
                    )
                    character_refs[char_name] = ref.image_path
                    
                    # Cache it
                    if self.config.cache_references:
                        subprocess.run([
                            "cp", ref.image_path, cache_path
                        ], check=False)
                else:
                    # Use placeholder in test mode
                    character_refs[char_name] = self._create_test_reference(char_name)
            
            # Add delay to avoid API throttling
            await asyncio.sleep(self.config.api_delay_seconds)
        
        return character_refs
    
    async def _generate_scenes_batched(self,
                                      movie_plan: MovieScript,
                                      character_refs: Dict,
                                      test_mode: bool) -> List[str]:
        """Generate scenes in efficient batches"""
        
        scene_clips = []
        batch_size = self.config.veo_batch_size
        
        # Process scenes in batches
        for batch_idx in range(0, len(movie_plan.scenes), batch_size):
            batch = movie_plan.scenes[batch_idx:batch_idx + batch_size]
            
            logger.info(f"🎬 Processing batch {batch_idx//batch_size + 1}/"
                       f"{len(movie_plan.scenes)//batch_size + 1}")
            
            # Generate batch with limited parallelism
            batch_clips = await self._generate_batch_parallel(
                batch, character_refs, test_mode
            )
            
            scene_clips.extend(batch_clips)
            
            # Memory cleanup
            if (batch_idx // batch_size) % self.config.memory_cleanup_interval == 0:
                self._cleanup_memory()
            
            # Progress save
            self._save_progress(scene_clips, batch_idx)
        
        return scene_clips
    
    async def _generate_batch_parallel(self,
                                      batch: List[Scene],
                                      character_refs: Dict,
                                      test_mode: bool) -> List[str]:
        """Generate batch with controlled parallelism"""
        
        clips = []
        
        # Use limited parallelism
        semaphore = asyncio.Semaphore(self.config.max_parallel_veo_calls)
        
        async def generate_with_limit(scene):
            async with semaphore:
                return await self._generate_single_scene(
                    scene, character_refs, test_mode
                )
        
        # Generate all scenes in batch
        tasks = [generate_with_limit(scene) for scene in batch]
        clips = await asyncio.gather(*tasks)
        
        return clips
    
    async def _generate_single_scene(self,
                                    scene: Scene,
                                    character_refs: Dict,
                                    test_mode: bool) -> str:
        """Generate single scene with optimization"""
        
        if test_mode:
            # Return placeholder clip
            return self._create_test_clip(scene.scene_id)
        
        # Check if similar scene exists in cache
        if self.config.reuse_similar_scenes:
            cached_clip = self._find_similar_cached_scene(scene)
            if cached_clip:
                logger.info(f"♻️ Reusing similar scene for {scene.scene_id}")
                return cached_clip
        
        try:
            # Generate with VEO
            clip_path = await self._generate_veo_clip_with_retry(
                scene, character_refs
            )
            
            # Cache the clip
            self._cache_scene_clip(scene, clip_path)
            
            return clip_path
            
        except Exception as e:
            logger.error(f"Scene {scene.scene_id} generation failed: {e}")
            # Return fallback clip
            return self._create_fallback_clip(scene)
    
    async def _generate_veo_clip_with_retry(self,
                                           scene: Scene,
                                           character_refs: Dict) -> str:
        """Generate VEO clip with retry logic"""
        
        for attempt in range(self.config.max_retries):
            try:
                # Add references to scene
                scene.reference_images = []
                for char in scene.characters:
                    if char in character_refs:
                        # Convert to proper reference format
                        from src.generators.enhanced_veo3_client import ReferenceImage, ReferenceType
                        ref = ReferenceImage(
                            image_path=character_refs[char],
                            reference_type=ReferenceType.ASSET
                        )
                        scene.reference_images.append(ref)
                
                # Generate with VEO using existing client
                clip_path = self.veo_director.veo_client.generate_video(
                    prompt=scene.veo_prompt,
                    duration=scene.duration,
                    clip_id=f"scene_{scene.scene_id}",
                    aspect_ratio="16:9"
                )
                
                if not clip_path:
                    raise Exception("VEO generation returned None")
                
                return clip_path
                
            except Exception as e:
                logger.warning(f"VEO attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    raise
    
    async def _generate_music_efficiently(self,
                                         movie_plan: MovieScript,
                                         test_mode: bool) -> str:
        """Generate music with resource optimization"""
        
        if test_mode:
            return self._create_test_music()
        
        # For now, create placeholder since Lyria 2 API is not yet public
        music_path = os.path.join(self.audio_dir, "soundtrack.mp3")
        
        # Generate silence or use royalty-free music
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"anullsrc=r=44100:cl=stereo:d={movie_plan.total_duration}",
            "-acodec", "mp3",
            music_path
        ], capture_output=True)
        
        logger.info("🎵 Created placeholder soundtrack")
        return music_path
    
    async def _assemble_movie_efficiently(self,
                                         scene_clips: List[str],
                                         music_track: str,
                                         movie_plan: MovieScript) -> str:
        """Assemble movie with resource optimization"""
        
        output_path = os.path.join(
            self.output_dir,
            f"{movie_plan.title.replace(' ', '_')}_5min.mp4"
        )
        
        # Create clip list file
        list_file = os.path.join(self.temp_dir, "clips.txt")
        with open(list_file, "w") as f:
            for clip in scene_clips:
                f.write(f"file '{clip}'\n")
        
        # Assemble with FFmpeg (resource-efficient settings)
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", list_file,
            "-i", music_track,
            "-c:v", "libx264",
            "-preset", "fast",  # Fast encoding for laptop
            "-crf", "23",  # Good quality/size balance
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            output_path
        ]
        
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.error(f"Assembly failed: {result.stderr}")
            raise RuntimeError("Movie assembly failed")
        
        # Cleanup temp files
        self._cleanup_temp_files()
        
        return output_path
    
    def _cleanup_memory(self):
        """Clean up memory periodically"""
        gc.collect()
        logger.info("🧹 Memory cleaned")
    
    def _save_progress(self, clips: List[str], batch_idx: int):
        """Save generation progress"""
        progress_file = os.path.join(self.cache_dir, "progress.json")
        progress = {
            "batch_idx": batch_idx,
            "clips_generated": len(clips),
            "clips": clips
        }
        with open(progress_file, "w") as f:
            json.dump(progress, f)
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            os.makedirs(self.temp_dir)
    
    def _load_cached_plan(self, cache_key: str) -> Optional[MovieScript]:
        """Load cached movie plan"""
        cache_file = os.path.join(self.cache_dir, f"plan_{cache_key}.json")
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                data = json.load(f)
                # Reconstruct MovieScript from data
                # (simplified for brevity)
                return None
        return None
    
    def _save_cached_plan(self, cache_key: str, plan: MovieScript):
        """Save movie plan to cache"""
        cache_file = os.path.join(self.cache_dir, f"plan_{cache_key}.json")
        # Serialize plan (simplified)
        with open(cache_file, "w") as f:
            json.dump({"title": plan.title}, f)
    
    def _find_similar_cached_scene(self, scene: Scene) -> Optional[str]:
        """Find similar cached scene"""
        # Implement similarity search in cache
        # (simplified for brevity)
        return None
    
    def _cache_scene_clip(self, scene: Scene, clip_path: str):
        """Cache generated scene clip"""
        cache_path = os.path.join(
            self.cache_dir,
            f"scene_{scene.scene_id}_{scene.scene_type.value}.mp4"
        )
        subprocess.run(["cp", clip_path, cache_path], check=False)
    
    def _create_test_clip(self, scene_id: int) -> str:
        """Create test clip for testing"""
        test_clip = os.path.join(self.temp_dir, f"test_clip_{scene_id}.mp4")
        
        # Create 3-second test clip
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=blue:s=1920x1080:d=3",
            "-vf", f"drawtext=text='Scene {scene_id}':fontsize=48:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            test_clip
        ], capture_output=True)
        
        return test_clip
    
    def _create_fallback_clip(self, scene: Scene) -> str:
        """Create fallback clip when generation fails"""
        fallback_clip = os.path.join(self.temp_dir, f"fallback_{scene.scene_id}.mp4")
        
        # Create simple colored clip with text
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c=gray:s=1920x1080:d={scene.duration}",
            "-vf", f"drawtext=text='{scene.description[:50]}':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2",
            fallback_clip
        ], capture_output=True)
        
        return fallback_clip
    
    def _create_test_reference(self, char_name: str) -> str:
        """Create test character reference"""
        test_ref = os.path.join(self.temp_dir, f"test_ref_{char_name}.jpg")
        
        # Create simple colored image
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "color=c=red:s=512x512:d=1",
            "-frames:v", "1",
            test_ref
        ], capture_output=True)
        
        return test_ref
    
    def _create_test_music(self) -> str:
        """Create test music track"""
        test_music = os.path.join(self.temp_dir, "test_music.mp3")
        
        # Create 30-second silence
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", "anullsrc=r=44100:cl=stereo:d=30",
            "-acodec", "mp3",
            test_music
        ], capture_output=True)
        
        return test_music
    
    def _map_scene_type(self, scene_plan) -> 'SceneType':
        """Map scene plan to scene type"""
        from src.generators.hollywood_veo_director import SceneType
        
        # Simple mapping based on emotional tone
        if "action" in scene_plan.description.lower():
            return SceneType.ACTION
        elif "dialogue" in scene_plan.description.lower():
            return SceneType.DIALOGUE
        elif "emotional" in scene_plan.emotional_tone.lower():
            return SceneType.EMOTIONAL
        else:
            return SceneType.ESTABLISHING
    
    def _get_test_scene_type(self, index: int) -> 'SceneType':
        """Get scene type for test scenes"""
        from src.generators.hollywood_veo_director import SceneType
        
        types = [SceneType.ESTABLISHING, SceneType.DIALOGUE, SceneType.ACTION]
        return types[index % len(types)]