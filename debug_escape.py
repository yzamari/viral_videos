#!/usr/bin/env python3
"""Debug FFmpeg escaping"""

def _escape_text_for_ffmpeg(text: str) -> str:
    """Escape text for FFmpeg drawtext filter - step by step debug"""
    if not text or not text.strip():
        return "Text"
    
    escaped = text
    print(f"Step 0 - Start: {repr(escaped)}")
    
    # Replace apostrophes with safe alternative or escape them
    escaped = escaped.replace("'", "\\'")
    print(f"Step 1 - After apostrophe: {repr(escaped)}")
    
    escaped = escaped.replace("'", "\\'")  # Unicode apostrophe
    print(f"Step 2 - After unicode apostrophe 1: {repr(escaped)}")
    
    escaped = escaped.replace("'", "\\'")  # Another Unicode apostrophe
    print(f"Step 3 - After unicode apostrophe 2: {repr(escaped)}")
    
    return escaped.strip() or "Text"

if __name__ == "__main__":
    test_text = "Here's what you need"
    print(f"Original input: {repr(test_text)}")
    print(f"Character by character: {[c for c in test_text]}")
    
    result = _escape_text_for_ffmpeg(test_text)
    print(f"Final output: {repr(result)}")
    print(f"Character by character: {[c for c in result]}")
    apostrophe_char = "'"
    print(f"Contains apostrophe: {apostrophe_char in result}")
    
    # Let's test if this would actually work in FFmpeg
    # The correct FFmpeg escaping should be: Here\'s what you need
    print("Expected for FFmpeg: Here\\'s what you need")