"""
Patch for VideoGenerator to integrate theme system.
This shows the modifications needed to video_generator.py
"""

# Add these imports to the top of video_generator.py:
"""
from ..themes.managers.theme_manager import ThemeManager
from ..themes.services.theme_integration_service import ThemeIntegrationService
from ..themes.managers.series_manager import SeriesManager
"""

# Add this to the VideoGenerator.__init__ method:
"""
def __init__(self, config: GeneratedVideoConfig, **kwargs):
    # ... existing init code ...
    
    # Initialize theme system
    self.theme_manager = ThemeManager()
    self.theme_service = ThemeIntegrationService(self.theme_manager, self.session_context)
    self.series_manager = SeriesManager()
    
    # Load theme if specified
    self.theme = None
    if hasattr(config, 'theme_id') and config.theme_id:
        self.theme = self.theme_service.load_theme(config.theme_id)
        
    # Load series if specified
    self.series = None
    if hasattr(config, 'series_id') and config.series_id:
        self.series = self.series_manager.get_series(config.series_id)
"""

# Add this method to VideoGenerator class:
"""
def _apply_theme_to_frame(self, frame, frame_number, total_frames):
    '''Apply theme elements to video frame'''
    if not self.theme:
        return frame
        
    # Apply logo overlay
    frame = self.theme_service.apply_logo_overlay(
        frame, self.theme, frame_number, total_frames
    )
    
    # Apply lower thirds if needed (for specific frames)
    # This would be triggered based on script segments
    if self._should_show_lower_thirds(frame_number):
        frame = self.theme_service.apply_lower_thirds(
            frame,
            self.theme,
            text_primary=self._get_lower_thirds_text(frame_number),
            text_secondary=self._get_lower_thirds_secondary(frame_number),
            frame_number=frame_number
        )
        
    # Apply captions if enabled
    if self._has_caption_at_frame(frame_number):
        frame = self.theme_service.apply_caption_style(
            frame,
            self.theme,
            caption_text=self._get_caption_text(frame_number)
        )
        
    return frame
"""

# Modify the _combine_clips_with_audio method to include theme processing:
"""
def _combine_clips_with_audio(self, video_clips, audio_path, output_path):
    '''Combine video clips with audio and apply theme'''
    # ... existing code ...
    
    # If theme is loaded, process the final video
    if self.theme:
        # Create temporary output
        temp_output = output_path.replace('.mp4', '_temp.mp4')
        
        # Run existing combination to temp file
        # ... existing ffmpeg code outputs to temp_output ...
        
        # Apply intro/outro if available
        if self.theme.video_template:
            intro_applied = self.theme_service.apply_intro_outro(
                temp_output, self.theme, output_path
            )
            if intro_applied:
                os.remove(temp_output)
                return True
                
        # If no intro/outro, just rename temp to final
        os.rename(temp_output, output_path)
        
    # ... rest of existing code ...
"""

# Add series tracking to the generate method:
"""
def generate(self) -> VideoGenerationResult:
    '''Generate video with theme and series support'''
    # ... existing code ...
    
    try:
        # ... existing generation code ...
        
        # After successful generation, update series if applicable
        if self.series and hasattr(self.config, 'episode_title'):
            episode = self.series_manager.add_episode_to_series(
                series_id=self.series.id,
                title=self.config.episode_title,
                description=self.config.topic,
                session_id=self.config.session_id,
                video_path=output_path,
                duration=total_duration
            )
            
            # Save series metadata
            series_metadata = self.theme_service.create_series_metadata(
                self.theme,
                self.series.name,
                episode.episode_number,
                episode.title
            )
            
            metadata_path = self.session_context.get_output_path(
                "series_metadata.json", "metadata"
            )
            with open(metadata_path, 'w') as f:
                json.dump(series_metadata, f, indent=2)
                
        # ... rest of existing code ...
"""

# Example usage in main.py or workflow:
"""
# Create a news series
series = series_manager.create_series(
    name="Daily Tech News",
    theme_id="news-edition",
    description="Your daily dose of technology news",
    character_id="news-anchor-1",
    voice_id="professional-narrator"
)

# Generate episode
config = GeneratedVideoConfig(
    topic="Latest AI breakthroughs in 2025",
    theme_id="news-edition",
    series_id=series.id,
    episode_title="AI Revolution Continues",
    # ... other config ...
)

generator = VideoGenerator(config)
result = generator.generate()
"""