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

    def write_script(self, trends, sentiment, style):
        self.monitoring_service.log(
            f"ScriptWriterAgent: Writing script with sentiment '{sentiment}' and style '{style}'."
        )

        topic = trends.get("topic", "general trends")
        youtube_trends = trends.get("youtube_trending")
        if self.gemini_model and youtube_trends:
            top_video = youtube_trends[0]
            video_title = top_video["snippet"]["title"]

            prompt = """
            Create a script for a short viral video about '{topic}'.
            The video should be in a '{style}' style with a '{sentiment}' sentiment.
            The script should be inspired by the a trending YouTube video titled '{video_title}'.
            The script should have 3 scenes.
            Provide the output in JSON format with a "title" and a list of "scenes", where each scene has a "scene" number and a "description".
            """
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
                script = eval(script)
            except BaseException:
                self.monitoring_service.log("ScriptWriterAgent: Failed to parse script from string. Using fallback.")
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