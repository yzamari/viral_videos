#!/usr/bin/env python3
"""
Test VEO-3 Fast Configuration
"""
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.veo_client_factory import VeoClientFactory, VeoModel
from config.config import Settings

def test_veo3_fast_config():
    """Test VEO-3 Fast configuration"""
    print("\n🔍 Testing VEO-3 Fast Configuration\n")
    
    # Check settings
    settings = Settings()
    print("📋 Current Settings:")
    print(f"   disable_veo3: {settings.disable_veo3}")
    print(f"   prefer_veo3_fast: {settings.prefer_veo3_fast}")
    print(f"   veo_model_preference_order: {settings.veo_model_preference_order}")
    
    # Check VeoModel enum
    print(f"\n📦 VEO Model Enum Values:")
    for model in VeoModel:
        print(f"   {model.name}: {model.value}")
    
    # Test factory preference order
    factory = VeoClientFactory()
    print(f"\n🏭 Factory Configuration:")
    print(f"   Project: {factory.project_id}")
    print(f"   Location: {factory.location}")
    print(f"   GCS Bucket: {factory.gcs_bucket}")
    
    # Parse model preference order
    model_order = settings.veo_model_preference_order.lower().split(',')
    model_order = [m.strip() for m in model_order]
    print(f"\n🎯 Model Preference Order: {model_order}")
    
    # Check if VEO-3 Fast is first in preference
    if model_order[0] == 'veo3-fast':
        print("\n✅ VEO-3 Fast is correctly set as the preferred model!")
    else:
        print(f"\n⚠️  VEO-3 Fast is not the preferred model. Current preference: {model_order[0]}")
    
    return True

if __name__ == "__main__":
    test_veo3_fast_config()