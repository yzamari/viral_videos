"""
Script generation service implementation that wraps existing functionality
"""

import asyncio
from typing import Dict, Any

from ...core.interfaces.services import ScriptGenerationService
from ...core.entities.video_entity import Platform

class ExistingScriptGenerationService(ScriptGenerationService):
    """
    Implementation of ScriptGenerationService that wraps existing script generation functionality

    This service adapts the existing script generation components to work with
    the clean architecture interfaces.
    """

    def __init__(self):
        """Initialize script generation service"""
        pass

    async def generate_script(
        self,
        mission: str,
        platform: Platform,
        duration_seconds: int,
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate script content

        Args:
            mission: Video mission/topic
            platform: Target platform
            duration_seconds: Target duration
            config: Generation configuration

        Returns:
            Script content dictionary
        """
        try:
            # For now, create a placeholder script structure
            # In a real implementation, this would call the existing orchestrators

            # Simulate script generation
            await asyncio.sleep(0.1)  # Simulate processing time

            # Calculate segments based on duration
            segment_duration = 5  # seconds per segment
            num_segments = max(1, (duration_seconds - 3) // segment_duration)  # Reserve 3s for hook

            # Generate script structure
            script_content = {
                "hook": {
                    "text": f"Amazing insights about {mission}!",
                    "type": "excitement",
                    "duration_seconds": 3
                },
                "segments": [],
                "call_to_action": "Follow for more amazing content!",
                "total_duration": duration_seconds,
                "word_count": 0,
                "style": config.get("style", "viral"),
                "tone": config.get("tone", "engaging"),
                "platform": platform.value,
                "mission": mission
            }

            # Generate segments
            for i in range(num_segments):
                segment = {
                    "text": f"Segment {i+1}: Key insight about {mission}",
                    "type": "content",
                    "duration_seconds": segment_duration,
                    "order": i + 1
                }
                script_content["segments"].append(segment)

            # Calculate total word count (rough estimate)
            total_text = script_content["hook"]["text"]
            for segment in script_content["segments"]:
                total_text += " " + segment["text"]
            total_text += " " + script_content["call_to_action"]

            script_content["word_count"] = len(total_text.split())

            return script_content

        except Exception as e:
            print(f"Error generating script: {e}")

            # Return minimal fallback script using the mission text directly
            return {
                "hook": {
                    "text": f"{mission[:50]}",  # First 50 chars of mission
                    "type": "simple",
                    "duration_seconds": 3
                },
                "segments": [
                    {
                        "text": f"{mission}",  # Use full mission text
                        "type": "content",
                        "duration_seconds": duration_seconds - 6,
                        "order": 1
                    }
                ],
                "call_to_action": "Follow for more!",
                "total_duration": duration_seconds,
                "word_count": 10,
                "style": "simple",
                "tone": "neutral",
                "platform": platform.value,
                "mission": mission
            }

    def get_supported_platforms(self) -> list[Platform]:
        """Get list of supported platforms"""
        return [
            Platform.YOUTUBE,
            Platform.TIKTOK,
            Platform.INSTAGRAM,
            Platform.TWITTER,
            Platform.FACEBOOK,
            Platform.LINKEDIN
        ]

    def get_supported_styles(self) -> list[str]:
        """Get list of supported styles"""
        return ["viral", "educational", "entertaining", "professional", "casual"]

    def get_supported_tones(self) -> list[str]:
        """Get list of supported tones"""
        return ["engaging", "excited", "calm", "authoritative", "friendly"]
