#!/usr/bin/env python3
"""
Quick Fix for Gemini Image Generation Issues

The issue is that the Gemini image generation is using incorrect response modalities.
The error shows: "The requested combination of response modalities is not supported"
"""

import os
import sys
import re

def fix_gemini_image_client():
    """Fix the Gemini image client response modalities issue"""
    
    client_path = 'src/generators/gemini_image_client.py'
    
    if not os.path.exists(client_path):
        print(f"❌ File not found: {client_path}")
        return False
    
    print(f"🔧 Fixing Gemini image client: {client_path}")
    
    # Read the file
    with open(client_path, 'r') as f:
        content = f.read()
    
    # The issue is likely in the response configuration
    # Look for response modalities configuration
    
    # Common fixes for Gemini image generation
    fixes = [
        # Fix 1: Remove incorrect response modalities
        (r'response_modalities=\[.*?\]', ''),
        
        # Fix 2: Use correct image generation parameters
        (r'model\.generate_content\(.*?response_modalities.*?\)', 
         'model.generate_content(prompt, generation_config=generation_config)'),
        
        # Fix 3: Fix the generation config
        (r'generation_config=.*?response_modalities.*?\)', 
         'generation_config=genai.GenerationConfig(temperature=0.7, top_p=0.8, max_output_tokens=1024)'),
    ]
    
    # Apply fixes
    fixed_content = content
    fixes_applied = 0
    
    for pattern, replacement in fixes:
        if re.search(pattern, fixed_content, re.DOTALL):
            fixed_content = re.sub(pattern, replacement, fixed_content, flags=re.DOTALL)
            fixes_applied += 1
            print(f"   ✅ Applied fix: {pattern[:50]}...")
    
    # Additional specific fix for the error we saw
    if 'response_modalities' in fixed_content:
        # Remove all response_modalities references
        fixed_content = re.sub(r',\s*response_modalities=[^,)]*', '', fixed_content)
        fixed_content = re.sub(r'response_modalities=[^,)]*,?\s*', '', fixed_content)
        fixes_applied += 1
        print("   ✅ Removed response_modalities references")
    
    # Write the fixed content back
    if fixes_applied > 0:
        # Create backup
        backup_path = f"{client_path}.backup"
        with open(backup_path, 'w') as f:
            f.write(content)
        print(f"   📁 Backup created: {backup_path}")
        
        # Write fixed content
        with open(client_path, 'w') as f:
            f.write(fixed_content)
        
        print(f"   ✅ Applied {fixes_applied} fixes to {client_path}")
        return True
    else:
        print("   ℹ️ No fixes needed or pattern not found")
        return False

def test_gemini_image_generation():
    """Test if Gemini image generation works after fix"""
    
    print("\n🧪 Testing Gemini image generation...")
    
    try:
        # Import and test
        from src.generators.gemini_image_client import GeminiImageClient
        
        # Test initialization
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ No GOOGLE_API_KEY found")
            return False
        
        client = GeminiImageClient(api_key, 'outputs')
        print("✅ Client initialized successfully")
        
        # Test simple image generation
        test_prompts = [{
            'description': 'A simple test image',
            'veo2_prompt': 'A cute cartoon cat'
        }]
        
        config = {
            'duration_seconds': 3,
            'images_per_second': 2
        }
        
        print("🎨 Testing image generation...")
        result = client.generate_image_based_clips(test_prompts, config, 'test_fix')
        
        if result and len(result) > 0:
            print("✅ Image generation test successful!")
            print(f"   Generated: {result[0].get('clip_path', 'Unknown path')}")
            return True
        else:
            print("❌ Image generation test failed - no results")
            return False
            
    except Exception as e:
        print(f"❌ Image generation test failed: {e}")
        return False

def main():
    """Main fix routine"""
    print("🔧 Gemini Image Generation Quick Fix")
    print("=" * 40)
    
    # 1. Fix the client
    print("\n1. Fixing Gemini image client...")
    fix_success = fix_gemini_image_client()
    
    if fix_success:
        print("✅ Gemini image client fixed")
    else:
        print("⚠️ No fixes applied - may already be correct")
    
    # 2. Test the fix
    print("\n2. Testing the fix...")
    test_success = test_gemini_image_generation()
    
    if test_success:
        print("✅ Gemini image generation is now working!")
    else:
        print("❌ Gemini image generation still has issues")
        print("   This may require manual inspection of the code")
    
    # 3. Summary
    print("\n📊 SUMMARY:")
    print("=" * 15)
    print(f"   Client Fix: {'✅ SUCCESS' if fix_success else '⚠️ NO CHANGES'}")
    print(f"   Test Result: {'✅ WORKING' if test_success else '❌ STILL BROKEN'}")
    
    if test_success:
        print("\n🎉 Gemini image generation should now work as fallback!")
        print("   VEO-2 quota issues will now fall back to working image generation")
    else:
        print("\n🔧 Manual fix may be needed:")
        print("   1. Check src/generators/gemini_image_client.py")
        print("   2. Remove any response_modalities parameters")
        print("   3. Use standard Gemini image generation API")
    
    return 0 if test_success else 1

if __name__ == "__main__":
    exit(main()) 