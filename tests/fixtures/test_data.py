"""
Test Fixtures and Sample Data
"""

import os
from typing import Dict, Any, List

# Test API Key
TEST_API_KEY = os.getenv('GOOGLE_API_KEY', 'test_key_placeholder')

# Sample Topics
SAMPLE_TOPICS = [
    "Create engaging content about Hila Pinto's Ashtanga Yoga journey",
    "Amazing AI breakthrough in video generation",
    "Quick cooking tips for busy professionals",
    "Latest tech gadgets review",
    "Fitness motivation for beginners"
]

# Sample Configurations
SAMPLE_CONFIGS = {
    'basic': {
        'force_generation': 'auto',
        'frame_continuity': 'auto',
        'image_only': False,
        'fallback_only': False,
        'style': 'viral',
        'tone': 'engaging'
    },
    'advanced': {
        'force_generation': 'force_veo2',
        'frame_continuity': 'on',
        'image_only': False,
        'fallback_only': False,
        'style': 'professional',
        'tone': 'authoritative',
        'enable_trending': True,
        'trending_count': 5,
        'trending_hours': 24
    },
    'image_only': {
        'force_generation': 'force_image_gen',
        'frame_continuity': 'off',
        'image_only': True,
        'fallback_only': False,
        'style': 'dynamic',
        'tone': 'playful'
    }
}

# Sample Script Data
SAMPLE_SCRIPT_DATA = {
    'hook': {'text': 'Did you know this amazing fact?'},
    'segments': [
        {'text': 'First segment about the topic'},
        {'text': 'Second segment with more details'},
        {'text': 'Third segment with conclusion'}
    ],
    'call_to_action': 'Follow for more amazing content!'
}

# Sample Agent Decisions
SAMPLE_AGENT_DECISIONS = {
    'continuity': {
        'use_frame_continuity': True,
        'confidence': 0.8,
        'primary_reason': 'Content flows better with continuity'
    },
    'voice': {
        'voice_strategy': 'single_voice',
        'personality': 'narrator',
        'gender': 'female',
        'voiceover_style': 'professional'
    },
    'structure': {
        'segments': 4,
        'flow_type': 'linear',
        'engagement_points': [5, 15, 25]
    }
}

# Sample Trending Data
SAMPLE_TRENDING_DATA = [
    {
        'title': 'Viral Video 1',
        'views': 1500000,
        'engagement_rate': 0.08,
        'keywords': ['viral', 'trending', 'amazing'],
        'hook_type': 'question',
        'duration': 20,
        'platform': 'instagram'
    },
    {
        'title': 'Viral Video 2',
        'views': 2000000,
        'engagement_rate': 0.12,
        'keywords': ['incredible', 'must-see', 'shocking'],
        'hook_type': 'statement',
        'duration': 15,
        'platform': 'tiktok'
    }
]

# Expected Results Structure
EXPECTED_GENERATION_RESULT = {
    'success': True,
    'final_video_path': str,
    'session_id': str,
    'mode': str,
    'agent_decisions': dict,
    'agents_used': int,
    'optimization_level': str
}

# Platform Test Data
PLATFORM_TEST_DATA = {
    'instagram': {
        'max_duration': 60,
        'aspect_ratio': '9:16',
        'optimal_length': 25
    },
    'tiktok': {
        'max_duration': 60,
        'aspect_ratio': '9:16',
        'optimal_length': 15
    },
    'youtube': {
        'max_duration': 300,
        'aspect_ratio': '16:9',
        'optimal_length': 60
    },
    'twitter': {
        'max_duration': 140,
        'aspect_ratio': '16:9',
        'optimal_length': 30
    }
}

# Agent Test Data
AGENT_TEST_DATA = {
    'director': {
        'expected_methods': ['write_script'],
        'required_params': ['topic', 'style', 'duration', 'platform', 'category']
    },
    'voice_director': {
        'expected_methods': ['analyze_content_and_select_voices', 'select_optimal_voice'],
        'required_params': ['topic', 'script', 'language', 'platform', 'category']
    },
    'continuity_agent': {
        'expected_methods': ['analyze_frame_continuity_need', 'analyze_and_decide'],
        'required_params': ['topic', 'category', 'platform', 'duration']
    }
}

# UI Test Data
UI_TEST_DATA = {
    'form_inputs': {
        'mission': SAMPLE_TOPICS[0],
        'platform': 'instagram',
        'category': 'Educational',
        'duration': 25,
        'system': 'enhanced'
    },
    'advanced_options': {
        'force_generation': 'auto',
        'enable_trending': False,
        'trending_count': 10,
        'trending_hours': 24,
        'frame_continuity': 'auto'
    }
}

def get_test_topic(index: int = 0) -> str:
    """Get a test topic by index"""
    return SAMPLE_TOPICS[index % len(SAMPLE_TOPICS)]

def get_test_config(config_type: str = 'basic') -> Dict[str, Any]:
    """Get a test configuration"""
    return SAMPLE_CONFIGS.get(config_type, SAMPLE_CONFIGS['basic'])

def get_sample_script_data() -> Dict[str, Any]:
    """Get sample script data"""
    return SAMPLE_SCRIPT_DATA.copy()

def get_sample_agent_decisions() -> Dict[str, Any]:
    """Get sample agent decisions"""
    return SAMPLE_AGENT_DECISIONS.copy()

def get_sample_trending_data() -> List[Dict[str, Any]]:
    """Get sample trending data"""
    return SAMPLE_TRENDING_DATA.copy()

def validate_generation_result(result: Dict[str, Any]) -> bool:
    """Validate generation result structure"""
    required_keys = ['success', 'session_id', 'mode']
    return all(key in result for key in required_keys) 