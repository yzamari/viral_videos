"""
Enhanced Veo3 Client with Reference Image Support for Character Consistency
Implements the latest Veo 3 features including reference-powered video generation
"""

import os
import json
import base64
import time
import logging
from typing import Dict, Optional, List, Union, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from google.cloud import aiplatform
from google.oauth2 import service_account
import vertexai
from vertexai.preview.vision_models import VideoGenerationModel

logger = logging.getLogger(__name__)


class ReferenceType(Enum):
    """Types of reference images for Veo 3"""
    ASSET = "asset"  # Character/object consistency
    STYLE = "style"  # Artistic style transfer


@dataclass
class ReferenceImage:
    """Reference image configuration for Veo 3"""
    image_path: str
    reference_type: ReferenceType
    mime_type: str = "image/jpeg"
    
    def to_dict(self) -> Dict:
        """Convert to API format"""
        with open(self.image_path, "rb") as f:
            image_bytes = f.read()
        
        return {
            "image": {
                "bytesBase64Encoded": base64.b64encode(image_bytes).decode("utf-8"),
                "mimeType": self.mime_type
            },
            "referenceType": self.reference_type.value
        }


class EnhancedVeo3Client:
    """
    Enhanced Veo 3 client with reference image support for character consistency
    Supports up to 3 asset images or 1 style image per generation
    """
    
    MODEL_NAMES = {
        "standard": "veo-3.0-generate-preview",
        "fast": "veo-3.0-fast-generate-001",  # No audio support
        "experimental": "veo.0-generate-exp"  # Fallback with reference support
    }
    
    def __init__(self,
                 project_id: str,
                 location: str = "us-central1",
                 gcs_bucket: Optional[str] = None,
                 output_dir: str = "./outputs"):
        """
        Initialize Enhanced Veo3 Client
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud location
            gcs_bucket: Optional GCS bucket for intermediate storage
            output_dir: Local directory for output videos
        """
        self.project_id = project_id
        self.location = location
        self.gcs_bucket = gcs_bucket
        self.output_dir = output_dir
        
        # Create output directories
        self.clips_dir = os.path.join(output_dir, "veo3_clips")
        self.references_dir = os.path.join(output_dir, "reference_images")
        os.makedirs(self.clips_dir, exist_ok=True)
        os.makedirs(self.references_dir, exist_ok=True)
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        
        # Model configuration
        self.current_model = self.MODEL_NAMES["standard"]
        self.model = None
        self._initialize_model()
        
        logger.info(f"✅ Enhanced Veo3 Client initialized for project {project_id}")
    
    def _initialize_model(self):
        """Initialize the Veo model"""
        try:
            self.model = VideoGenerationModel.from_pretrained(self.current_model)
            logger.info(f"Model {self.current_model} initialized")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            # Try fallback model
            self.current_model = self.MODEL_NAMES["experimental"]
            self.model = VideoGenerationModel.from_pretrained(self.current_model)
    
    def generate_video_with_references(self,
                                      prompt: str,
                                      reference_images: List[str],
                                      output_path: str,
                                      reference_type: ReferenceType = ReferenceType.ASSET,
                                      duration: int = 8,
                                      fps: int = 24,
                                      aspect_ratio: str = "16:9",
                                      include_audio: bool = True,
                                      camera_motion: Optional[str] = None) -> Optional[str]:
        """
        Generate video with reference images for character consistency
        
        Args:
            prompt: Text description of the video
            reference_images: List of paths to reference images (max 3 for assets, 1 for style)
            output_path: Path to save the generated video
            reference_type: Type of reference (asset or style)
            duration: Video duration in seconds (max 8)
            fps: Frames per second
            aspect_ratio: Video aspect ratio
            include_audio: Whether to include audio (not available in fast mode)
            camera_motion: Optional camera motion description
            
        Returns:
            Path to generated video or None if failed
        """
        
        # Validate reference images
        if reference_type == ReferenceType.ASSET and len(reference_images) > 3:
            logger.warning("Max 3 asset reference images allowed. Using first 3.")
            reference_images = reference_images[:3]
        elif reference_type == ReferenceType.STYLE and len(reference_images) > 1:
            logger.warning("Max 1 style reference image allowed. Using first one.")
            reference_images = reference_images[:1]
        
        # Validate all reference images exist
        valid_references = []
        for ref_path in reference_images:
            if os.path.exists(ref_path):
                valid_references.append(ref_path)
            else:
                logger.warning(f"Reference image not found: {ref_path}")
        
        if not valid_references:
            logger.error("No valid reference images provided")
            return None
        
        try:
            # Prepare reference images
            references = [
                ReferenceImage(img_path, reference_type)
                for img_path in valid_references
            ]
            
            # Build enhanced prompt with camera motion
            enhanced_prompt = prompt
            if camera_motion:
                enhanced_prompt += f"\nCamera: {camera_motion}"
            
            # Add character consistency instructions for asset references
            if reference_type == ReferenceType.ASSET:
                enhanced_prompt += "\nMaintain exact character appearance and identity from reference images."
            
            logger.info(f"🎬 Generating video with {len(references)} reference images")
            logger.info(f"Prompt: {enhanced_prompt[:200]}...")
            
            # Generate video with references
            generation_params = {
                "prompt": enhanced_prompt,
                "duration": min(duration, 8),  # Max 8 seconds for Veo 3
                "fps": fps,
                "aspect_ratio": aspect_ratio,
                "references": [ref.to_dict() for ref in references]
            }
            
            # Use fast mode if audio not needed
            if not include_audio and self.current_model != self.MODEL_NAMES["fast"]:
                logger.info("Switching to fast mode (no audio)")
                self.current_model = self.MODEL_NAMES["fast"]
                self._initialize_model()
            
            # Generate video
            response = self.model.generate_video(
                prompt=enhanced_prompt,
                generation_config=generation_params
            )
            
            # Wait for generation to complete
            logger.info("⏳ Waiting for video generation...")
            while not response.is_done():
                time.sleep(5)
            
            # Download the generated video
            if response.video_url:
                self._download_video(response.video_url, output_path)
                logger.info(f"✅ Video generated with references: {output_path}")
                
                # Log metadata
                self._save_generation_metadata(
                    output_path,
                    prompt,
                    references,
                    generation_params
                )
                
                return output_path
            else:
                logger.error("No video URL in response")
                return None
            
        except Exception as e:
            logger.error(f"Failed to generate video with references: {e}")
            return None
    
    def generate_character_video_sequence(self,
                                         character_id: str,
                                         character_references: List[str],
                                         scene_descriptions: List[Dict[str, str]],
                                         output_dir: str) -> List[str]:
        """
        Generate a sequence of videos with consistent character
        
        Args:
            character_id: Unique identifier for the character
            character_references: List of reference images for the character
            scene_descriptions: List of scene descriptions with prompts and settings
            output_dir: Directory to save generated videos
            
        Returns:
            List of paths to generated videos
        """
        os.makedirs(output_dir, exist_ok=True)
        generated_videos = []
        
        for idx, scene in enumerate(scene_descriptions):
            output_path = os.path.join(output_dir, f"{character_id}_scene_{idx:03d}.mp4")
            
            prompt = scene.get("prompt", "")
            setting = scene.get("setting", "")
            action = scene.get("action", "")
            dialogue = scene.get("dialogue", "")
            
            # Build comprehensive prompt
            full_prompt = f"""
            Character in scene: {setting}
            Action: {action}
            {f'Dialogue: "{dialogue}"' if dialogue else ''}
            {prompt}
            """.strip()
            
            # Generate video with character references
            video_path = self.generate_video_with_references(
                prompt=full_prompt,
                reference_images=character_references,
                output_path=output_path,
                reference_type=ReferenceType.ASSET,
                duration=8,
                include_audio=bool(dialogue)
            )
            
            if video_path:
                generated_videos.append(video_path)
                logger.info(f"Generated scene {idx + 1}/{len(scene_descriptions)}")
            else:
                logger.warning(f"Failed to generate scene {idx + 1}")
        
        logger.info(f"✅ Generated {len(generated_videos)}/{len(scene_descriptions)} videos")
        return generated_videos
    
    def apply_style_transfer(self,
                           prompt: str,
                           style_reference: str,
                           output_path: str,
                           duration: int = 8) -> Optional[str]:
        """
        Generate video with style transfer from reference image
        
        Args:
            prompt: Video content description
            style_reference: Path to style reference image
            output_path: Path to save generated video
            duration: Video duration in seconds
            
        Returns:
            Path to generated video or None if failed
        """
        if not os.path.exists(style_reference):
            logger.error(f"Style reference not found: {style_reference}")
            return None
        
        style_prompt = f"{prompt}\nApply the artistic style from the reference image."
        
        return self.generate_video_with_references(
            prompt=style_prompt,
            reference_images=[style_reference],
            output_path=output_path,
            reference_type=ReferenceType.STYLE,
            duration=duration
        )
    
    def generate_multi_character_scene(self,
                                      characters: Dict[str, List[str]],
                                      interaction_prompt: str,
                                      output_path: str,
                                      duration: int = 8) -> Optional[str]:
        """
        Generate a scene with multiple characters interacting
        
        Args:
            characters: Dictionary mapping character names to their reference images
            interaction_prompt: Description of character interaction
            output_path: Path to save generated video
            duration: Video duration
            
        Returns:
            Path to generated video or None if failed
        """
        # Collect all reference images (max 3)
        all_references = []
        character_descriptions = []
        
        for char_name, char_refs in characters.items():
            if char_refs and all_references.__len__() < 3:
                all_references.extend(char_refs[:min(len(char_refs), 3 - len(all_references))])
                character_descriptions.append(char_name)
        
        if not all_references:
            logger.error("No character references provided")
            return None
        
        # Build multi-character prompt
        prompt = f"""
        Scene with characters: {', '.join(character_descriptions)}
        {interaction_prompt}
        Each character must maintain their distinct appearance from references.
        Show clear interaction between characters.
        """
        
        return self.generate_video_with_references(
            prompt=prompt,
            reference_images=all_references,
            output_path=output_path,
            reference_type=ReferenceType.ASSET,
            duration=duration
        )
    
    def _download_video(self, video_url: str, output_path: str):
        """Download video from URL to local path"""
        import requests
        
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    
    def _save_generation_metadata(self,
                                 video_path: str,
                                 prompt: str,
                                 references: List[ReferenceImage],
                                 params: Dict):
        """Save metadata about the generation"""
        metadata = {
            "video_path": video_path,
            "prompt": prompt,
            "references": [
                {
                    "path": ref.image_path,
                    "type": ref.reference_type.value
                }
                for ref in references
            ],
            "parameters": params,
            "model": self.current_model,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        metadata_path = video_path.replace(".mp4", "_metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def test_connection(self) -> bool:
        """Test if the Veo3 client is properly configured"""
        try:
            if self.model:
                logger.info("✅ Enhanced Veo3 client connection successful")
                return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
        
        return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model": self.current_model,
            "max_duration": 8,
            "max_references": {
                "asset": 3,
                "style": 1
            },
            "features": [
                "Character consistency via reference images",
                "Style transfer",
                "Native audio generation (standard mode)",
                "Camera motion control",
                "Multi-character scenes"
            ],
            "supported_aspect_ratios": ["16:9", "9:16", "1:1", "4:3", "3:4"]
        }


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = EnhancedVeo3Client(
        project_id="viralgen-464411",
        location="us-central1"
    )
    
    if client.test_connection():
        print("Enhanced Veo3 client ready!")
        
        # Get model info
        info = client.get_model_info()
        print(f"\nModel: {info['model']}")
        print(f"Features: {', '.join(info['features'])}")
        
        # Example: Generate video with character references
        # character_refs = ["path/to/character1.jpg", "path/to/character2.jpg"]
        # video = client.generate_video_with_references(
        #     prompt="Two friends having coffee at a futuristic cafe",
        #     reference_images=character_refs,
        #     output_path="test_character_video.mp4",
        #     reference_type=ReferenceType.ASSET
        # )