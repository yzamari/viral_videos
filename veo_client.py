import os
import time
import json
import requests
from typing import Optional
import google.auth
import google.auth.transport.requests

# --- Configuration ---
# Replace these with your actual project and bucket details.
# It's recommended to set these as environment variables for better security.
PROJECT_ID = "viralgen-464411"
GCS_BUCKET_NAME = "viral-veo2-results"


class VeoApiClient:
    """
    A Python client for the asynchronous Veo Video Generation API on Vertex AI.

    This class handles the entire three-step workflow:
    1. Job Submission: Initiates the video generation job via the `:predictLongRunning` endpoint.
    2. Status Polling: Repeatedly checks the job's status using the `:fetchPredictOperation` endpoint.
    3. Result Processing: Handles the final success or error response, including content policy errors.
    """

    def __init__(self, project_id: str, location: str = "us-central1", model_id: str = "veo-2.0-generate-001"):
        """
        Initializes the Veo API client.

        Args:
            project_id: Your Google Cloud project ID.
            location: The GCP location for the API endpoint (default: "us-central1").
            model_id: The Veo model ID to use (default: "veo-2.0-generate-001").
        """
        self.project_id = project_id
        self.location = location
        self.model_id = model_id
        self.api_base_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}"

    def _get_access_token(self) -> str:
        """
        Authenticates with Google Cloud and retrieves a temporary access token.
        This uses Application Default Credentials (ADC), which is the recommended secure method.
        """
        try:
            creds, _ = google.auth.default()
            auth_req = google.auth.transport.requests.Request()
            creds.refresh(auth_req)
            return creds.token
        except Exception as e:
            print(f"Error getting access token: {e}")
            raise

    def _submit_job(self, prompt: str, storage_uri: str, token: str) -> str:
        """
        Submits the video generation job to the `:predictLongRunning` endpoint.
        """
        url = f"{self.api_base_url}:predictLongRunning"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "durationSeconds": 8,
                "aspectRatio": "16:9",
                "personGeneration": "allow_adult",
                "storageUri": storage_uri,
            },
        }

        print("Submitting video generation job...")
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        operation_name = response.json().get("name")
        if not operation_name:
            raise ValueError("Failed to get operation name from submission response.")
            
        print(f"Successfully submitted job. Operation Name: {operation_name}")
        return operation_name

    def _poll_status(self, operation_name: str, token: str, poll_interval_seconds: int = 20) -> dict:
        """
        Polls the `:fetchPredictOperation` endpoint until the job is complete.
        """
        url = f"{self.api_base_url}:fetchPredictOperation"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json; charset=utf-8",
        }
        payload = {"operationName": operation_name}

        while True:
            print("Polling for job status...")
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("done", False):
                print("Job finished!")
                return result
            
            print(f"Job not done yet. Waiting for {poll_interval_seconds} seconds...")
            time.sleep(poll_interval_seconds)

    def generate_video(self, prompt: str, output_folder: str = "veo-outputs") -> Optional[str]:
        """
        Executes the full video generation workflow from submission to result retrieval.

        Args:
            prompt: The text prompt to generate the video from.
            output_folder: The subfolder within your GCS bucket to save the video.

        Returns:
            The GCS URI of the generated video on success, otherwise None.
        """
        try:
            # Step 0: Authentication
            token = self._get_access_token()
            storage_uri = f"gs://{GCS_BUCKET_NAME}/{output_folder}/"

            # Step 1: Submit Job
            operation_name = self._submit_job(prompt, storage_uri, token)

            # Step 2: Poll for Status
            final_result = self._poll_status(operation_name, token)

            # Step 3: Process Final Result
            if "error" in final_result:
                error_message = final_result["error"].get("message", "Unknown error")
                if "Responsible AI practices" in error_message:
                    print(f"\n--- JOB FAILED (CONTENT POLICY) ---\nPrompt was rejected for safety reasons: {error_message}\nPlease try rephrasing your prompt.\n")
                else:
                    print(f"\n--- JOB FAILED ---\nAn error occurred: {error_message}\n")
                return None

            video_uri = final_result.get("response", {}).get("videos", [{}])[0].get("gcsUri")
            if video_uri:
                print(f"\n--- SUCCESS! ---\nVideo generated successfully.\nLocation: {video_uri}\n")
                return video_uri
            else:
                print(f"\n--- JOB COMPLETED WITH UNEXPECTED RESPONSE ---\nFull response: {json.dumps(final_result, indent=2)}\n")
                return None

        except requests.exceptions.RequestException as e:
            print(f"\n--- HTTP ERROR ---\nAn error occurred during the API call: {e}\nResponse: {e.response.text if e.response else 'No response'}\n")
            return None
        except Exception as e:
            print(f"\n--- AN UNEXPECTED ERROR OCCURRED ---\n{e}\n")
            return None


if __name__ == "__main__":
    # This block runs when you execute the script directly
    
    print("--- Starting VEO Video Generation Client ---")

    # --- Configuration Check ---
    if not PROJECT_ID or not GCS_BUCKET_NAME:
        raise ValueError("Please set your PROJECT_ID and GCS_BUCKET_NAME at the top of the script.")

    # --- Instantiate and Run the Client ---
    veo_client = VeoApiClient(project_id=PROJECT_ID)
    
    # --- Define Your Prompt ---
    # Remember to avoid words that might trigger content filters (e.g., "toddler")
    video_prompt = "A whimsical cartoon character riding a small pony through a magical forest"
    
    # --- Generate the Video ---
    final_video_path = veo_client.generate_video(prompt=video_prompt)

    if final_video_path:
        print("Workflow complete. You can find your video at the GCS URI printed above.")
    else:
        print("Workflow failed. Please check the logs for details.") 