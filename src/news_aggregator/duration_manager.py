#!/usr/bin/env python3
"""
Duration Manager - Smart duration calculation for news clips
"""

import re
from typing import Dict, List, Optional, Union


class DurationManager:
    """Manages clip durations based on content type and complexity"""
    
    # Default durations in seconds
    DEFAULT_DURATIONS = {
        'breaking_news': 8,      # Breaking news needs more time
        'title_only': 3,         # Simple titles
        'title_with_subtitle': 5, # Title + description
        'complex_story': 7,      # Multiple elements
        'video_clip': 'original', # Use original video duration
        'image_simple': 4,       # Simple image with title
        'image_complex': 6,      # Image with lots of text
        'sports_score': 5,       # Sports scores need time to read
        'finance_data': 6,       # Financial data needs time
        'weather': 7,            # Weather forecasts
    }
    
    # Reading speed estimates (words per second)
    READING_SPEEDS = {
        'en': 3.5,  # English: ~3.5 words per second
        'he': 3.0,  # Hebrew: ~3 words per second (slightly slower due to RTL)
        'ar': 2.8,  # Arabic: ~2.8 words per second
        'es': 3.5,  # Spanish: ~3.5 words per second
    }
    
    # Minimum and maximum durations
    MIN_DURATION = 2
    MAX_DURATION = 15
    
    def __init__(self, default_duration: int = 5):
        """Initialize duration manager
        
        Args:
            default_duration: Default duration for clips in seconds
        """
        self.default_duration = default_duration
    
    def calculate_reading_time(self, text: str, language: str = 'en') -> float:
        """Calculate time needed to read text
        
        Args:
            text: Text to read
            language: Language code (en, he, ar, es, etc.)
            
        Returns:
            Time in seconds needed to read the text
        """
        # Count words (simple split by whitespace)
        word_count = len(text.split())
        
        # Get reading speed for language
        reading_speed = self.READING_SPEEDS.get(language, 3.0)
        
        # Calculate time (add 1 second buffer for processing)
        reading_time = (word_count / reading_speed) + 1
        
        return reading_time
    
    def analyze_content_complexity(self, content: Dict) -> str:
        """Analyze content complexity to determine type
        
        Args:
            content: Content dictionary with title, description, etc.
            
        Returns:
            Content type string
        """
        title = content.get('title', '')
        description = content.get('description', '')
        media_type = content.get('type', 'image')
        category = content.get('category', '')
        
        # Check for breaking news
        if any(word in title.lower() for word in ['breaking', 'urgent', 'alert', 'just in']):
            return 'breaking_news'
        
        # Check for sports scores
        if category == 'sports' or re.search(r'\d+\s*-\s*\d+', title):
            return 'sports_score'
        
        # Check for financial data
        if category == 'finance' or any(char in title for char in ['$', '€', '£', '%']):
            return 'finance_data'
        
        # Check for weather
        if category == 'weather' or any(word in title.lower() for word in ['weather', 'forecast', 'temperature']):
            return 'weather'
        
        # Video clips use original duration
        if media_type == 'video':
            return 'video_clip'
        
        # Analyze text complexity
        total_text = f"{title} {description}".strip()
        word_count = len(total_text.split())
        
        if word_count <= 10:
            return 'title_only'
        elif word_count <= 20:
            return 'image_simple' if media_type == 'image' else 'title_with_subtitle'
        else:
            return 'image_complex' if media_type == 'image' else 'complex_story'
    
    def get_duration(self, content: Dict, 
                    min_duration: Optional[int] = None,
                    max_duration: Optional[int] = None,
                    force_duration: Optional[int] = None) -> int:
        """Get optimal duration for content
        
        Args:
            content: Content dictionary
            min_duration: Minimum allowed duration
            max_duration: Maximum allowed duration  
            force_duration: Force specific duration (overrides calculation)
            
        Returns:
            Duration in seconds
        """
        # If forced duration is specified, use it
        if force_duration is not None:
            return max(self.MIN_DURATION, min(force_duration, self.MAX_DURATION))
        
        # Get content type
        content_type = self.analyze_content_complexity(content)
        
        # Get base duration
        base_duration = self.DEFAULT_DURATIONS.get(content_type, self.default_duration)
        
        # Handle video clips specially
        if base_duration == 'original':
            video_duration = content.get('duration', self.default_duration)
            base_duration = video_duration
        
        # Calculate reading time
        title = content.get('title', '')
        description = content.get('description', '')
        language = content.get('language', 'en')
        
        total_text = f"{title} {description}".strip()
        reading_time = self.calculate_reading_time(total_text, language)
        
        # Use the maximum of base duration and reading time
        calculated_duration = max(base_duration, reading_time)
        
        # Apply constraints
        min_dur = min_duration or self.MIN_DURATION
        max_dur = max_duration or self.MAX_DURATION
        
        final_duration = max(min_dur, min(calculated_duration, max_dur))
        
        return int(final_duration)
    
    def distribute_durations(self, content_items: List[Dict], 
                           total_duration: int,
                           min_clip_duration: int = 2,
                           max_clip_duration: int = 10) -> List[Dict]:
        """Distribute total duration across multiple clips
        
        Args:
            content_items: List of content items
            total_duration: Total duration to distribute (seconds)
            min_clip_duration: Minimum duration per clip
            max_clip_duration: Maximum duration per clip
            
        Returns:
            List of content items with 'duration' field added
        """
        if not content_items:
            return []
        
        # First pass: calculate ideal durations
        ideal_durations = []
        for item in content_items:
            ideal = self.get_duration(item, min_clip_duration, max_clip_duration)
            ideal_durations.append(ideal)
        
        # Calculate total ideal duration
        total_ideal = sum(ideal_durations)
        
        # If total ideal fits within total duration, use it
        if total_ideal <= total_duration:
            for i, item in enumerate(content_items):
                item['duration'] = ideal_durations[i]
            return content_items
        
        # Otherwise, scale proportionally
        scale_factor = total_duration / total_ideal
        
        # Apply scaling with constraints
        final_durations = []
        remaining_duration = total_duration
        
        for i, ideal in enumerate(ideal_durations):
            # Scale duration
            scaled = ideal * scale_factor
            
            # Apply constraints
            constrained = max(min_clip_duration, min(scaled, max_clip_duration))
            
            # Ensure we don't exceed remaining duration
            final = min(constrained, remaining_duration)
            
            final_durations.append(int(final))
            remaining_duration -= final
        
        # Distribute any remaining duration
        if remaining_duration > 0:
            # Add to clips that can take more time
            for i in range(len(final_durations)):
                if final_durations[i] < max_clip_duration and remaining_duration > 0:
                    add_time = min(max_clip_duration - final_durations[i], remaining_duration)
                    final_durations[i] += add_time
                    remaining_duration -= add_time
        
        # Apply durations to items
        for i, item in enumerate(content_items):
            item['duration'] = final_durations[i]
        
        return content_items


def create_duration_config(preset: str = 'default') -> Dict:
    """Create duration configuration presets
    
    Args:
        preset: Preset name (default, fast, slow, custom)
        
    Returns:
        Duration configuration dictionary
    """
    presets = {
        'default': {
            'min_duration': 3,
            'max_duration': 8,
            'default_duration': 5,
            'reading_speed_multiplier': 1.0
        },
        'fast': {
            'min_duration': 2,
            'max_duration': 5,
            'default_duration': 3,
            'reading_speed_multiplier': 1.3  # Assume faster reading
        },
        'slow': {
            'min_duration': 5,
            'max_duration': 12,
            'default_duration': 8,
            'reading_speed_multiplier': 0.7  # Slower reading
        },
        'breaking_news': {
            'min_duration': 5,
            'max_duration': 15,
            'default_duration': 8,
            'reading_speed_multiplier': 0.9
        },
        'social_media': {
            'min_duration': 2,
            'max_duration': 4,
            'default_duration': 3,
            'reading_speed_multiplier': 1.5  # Very fast for social
        }
    }
    
    return presets.get(preset, presets['default'])


if __name__ == "__main__":
    # Test the duration manager
    print("🕐 Testing Duration Manager...")
    print("=" * 50)
    
    manager = DurationManager()
    
    # Test cases
    test_content = [
        {
            'title': 'Breaking: Major earthquake hits California',
            'description': 'A 7.2 magnitude earthquake struck Southern California causing widespread damage',
            'type': 'image',
            'language': 'en'
        },
        {
            'title': 'מכבי תל אביב ניצחה 3-1',
            'description': '',
            'type': 'image',
            'language': 'he'
        },
        {
            'title': 'Stock Market Update',
            'description': 'Dow Jones up 2.5%, S&P 500 reaches new high at $4,500',
            'type': 'image',
            'category': 'finance'
        },
        {
            'title': 'Quick News',
            'type': 'image'
        },
        {
            'title': 'Video Report from the Scene',
            'type': 'video',
            'duration': 12
        }
    ]
    
    print("\n📊 Individual Duration Calculations:")
    for i, content in enumerate(test_content):
        duration = manager.get_duration(content)
        content_type = manager.analyze_content_complexity(content)
        print(f"\nContent {i+1}:")
        print(f"  Title: {content.get('title', 'N/A')}")
        print(f"  Type: {content_type}")
        print(f"  Duration: {duration} seconds")
    
    print("\n\n📈 Duration Distribution Test:")
    print("Distributing 60 seconds across 5 clips:")
    
    distributed = manager.distribute_durations(test_content.copy(), total_duration=60)
    
    total = 0
    for i, item in enumerate(distributed):
        print(f"  Clip {i+1}: {item['duration']} seconds - {item.get('title', 'N/A')[:30]}...")
        total += item['duration']
    
    print(f"\nTotal: {total} seconds")