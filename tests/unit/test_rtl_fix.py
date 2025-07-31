#!/usr/bin/env python3
"""Test RTL text rendering to identify the root cause"""

import sys
sys.path.append('/Users/yahavzamari/viralAi')

# Test 1: Check if RTL libraries are properly installed
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    print("✅ RTL libraries installed correctly")
except ImportError as e:
    print(f"❌ RTL libraries missing: {e}")
    sys.exit(1)

# Test 2: Test RTL text processing
test_texts = [
    "זקן",  # Should display as ןקז (reversed)
    "היום, עם ישראל נולד",  # Full sentence
    "מתוך לב היער הקסום, נשר זקן הכריז"  # With punctuation
]

print("\n🔍 Testing RTL text processing:")
for text in test_texts:
    print(f"\nOriginal: {text}")
    print(f"Original hex: {' '.join(f'{ord(c):04x}' for c in text)}")
    
    # Apply reshaping
    reshaped = arabic_reshaper.reshape(text)
    print(f"Reshaped: {reshaped}")
    
    # Apply bidi algorithm
    display_text = get_display(reshaped)
    print(f"After bidi: {display_text}")
    print(f"After bidi hex: {' '.join(f'{ord(c):04x}' for c in display_text)}")

# Test 3: Check MoviePy rendering
from moviepy.editor import TextClip
import numpy as np

print("\n🎬 Testing MoviePy rendering:")
for text in test_texts:
    try:
        # Process text
        reshaped = arabic_reshaper.reshape(text)
        display_text = get_display(reshaped)
        
        # Create TextClip
        clip = TextClip(
            display_text,
            fontsize=50,
            color='white',
            font='Arial',
            method='caption',
            align='right',
            size=(800, 100)
        )
        
        # Get a frame
        frame = clip.get_frame(0)
        print(f"✅ Successfully created TextClip for: {text}")
        print(f"   Frame shape: {frame.shape}")
        
    except Exception as e:
        print(f"❌ Failed to create TextClip for '{text}': {e}")

print("\n🔤 Character-by-character analysis:")
text = "זקן יונש תנחור בעלטס"
print(f"Original: {text}")
for i, char in enumerate(text):
    print(f"  [{i}] '{char}' (U+{ord(char):04X})")

# Apply bidi
reshaped = arabic_reshaper.reshape(text)
display_text = get_display(reshaped)
print(f"\nAfter bidi: {display_text}")
for i, char in enumerate(display_text):
    print(f"  [{i}] '{char}' (U+{ord(char):04X})")