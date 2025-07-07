#!/usr/bin/env python3
"""
Test Enhanced Image Generation
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.generators.video_generator import VideoGenerator
from PIL import Image

def test_enhanced_placeholders():
    """Test the enhanced placeholder generation"""
    
    # Create a video generator instance
    api_key = os.getenv("GEMINI_API_KEY", "test-key")
    generator = VideoGenerator(api_key, output_dir="test_images")
    
    # Test different styles
    test_cases = [
        {
            "prompt": "B2 stealth bomber flying over desert at sunset",
            "expected_style": "military",
            "filename": "b2_bomber"
        },
        {
            "prompt": "Desert landscape in Iran with mountains",
            "expected_style": "desert", 
            "filename": "iran_desert"
        },
        {
            "prompt": "Advanced AI technology circuit board",
            "expected_style": "tech",
            "filename": "tech_circuit"
        },
        {
            "prompt": "Beautiful abstract art with flowing colors",
            "expected_style": "default",
            "filename": "abstract_art"
        }
    ]
    
    print("🎨 Testing Enhanced Image Generation")
    print("=" * 50)
    
    os.makedirs("test_images", exist_ok=True)
    
    for test in test_cases:
        print(f"\n📸 Generating: {test['prompt']}")
        print(f"   Expected style: {test['expected_style']}")
        
        output_path = f"test_images/{test['filename']}.jpg"
        
        # Generate the image
        success = generator._create_sophisticated_placeholder(
            test['prompt'], 
            output_path
        )
        
        if success and os.path.exists(output_path):
            # Check image properties
            img = Image.open(output_path)
            print(f"   ✅ Generated: {img.size[0]}x{img.size[1]} {img.mode}")
            print(f"   📁 Saved to: {output_path}")
            
            # Calculate file size
            file_size = os.path.getsize(output_path) / 1024
            print(f"   💾 Size: {file_size:.1f} KB")
        else:
            print(f"   ❌ Failed to generate image")
    
    print("\n" + "=" * 50)
    print("✅ Test complete! Check the 'test_images' folder for results.")
    
    # Test Vertex AI if configured
    if os.getenv("ENABLE_VERTEX_AI_IMAGEN", "false").lower() == "true":
        print("\n🎨 Testing Vertex AI Imagen...")
        
        try:
            from src.generators.vertex_imagen_client import VertexImagenClient
            
            imagen = VertexImagenClient()
            if imagen.test_connection():
                print("✅ Vertex AI Imagen is available!")
                
                # Generate a test image
                result = imagen.generate_image(
                    prompt="A photorealistic B2 stealth bomber flying over desert",
                    output_path="test_images/vertex_ai_test.jpg"
                )
                
                if result:
                    print(f"✅ Generated real AI image: {result}")
                else:
                    print("❌ Failed to generate with Vertex AI")
            else:
                print("❌ Vertex AI Imagen connection failed")
                
        except Exception as e:
            print(f"❌ Vertex AI test failed: {e}")
    else:
        print("\n💡 Tip: Set ENABLE_VERTEX_AI_IMAGEN=true to test real AI image generation")

if __name__ == "__main__":
    test_enhanced_placeholders() 