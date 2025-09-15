from src.services.monitoring_service import MonitoringService
from src.services.file_service import FileService
import google.generativeai as genai
from config.config import settings
import json
import re
from src.config.ai_model_config import DEFAULT_AI_MODEL

class ScriptWriterAgent:
    def __init__(self, session_id):
        self.session_id = session_id
        self.monitoring_service = MonitoringService(self.session_id)
        self.file_service = FileService(self.session_id)
        self.gemini_model = None
        if settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)
            self.gemini_model = genai.GenerativeModel(DEFAULT_AI_MODEL)

    def write_script(self, trends, sentiment, style, duration=None):
        self.monitoring_service.log(
            f"ScriptWriterAgent: Writing script with sentiment '{sentiment}' and style '{style}'."
        )
        if duration:
            self.monitoring_service.log(f"ScriptWriterAgent: Target duration: {duration} seconds")

        topic = trends.get("topic", "general trends")
        youtube_trends = trends.get("youtube_trending")
        if self.gemini_model and youtube_trends:
            top_video = youtube_trends[0]
            video_title = top_video["snippet"]["title"]

            # Format duration constraint if provided
            duration_constraint = ""
            if duration:
                num_segments = 3  # Default to 3 scenes
                segment_duration = duration / num_segments
                duration_constraint = f"""
CRITICAL DURATION CONSTRAINT: The video MUST be exactly {duration} seconds.
- Each segment should be approximately {segment_duration:.1f} seconds
- Account for 300ms padding between segments
- Total content must fit within duration including pauses
- DO NOT generate content that exceeds the target duration
- IMPORTANT: Each scene description should be brief enough to be spoken in {segment_duration:.1f} seconds

"""
            
            prompt = f"""{duration_constraint}You are writing the actual movie script content for '{topic}'.
Write the EXACT words that will be spoken by the narrator or characters IN the movie itself.
DO NOT write descriptions ABOUT making a video - write the actual dialogue/narration FOR the movie.
The style should be '{style}' with a '{sentiment}' sentiment.
Draw inspiration from trending content like '{video_title}'.
Create 3 scenes with ACTUAL SPOKEN CONTENT that viewers will hear.

CRITICAL: Write as if you ARE the narrator speaking directly to the audience, not describing what a video should contain.

Examples of what TO write:
- "June 13, 2025 - Iranian drones cross into Israeli airspace..."  
- "This is the moment everything changed..."
- "Israel's defense systems activated immediately..."

Examples of what NOT to write:
- "A three-minute film depicts June 2025 Israel-Iran events..."
- "The video shows Iranian drones crossing..."
- "This scene features the defense systems..."

Provide the output in JSON format with a "title" and a list of "scenes", where each scene has a "scene" number and a "description" containing the ACTUAL SPOKEN WORDS."""
            try:
                response = self.gemini_model.generate_content(prompt)

                # Use regex to find the JSON object in the response
                json_match = re.search(r'\{.*\}', response.text, re.DOTALL)

                if json_match:
                    json_string = json_match.group(0)
                    script = json.loads(json_string)
                else:
                    self.monitoring_service.log(
                        "ScriptWriterAgent: No JSON object found in the response. Using fallback.")
                    script = self._get_fallback_script(topic, sentiment, style)

            except Exception as e:
                self.monitoring_service.log(f"ScriptWriterAgent: Error generating script with Gemini: {e}")
                script = self._get_fallback_script(topic, sentiment, style)
        else:
            script = self._get_fallback_script(topic, sentiment, style)

        # Ensure script is a dictionary
        if isinstance(script, str):
            try:
                script = json.loads(script)
            except (json.JSONDecodeError, ValueError) as e:
                self.monitoring_service.log(f"ScriptWriterAgent: Failed to parse script from string: {e}. Using fallback.")
                script = self._get_fallback_script(topic, sentiment, style)

        self.file_service.save_json("script.json", script)
        self.monitoring_service.log("ScriptWriterAgent: Script writing complete.")
        return script

    def _get_fallback_script(self, topic, sentiment, style):
        return {
            "title": f"{style.capitalize()} {sentiment.capitalize()} Video about {topic}",
            "scenes": [
                {"scene": 1, "description": "Opening scene introducing the topic."},
                {"scene": 2, "description": "Middle scene developing the story."},
                {"scene": 3, "description": "Closing scene with a call to action."},
            ],
        }