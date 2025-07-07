#!/usr/bin/env python3
"""
Simple Veo-2 Client using existing Google API key (no gcloud required)
Based on user's working code but adapted to use API key authentication
"""
import os
import time
import json
import requests
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from user's working setup
PROJECT_ID = "viralgen-464411"
GCS_BUCKET_NAME = "viral-veo2-results"

class SimpleVeoApiClient:
    """
    A simplified Veo API client that uses Google API key (no gcloud required)
    """

    def __init__(self, api_key: str, project_id: str, location: str = "us-central1", model_id: str = "veo-2.0-generate-001"):
        """
        Initialize with API key instead of gcloud authentication
        """
        self.api_key = api_key
        self.project_id = project_id
        self.location = location
        self.model_id = model_id
        self.api_base_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model_id}"

    def _get_headers(self) -> dict:
        """
        Get headers with API key authentication
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json; charset=utf-8",
        }

    def _submit_job(self, prompt: str, storage_uri: str) -> Optional[str]:
        """
        Submit video generation job using API key
        """
        url = f"{self.api_base_url}:predictLongRunning"
        headers = self._get_headers()
        
        payload = {
            "instances": [{"prompt": prompt}],
            "parameters": {
                "durationSeconds": 8,
                "aspectRatio": "16:9",
                "personGeneration": "allow_adult",
                "storageUri": storage_uri,
            },
        }

        print("🚀 Submitting video generation job...")
        print(f"📝 Prompt: {prompt}")
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 429:
                print("⚠️ Quota limit hit - falling back to Google AI Studio approach")
                return None
                
            response.raise_for_status()
            
            operation_name = response.json().get("name")
            if not operation_name:
                raise ValueError("Failed to get operation name from submission response.")
                
            print(f"✅ Job submitted successfully")
            print(f"🔄 Operation: {operation_name}")
            return operation_name
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                print("⚠️ Quota limit reached")
                return None
            else:
                print(f"❌ HTTP Error: {e}")
                raise

    def _poll_status(self, operation_name: str, poll_interval_seconds: int = 20) -> dict:
        """
        Poll for job completion
        """
        url = f"{self.api_base_url}:fetchPredictOperation"
        headers = self._get_headers()
        payload = {"operationName": operation_name}

        check_count = 0
        max_checks = 20  # Max 6-7 minutes
        
        print("⏳ Waiting for Veo-2 video generation...")
        
        while check_count < max_checks:
            check_count += 1
            print(f"   Check {check_count}/{max_checks}: Polling job status...")
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get("done", False):
                print("✅ Job completed!")
                return result
            
            print(f"   Job still in progress, waiting {poll_interval_seconds} seconds...")
            time.sleep(poll_interval_seconds)
        
        raise Exception(f"Job did not complete within {max_checks * poll_interval_seconds} seconds")

    def generate_video(self, prompt: str, output_folder: str = "veo-outputs") -> Optional[str]:
        """
        Generate video using simplified API key approach
        """
        try:
            storage_uri = f"gs://{GCS_BUCKET_NAME}/{output_folder}/"
            
            # Step 1: Submit job
            operation_name = self._submit_job(prompt, storage_uri)
            if not operation_name:
                print("💡 Job submission failed - likely quota limit")
                return None

            # Step 2: Poll for completion
            final_result = self._poll_status(operation_name)

            # Step 3: Process result
            if "error" in final_result:
                error_message = final_result["error"].get("message", "Unknown error")
                if "Responsible AI practices" in error_message:
                    print(f"\n❌ CONTENT POLICY VIOLATION")
                    print(f"Prompt rejected for safety: {error_message}")
                    print("💡 Try rephrasing your prompt\n")
                else:
                    print(f"\n❌ JOB FAILED: {error_message}\n")
                return None

            # Extract video URI
            videos = final_result.get("response", {}).get("videos", [])
            if videos:
                video_uri = videos[0].get("gcsUri")
                if video_uri:
                    print(f"\n🎉 SUCCESS!")
                    print(f"Video generated: {video_uri}")
                    return video_uri

            print(f"\n⚠️ Unexpected response:")
            print(json.dumps(final_result, indent=2))
            return None

        except requests.exceptions.RequestException as e:
            print(f"\n❌ Network error: {e}")
            return None
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return None

def test_simple_generation():
    """Test simple video generation"""
    print("🧪 Testing Simple Veo-2 Client")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment")
        print("💡 Make sure your .env file contains GOOGLE_API_KEY")
        return False
    
    print(f"✅ API key loaded: {api_key[:20]}...")
    
    # Create client
    client = SimpleVeoApiClient(api_key=api_key, project_id=PROJECT_ID)
    
    # Test prompt (safe for content filters)
    prompt = "A whimsical cartoon character riding a small pony through a magical forest"
    
    print(f"\n🎬 Generating video...")
    print(f"📝 Prompt: {prompt}")
    
    # Generate video
    result = client.generate_video(prompt)
    
    if result:
        print(f"\n🎉 Video generation successful!")
        print(f"📍 GCS Location: {result}")
        print(f"\n💡 To download: gsutil cp {result} ./generated_video.mp4")
        return True
    else:
        print(f"\n⚠️ Video generation failed")
        print(f"💡 This might be due to quota limits or authentication issues")
        return False

if __name__ == "__main__":
    test_simple_generation() 