#!/usr/bin/env python3
"""
Fix VEO-2 API client to use correct Vertex AI endpoints
"""

import os
import re

def fix_veo2_client():
    """Fix the VEO-2 client to use correct API endpoints"""
    file_path = "src/generators/vertex_ai_veo2_client.py"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix the API endpoint URL structure
    old_endpoint_pattern = r'url = f"{self\.model_endpoint}/{model_name}:generateVideos"'
    new_endpoint_pattern = 'url = f"{self.model_endpoint}/{model_name}:predictLongRunning"'
    
    if old_endpoint_pattern in content:
        content = re.sub(old_endpoint_pattern, new_endpoint_pattern, content)
        print("✅ Fixed API endpoint from :generateVideos to :predictLongRunning")
    
    # Fix the request data structure to match Vertex AI API
    old_request_structure = '''request_data = {
                "prompt": prompt,
                "config": {
                    "aspectRatio": aspect_ratio,
                    "personGeneration": "allow_adult"  # Allow people in videos
                }
            }'''
    
    new_request_structure = '''request_data = {
                "instances": [
                    {
                        "prompt": prompt
                    }
                ],
                "parameters": {
                    "aspectRatio": aspect_ratio,
                    "durationSeconds": int(duration),
                    "personGeneration": "allow_adult"
                }
            }'''
    
    content = content.replace(old_request_structure, new_request_structure)
    
    # Fix image handling
    old_image_handling = '''request_data["image"] = {
                        "bytesBase64Encoded": image_data,
                        "mimeType": "image/jpeg"
                    }'''
    
    new_image_handling = '''request_data["instances"][0]["image"] = {
                        "bytesBase64Encoded": image_data,
                        "mimeType": "image/jpeg"
                    }'''
    
    content = content.replace(old_image_handling, new_image_handling)
    
    # Fix GCS storage configuration
    old_storage = 'request_data["storageUri"] = f"gs://{self.gcs_bucket}/veo2_generations/{datetime.now().strftime(\'%Y%m%d_%H%M%S\')}"'
    new_storage = 'request_data["parameters"]["storageUri"] = f"gs://{self.gcs_bucket}/veo2_generations/{datetime.now().strftime(\'%Y%m%d_%H%M%S\')}"'
    
    content = content.replace(old_storage, new_storage)
    
    # Fix polling endpoint
    old_polling = 'url = f"{self.base_url}/{operation_name}"'
    new_polling = 'url = f"{self.model_endpoint}/{self.veo2_model}:fetchPredictOperation"'
    
    content = content.replace(old_polling, new_polling)
    
    # Fix polling request data
    old_poll_data = 'response = requests.get(url, headers=headers, timeout=30)'
    new_poll_data = '''poll_data = {
                    "operationName": operation_name
                }
                response = requests.post(url, headers=headers, json=poll_data, timeout=30)'''
    
    content = content.replace(old_poll_data, new_poll_data)
    
    # Write the fixed content back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ VEO-2 client fixed successfully!")
    return True

if __name__ == "__main__":
    fix_veo2_client() 