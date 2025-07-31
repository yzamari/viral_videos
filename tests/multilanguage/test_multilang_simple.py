#!/usr/bin/env python3
"""
Simple test to isolate the multi-language generation issue
"""
import os
import sys
import asyncio

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.models.video_models import Language

def test_simple_multilang():
    """Test with a simple script"""
    print("🧪 Testing simple multi-language generation...")
    
    # Simple test without API calls - just check the configuration
    languages = ['en-US', 'he', 'fa']
    
    # Test the language conversion from the workflow
    try:
        language_enums = []
        lang_mapping = {
            'en': Language.ENGLISH_US,
            'en-US': Language.ENGLISH_US,
            'he': Language.HEBREW,
            'ar': Language.ARABIC,
            'fa': Language.PERSIAN,
        }
        
        for lang_str in languages:
            if lang_str in lang_mapping:
                language_enums.append(lang_mapping[lang_str])
                print(f"✅ Mapped {lang_str} -> {lang_mapping[lang_str].value}")
            else:
                print(f"❌ Failed to map {lang_str}")
                
        print(f"📋 Final language list: {[lang.value for lang in language_enums]}")
        
        # Test RTL detection
        rtl_languages = {Language.ARABIC, Language.PERSIAN, Language.HEBREW}
        rtl_detected = [lang for lang in language_enums if lang in rtl_languages]
        
        if rtl_detected:
            print(f"📜 RTL languages detected: {[lang.value for lang in rtl_detected]}")
        else:
            print("📝 No RTL languages detected")
            
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_simple_multilang()
    if success:
        print("🎉 Simple test completed successfully")
    else:
        print("💥 Simple test failed")