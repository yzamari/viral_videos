"""
Vertex AI Veo-3 Client
Supports Google Cloud project-based Veo-3 generation
"""

import os
import time
import logging
from typing import Optional, Dict, List
import google.generativeai as genai
from google.generativeai.types import File

logger = logging.getLogger(__name__)


class VertexVeo3Client:
    """Veo-3 client using Vertex AI project configuration"""
    
    def __init__(self, project_id: Optional[str] = None, location: str = "us-central1"):
        """
        Initialize Vertex AI Veo-3 client
        
        Args:
            project_id: Google Cloud project ID (or from env)
            location: Google Cloud location (default: us-central1)
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location
        
        if not self.project_id:
            raise ValueError("Project ID required. Set GOOGLE_CLOUD_PROJECT or pass project_id")
            
        # Configure with project
        try:
            genai.configure(
                project=self.project_id,
                location=self.location
            )
            logger.info(f"✅ Configured Vertex AI for project: {self.project_id}")
        except Exception as e:
            logger.error(f"Failed to configure Vertex AI: {e}")
            raise
            
        # Initialize Veo-3 model
        try:
            self.model = genai.GenerativeModel("veo-3.0-generate-preview")
            logger.info("✅ Veo-3 model initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Veo-3: {e}")
            raise
    
    def generate_video_to_gcs(self, prompt: str, output_gcs_uri: str, 
                             duration_seconds: int = 8, aspect_ratio: str = "16:9",
                             generate_audio: bool = True) -> Optional[str]:
        """
        Generate video directly to Google Cloud Storage
        
        Args:
            prompt: Video generation prompt
            output_gcs_uri: GCS URI like gs://bucket/path/video.mp4
            duration_seconds: Video duration (default: 8)
            aspect_ratio: Video aspect ratio (default: 16:9)
            generate_audio: Whether to generate audio (default: True)
            
        Returns:
            GCS URI of generated video or None if failed
        """
        try:
            logger.info(f"🎬 Starting Veo-3 generation to {output_gcs_uri}")
            logger.info(f"   Duration: {duration_seconds}s, Aspect: {aspect_ratio}")
            
            # Start generation
            generation_job = self.model.generate_content(
                [prompt, output_gcs_uri],
                generation_config={
                    "video_length_sec": duration_seconds,
                    "aspect_ratio": aspect_ratio,
                    "generate_audio": generate_audio,
                },
                stream=False,
            )
            
            logger.info(f"📡 Generation job started: {generation_job.operation.name}")
            
            # Poll for completion (with timeout)
            max_wait = 300  # 5 minutes
            poll_interval = 10
            elapsed = 0
            
            while elapsed < max_wait:
                try:
                    # Check if operation is complete
                    if hasattr(generation_job, 'operation') and generation_job.operation.done:
                        logger.info(f"✅ Veo-3 generation complete!")
                        return output_gcs_uri
                        
                except Exception as e:
                    logger.warning(f"Error checking status: {e}")
                
                time.sleep(poll_interval)
                elapsed += poll_interval
                logger.info(f"⏳ Waiting... ({elapsed}s/{max_wait}s)")
            
            logger.warning("⏰ Generation timed out")
            return None
            
        except Exception as e:
            logger.error(f"❌ Veo-3 generation failed: {e}")
            return None
    
    def generate_video_from_image(self, prompt: str, image_gcs_uri: str, 
                                 output_gcs_uri: str, duration_seconds: int = 5,
                                 aspect_ratio: str = "16:9", generate_audio: bool = True) -> Optional[str]:
        """
        Generate video from image using Veo-3
        
        Args:
            prompt: Animation instructions
            image_gcs_uri: Source image in GCS
            output_gcs_uri: Output video location in GCS
            duration_seconds: Video duration (default: 5)
            aspect_ratio: Video aspect ratio (default: 16:9)
            generate_audio: Whether to generate audio (default: True)
            
        Returns:
            GCS URI of generated video or None if failed
        """
        try:
            logger.info(f"🖼️ Starting Veo-3 image animation")
            logger.info(f"   Image: {image_gcs_uri}")
            logger.info(f"   Output: {output_gcs_uri}")
            
            # Start generation with image
            generation_job = self.model.generate_content(
                [prompt, File.from_uri(image_gcs_uri), output_gcs_uri],
                generation_config={
                    "video_length_sec": duration_seconds,
                    "aspect_ratio": aspect_ratio,
                    "generate_audio": generate_audio,
                },
                stream=False,
            )
            
            logger.info(f"📡 Image animation job started: {generation_job.operation.name}")
            
            # Poll for completion
            max_wait = 300
            poll_interval = 10
            elapsed = 0
            
            while elapsed < max_wait:
                try:
                    if hasattr(generation_job, 'operation') and generation_job.operation.done:
                        logger.info(f"✅ Image animation complete!")
                        return output_gcs_uri
                        
                except Exception as e:
                    logger.warning(f"Error checking status: {e}")
                
                time.sleep(poll_interval)
                elapsed += poll_interval
                logger.info(f"⏳ Waiting... ({elapsed}s/{max_wait}s)")
            
            logger.warning("⏰ Animation timed out")
            return None
            
        except Exception as e:
            logger.error(f"❌ Image animation failed: {e}")
            return None
    
    def download_from_gcs(self, gcs_uri: str, local_path: str) -> bool:
        """
        Download video from GCS to local file
        
        Args:
            gcs_uri: Source GCS URI
            local_path: Local destination path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            from google.cloud import storage
            
            # Parse GCS URI
            if not gcs_uri.startswith('gs://'):
                raise ValueError(f"Invalid GCS URI: {gcs_uri}")
                
            parts = gcs_uri[5:].split('/', 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid GCS URI format: {gcs_uri}")
                
            bucket_name, blob_name = parts
            
            # Download file
            client = storage.Client(project=self.project_id)
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            logger.info(f"📥 Downloading {gcs_uri} to {local_path}")
            blob.download_to_filename(local_path)
            
            if os.path.exists(local_path):
                size_mb = os.path.getsize(local_path) / (1024 * 1024)
                logger.info(f"✅ Downloaded successfully: {size_mb:.1f}MB")
                return True
            else:
                logger.error("Download failed - file not found")
                return False
                
        except Exception as e:
            logger.error(f"❌ GCS download failed: {e}")
            return False


def test_veo3_availability():
    """Test if Veo-3 is available with project configuration"""
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
    if not project_id:
        print("❌ GOOGLE_CLOUD_PROJECT not set")
        print("To use Veo-3, you need:")
        print("1. A Google Cloud project")
        print("2. Set GOOGLE_CLOUD_PROJECT=your-project-id")
        print("3. Enable Vertex AI API")
        print("4. Configure authentication")
        return False
        
    try:
        client = VertexVeo3Client(project_id)
        print(f"✅ Veo-3 client initialized for project: {project_id}")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize Veo-3: {e}")
        return False


if __name__ == "__main__":
    test_veo3_availability() 