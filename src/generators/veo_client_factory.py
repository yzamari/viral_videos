#!/usr/bin/env python3
"""
VEO Client Factory - Factory pattern for creating VEO clients
"""

import os
import sys
from typing import Dict, Optional, List, Union
from enum import Enum

# Add src to path for imports
if 'src' not in sys.path:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from src.utils.logging_config import get_logger
except ImportError:
    from utils.logging_config import get_logger

logger = get_logger(__name__)


class VeoModel(Enum):
    """Available VEO models"""
    VEO2 = "veo-2.0-generate-001"
    VEO3 = "veo-3.0-generate-preview"


class VeoClientFactory:
    """Factory for creating and managing VEO clients"""
    
    def __init__(self, project_id: Optional[str] = None, location: Optional[str] = None, gcs_bucket: Optional[str] = None):
        self.project_id = project_id or os.getenv('VERTEX_AI_PROJECT_ID', 'viralgen-464411')
        self.location = location or os.getenv('VERTEX_AI_LOCATION', 'us-central1')
        self.gcs_bucket = gcs_bucket or os.getenv('VERTEX_AI_GCS_BUCKET', 'viral-veo2-results')
        self._clients: Dict[str, any] = {}
        
        logger.info(f"🏭 VEO Client Factory initialized")
        logger.info(f"   Project: {self.project_id}")
        logger.info(f"   Location: {self.location}")
        logger.info(f"   GCS Bucket: {self.gcs_bucket}")
    
    def create_client(self, model: Union[VeoModel, str], output_dir: str):
        """Create VEO client for specified model"""
        # Convert string to enum if needed
        if isinstance(model, str):
            try:
                model = VeoModel(model)
            except ValueError:
                model_name = model.upper().replace('-', '').replace('.', '')
                if model_name in ['VEO2', 'VEO20']:
                    model = VeoModel.VEO2
                elif model_name in ['VEO3', 'VEO30']:
                    model = VeoModel.VEO3
                else:
                    raise ValueError(f"Unsupported VEO model: {model}")
        
        # Create cache key
        cache_key = f"{model.value}_{output_dir}"
        
        # Return cached client if available
        if cache_key in self._clients:
            client = self._clients[cache_key]
            if hasattr(client, 'is_available') and client.is_available:
                return client
            else:
                del self._clients[cache_key]
        
        # Create new client
        if model == VeoModel.VEO2:
            try:
                from src.generators.vertex_ai_veo2_client import VertexAIVeo2Client
            except ImportError:
                from generators.vertex_ai_veo2_client import VertexAIVeo2Client
            
            client = VertexAIVeo2Client(
                project_id=self.project_id,
                location=self.location,
                gcs_bucket=self.gcs_bucket,
                output_dir=output_dir
            )
        elif model == VeoModel.VEO3:
            try:
                from src.generators.vertex_veo3_client import VertexAIVeo3Client
            except ImportError:
                from generators.vertex_veo3_client import VertexAIVeo3Client
            
            client = VertexAIVeo3Client(
                project_id=self.project_id,
                location=self.location,
                gcs_bucket=self.gcs_bucket,
                output_dir=output_dir
            )
        else:
            raise ValueError(f"Unsupported VEO model: {model}")
        
        # Cache client if available
        if hasattr(client, 'is_available') and client.is_available:
            self._clients[cache_key] = client
        
        return client
    
    def get_veo_client(self, model: Union[VeoModel, str], output_dir: str):
        """Get VEO client for specified model (alias for create_client)"""
        return self.create_client(model, output_dir)
    
    def get_best_available_client(self, output_dir: str, prefer_veo3: bool = True):
        """Get the best available VEO client"""
        try:
            if prefer_veo3:
                veo3_client = self.create_client(VeoModel.VEO3, output_dir)
                if hasattr(veo3_client, 'is_available') and veo3_client.is_available:
                    logger.info("🚀 Using VEO-3 (preferred)")
                    return veo3_client
            
            veo2_client = self.create_client(VeoModel.VEO2, output_dir)
            if hasattr(veo2_client, 'is_available') and veo2_client.is_available:
                logger.info("🎬 Using VEO-2")
                return veo2_client
            
            logger.warning("❌ No VEO models available")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to create VEO client: {e}")
            return None
    
    def get_available_models(self) -> List[VeoModel]:
        """Get list of available VEO models"""
        available_models = []
        
        # Test VEO-2
        try:
            veo2_client = self.create_client(VeoModel.VEO2, "/tmp")
            if hasattr(veo2_client, 'is_available') and veo2_client.is_available:
                available_models.append(VeoModel.VEO2)
        except Exception as e:
            logger.debug(f"VEO-2 not available: {e}")
        
        # Test VEO-3
        try:
            veo3_client = self.create_client(VeoModel.VEO3, "/tmp")
            if hasattr(veo3_client, 'is_available') and veo3_client.is_available:
                available_models.append(VeoModel.VEO3)
        except Exception as e:
            logger.debug(f"VEO-3 not available: {e}")
        
        return available_models


# Global factory instance
veo_factory = VeoClientFactory()


def get_veo_client(model: Union[VeoModel, str], output_dir: str):
    """Convenience function to get VEO client"""
    return veo_factory.create_client(model, output_dir)


def get_best_veo_client(output_dir: str, prefer_veo3: bool = True):
    """Convenience function to get best available VEO client"""
    return veo_factory.get_best_available_client(output_dir, prefer_veo3) 