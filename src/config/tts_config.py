# TTS Configuration
# Centralized configuration for Text-to-Speech parameters

class TTSConfig:
    """Configuration for TTS (Text-to-Speech) parameters."""
    
    # Speech rate configuration
    # Based on empirical testing with Google TTS
    WORDS_PER_SECOND = 2.8  # More accurate than the previous 2.5
    
    # Speed limits for TTS
    MIN_SPEED = 0.75
    MAX_SPEED = 1.1  # Cap at 1.1x for better quality
    DEFAULT_SPEED = 1.0
    
    # Duration calculation parameters
    MIN_WORDS_PER_SECOND = 2.7
    MAX_WORDS_PER_SECOND = 2.9
    
    @classmethod
    def calculate_duration(cls, word_count: int) -> float:
        """Calculate expected duration for given word count."""
        return word_count / cls.WORDS_PER_SECOND
    
    @classmethod
    def calculate_word_count(cls, duration: float) -> int:
        """Calculate required word count for target duration."""
        return int(duration * cls.WORDS_PER_SECOND)
    
    @classmethod
    def get_target_word_range(cls, duration: float) -> tuple[int, int]:
        """Get min and max word count for target duration."""
        min_words = int(duration * cls.MIN_WORDS_PER_SECOND)
        max_words = int(duration * cls.MAX_WORDS_PER_SECOND)
        return min_words, max_words

# Global instance
tts_config = TTSConfig()