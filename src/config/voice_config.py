"""
Voice Configuration
Centralized configuration for voice IDs and settings across different providers
"""

from typing import Dict, Any

# ElevenLabs Voice Configuration
ELEVENLABS_VOICES = {
    "emotions": {
        "excited": {
            "id": "EXAVITQu4vr4xnSDxMaL",
            "name": "Bella",
            "description": "Energetic and enthusiastic voice"
        },
        "serious": {
            "id": "21m00Tcm4TlvDq8ikWAM",
            "name": "Rachel",
            "description": "Professional and authoritative voice"
        },
        "playful": {
            "id": "yoZ06aMxZJJ28mfd3POQ",
            "name": "Sam",
            "description": "Fun and friendly voice"
        },
        "calm": {
            "id": "MF3mGyEYCl7XYWbV9V6O",
            "name": "Emily",
            "description": "Soothing and peaceful voice"
        },
        "mysterious": {
            "id": "TxGEqnHWrfWFTfGW9XjX",
            "name": "Josh",
            "description": "Deep and intriguing voice"
        },
        "urgent": {
            "id": "VR6AewLTigWG4xSOukaG",
            "name": "Arnold",
            "description": "Fast-paced and urgent voice"
        },
        "inspirational": {
            "id": "pNInz6obpgDQGcFmaJgB",
            "name": "Adam",
            "description": "Motivational and uplifting voice"
        }
    },
    "default": "21m00Tcm4TlvDq8ikWAM"  # Rachel - professional
}

# OpenAI Voice Configuration
OPENAI_VOICES = {
    "emotions": {
        "excited": "nova",       # Energetic female
        "serious": "onyx",       # Deep male
        "playful": "shimmer",    # Fun female
        "calm": "echo",          # Soothing male
        "mysterious": "fable",   # British male
        "urgent": "alloy",       # Neutral fast
        "inspirational": "nova"  # Clear female
    },
    "default": "nova"
}

# Google TTS Voice Configuration
GOOGLE_TTS_VOICES = {
    "languages": {
        "en-US": {
            "male": ["en-US-Neural2-A", "en-US-Neural2-D", "en-US-Neural2-I", "en-US-Neural2-J"],
            "female": ["en-US-Neural2-C", "en-US-Neural2-E", "en-US-Neural2-F", "en-US-Neural2-G", "en-US-Neural2-H"],
            "default": "en-US-Neural2-C"
        },
        "en-GB": {
            "male": ["en-GB-Neural2-B", "en-GB-Neural2-D"],
            "female": ["en-GB-Neural2-A", "en-GB-Neural2-C", "en-GB-Neural2-F"],
            "default": "en-GB-Neural2-A"
        },
        "es-ES": {
            "male": ["es-ES-Neural2-B", "es-ES-Neural2-F"],
            "female": ["es-ES-Neural2-A", "es-ES-Neural2-C", "es-ES-Neural2-D", "es-ES-Neural2-E"],
            "default": "es-ES-Neural2-A"
        },
        "fr-FR": {
            "male": ["fr-FR-Neural2-B", "fr-FR-Neural2-D"],
            "female": ["fr-FR-Neural2-A", "fr-FR-Neural2-C", "fr-FR-Neural2-E"],
            "default": "fr-FR-Neural2-A"
        },
        "de-DE": {
            "male": ["de-DE-Neural2-B", "de-DE-Neural2-D"],
            "female": ["de-DE-Neural2-A", "de-DE-Neural2-C", "de-DE-Neural2-F"],
            "default": "de-DE-Neural2-A"
        },
        "it-IT": {
            "male": ["it-IT-Neural2-C"],
            "female": ["it-IT-Neural2-A"],
            "default": "it-IT-Neural2-A"
        },
        "pt-BR": {
            "male": ["pt-BR-Neural2-B"],
            "female": ["pt-BR-Neural2-A", "pt-BR-Neural2-C"],
            "default": "pt-BR-Neural2-A"
        },
        "ru-RU": {
            "male": ["ru-RU-Neural2-B"],
            "female": ["ru-RU-Neural2-A"],
            "default": "ru-RU-Neural2-A"
        },
        "ja-JP": {
            "male": ["ja-JP-Neural2-C", "ja-JP-Neural2-D"],
            "female": ["ja-JP-Neural2-A", "ja-JP-Neural2-B"],
            "default": "ja-JP-Neural2-A"
        },
        "ko-KR": {
            "male": ["ko-KR-Neural2-C"],
            "female": ["ko-KR-Neural2-A", "ko-KR-Neural2-B"],
            "default": "ko-KR-Neural2-A"
        },
        "zh-CN": {
            "male": ["zh-CN-Neural2-B", "zh-CN-Neural2-C"],
            "female": ["zh-CN-Neural2-A", "zh-CN-Neural2-D", "zh-CN-Neural2-F"],
            "default": "zh-CN-Neural2-A"
        },
        "ar-XA": {
            "male": ["ar-XA-Neural2-B", "ar-XA-Neural2-C"],
            "female": ["ar-XA-Neural2-A", "ar-XA-Neural2-D"],
            "default": "ar-XA-Neural2-A"
        },
        "he-IL": {
            "male": ["he-IL-Standard-B", "he-IL-Standard-D"],
            "female": ["he-IL-Standard-A", "he-IL-Standard-C"],
            "default": "he-IL-Standard-A"
        },
        "fa-IR": {
            "male": ["fa-IR-Standard-B"],
            "female": ["fa-IR-Standard-A"],
            "default": "fa-IR-Standard-A"
        },
        "th-TH": {
            "female": ["th-TH-Neural2-A"],
            "default": "th-TH-Neural2-A"
        }
    }
}

# Voice Provider Settings
VOICE_SETTINGS = {
    "elevenlabs": {
        "stability": 0.5,
        "similarity_boost": 0.5,
        "style": 0.0,
        "use_speaker_boost": True
    },
    "openai": {
        "speed": 1.0,
        "temperature": 0.7
    },
    "google_tts": {
        "speaking_rate": 1.0,
        "pitch": 0.0,
        "volume_gain_db": 0.0
    }
}

# Voice selection priorities
VOICE_PROVIDER_PRIORITY = [
    "google_tts",    # Default provider
    "elevenlabs",    # Premium provider
    "openai"         # Alternative provider
]

# Voice emotion mappings
EMOTION_MAPPINGS = {
    "happy": "excited",
    "sad": "calm",
    "angry": "urgent",
    "fearful": "mysterious",
    "neutral": "serious",
    "surprised": "playful",
    "disgusted": "serious"
}

def get_voice_id(provider: str, emotion: str = None, language: str = "en-US", gender: str = None) -> str:
    """
    Get voice ID for a specific provider and configuration
    
    Args:
        provider: Voice provider (elevenlabs, openai, google_tts)
        emotion: Desired emotion (optional)
        language: Language code (for Google TTS)
        gender: Voice gender (for Google TTS)
    
    Returns:
        Voice ID string
    """
    if provider == "elevenlabs":
        if emotion and emotion in ELEVENLABS_VOICES["emotions"]:
            return ELEVENLABS_VOICES["emotions"][emotion]["id"]
        return ELEVENLABS_VOICES["default"]
    
    elif provider == "openai":
        if emotion and emotion in OPENAI_VOICES["emotions"]:
            return OPENAI_VOICES["emotions"][emotion]
        return OPENAI_VOICES["default"]
    
    elif provider == "google_tts":
        if language in GOOGLE_TTS_VOICES["languages"]:
            lang_voices = GOOGLE_TTS_VOICES["languages"][language]
            if gender and gender in lang_voices:
                return lang_voices[gender][0]  # Return first voice of that gender
            return lang_voices["default"]
        # Fallback to English
        return GOOGLE_TTS_VOICES["languages"]["en-US"]["default"]
    
    return None

def get_voice_settings(provider: str) -> Dict[str, Any]:
    """Get provider-specific voice settings"""
    return VOICE_SETTINGS.get(provider, {})