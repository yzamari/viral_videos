"""
Vertex AI Imagen Client for Real AI Image Generation
"""
import os
import logging
from typing import Optional, List
import tempfile

logger = logging.getLogger(__name__)

class VertexImagenClient:
    """Client for generating images using Google's Imagen through Vertex AI"""

    def __init__(self, project_id: str = None, location: str = "us-central1"):
        """Initialize Vertex AI Imagen client"""
        self.initialized = False
        self.model = None

        try:
            # Import Vertex AI libraries
            # Suppress deprecation warnings for now - we'll need to migrate to new SDK
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore", category=UserWarning, module="vertexai")
                from google.cloud import aiplatform
                from vertexai.preview.vision_models import ImageGenerationModel

            # Get project ID from multiple sources
            self.project_id = (
                project_id or 
                os.getenv("VERTEX_AI_PROJECT_ID") or 
                os.getenv("GOOGLE_CLOUD_PROJECT") or
                self._get_gcloud_project()
            )
            self.location = location or os.getenv("VERTEX_AI_LOCATION", "us-central1")

            if not self.project_id:
                logger.warning("No Vertex AI project ID provided. Please set GOOGLE_CLOUD_PROJECT or run 'gcloud config set project PROJECT_ID'")
                return

            # Initialize Vertex AI
            aiplatform.init(
                project=self.project_id,
                location=self.location
            )

            # Load Imagen model - use Imagen 3 Fast for cost efficiency ($0.02 per image)
            # TODO: Migrate to new Generative AI SDK before June 2025
            try:
                # Try Imagen 3 Fast first
                self.model = ImageGenerationModel.from_pretrained("imagen-3-fast")
                logger.info("✅ Using Imagen 3 Fast model ($0.02 per image)")
            except Exception:
                # Fallback to imagegeneration@002 if Imagen 3 Fast not available
                self.model = ImageGenerationModel.from_pretrained("imagegeneration@002")
                logger.info("✅ Using Imagen 2 model (fallback)")
            self.initialized = True

            logger.info(f"✅ Vertex AI Imagen initialized for project: {self.project_id}")

        except ImportError:
            logger.warning("Vertex AI libraries not installed. Run: pip install google-cloud-aiplatform")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI Imagen: {e}")

    def generate_image(self, prompt: str, output_path: str,
                       aspect_ratio: str = "16:9",
                       number_of_images: int = 1) -> Optional[str]:
        """Generate an image using Imagen"""

        if not self.initialized or not self.model:
            logger.warning("Vertex AI Imagen not initialized")
            return None

        try:
            logger.info(f"🎨 Generating image with Imagen: {prompt[:50]}...")

            # Generate images with appropriate safety settings
            response = self.model.generate_images(
                prompt=prompt,
                number_of_images=number_of_images,
                aspect_ratio=aspect_ratio,
                # Use default safety settings - block_some causes issues
                person_generation="allow_adult"
            )

            if response and response.images:
                # Save the first image
                image = response.images[0]

                # Save to specified path
                image.save(output_path)

                logger.info(f"✅ Successfully generated image: {output_path}")
                return output_path
            else:
                logger.warning("Imagen returned no images")
                return None

        except Exception as e:
            logger.error(f"Imagen generation failed: {e}")
            return None

    def generate_scene_progression(self, base_prompt: str, num_images: int,
                                   output_dir: str) -> List[str]:
        """Generate a coherent sequence of images for video scenes"""

        if not self.initialized:
            return []

        image_paths = []

        # Define scene progression types
        progressions = [
            "establishing wide shot",
            "medium shot approaching",
            "close-up detail shot",
            "dynamic action shot",
            "dramatic angle shot",
            "concluding wide shot"
        ]

        for i in range(num_images):
            try:
                # Create scene-specific prompt
                progression_idx = i % len(progressions)
                scene_prompt = f"{base_prompt}, {progressions[progression_idx]}, cinematic quality, 16:9 aspect ratio"

                # Add variety to avoid repetition
                if i > 0:
                    scene_prompt += f", continuation from previous scene, slight variation {i + 1}"

                output_path = os.path.join(output_dir, f"imagen_{i:03d}.jpg")

                result = self.generate_image(
                    prompt=scene_prompt,
                    output_path=output_path,
                    aspect_ratio="16:9"
                )

                if result:
                    image_paths.append(result)
                else:
                    logger.warning(f"Failed to generate image {i + 1}/{num_images}")

            except Exception as e:
                logger.error(f"Error generating image {i + 1}: {e}")

        return image_paths

    def test_connection(self) -> bool:
        """Test if Imagen is accessible"""

        if not self.initialized:
            return False

        try:
            # Try a simple generation with safe prompt
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                result = self.generate_image(
                    prompt="A simple geometric blue square on white background, minimalist design",
                    output_path=tmp.name
                )

                # Clean up test file
                if result and os.path.exists(tmp.name):
                    os.unlink(tmp.name)

                return result is not None

        except Exception as e:
            logger.error(f"Imagen connection test failed: {e}")
            return False
    
    def _get_gcloud_project(self) -> Optional[str]:
        """Get project ID from gcloud config"""
        try:
            import subprocess
            result = subprocess.run(
                ['gcloud', 'config', 'get', 'project'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            logger.debug(f"Could not get gcloud project: {e}")
        return None
