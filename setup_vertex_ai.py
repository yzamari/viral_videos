#!/usr/bin/env python3
"""
Setup script for Vertex AI integration
"""
import os
import subprocess
import sys

def main():
    print("🚀 Vertex AI Setup for Viral Video Generator")
    print("=" * 50)
    
    # Check if gcloud is installed
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        print("✅ Google Cloud SDK installed")
        print(f"   Version: {result.stdout.split()[0]}")
    except FileNotFoundError:
        print("❌ Google Cloud SDK not installed")
        print("   Install from: https://cloud.google.com/sdk/docs/install")
        return False
    
    # Check if authenticated
    try:
        result = subprocess.run(['gcloud', 'auth', 'list', '--filter=status:ACTIVE'], 
                              capture_output=True, text=True)
        if 'ACTIVE' in result.stdout:
            print("✅ Google Cloud authenticated")
        else:
            print("❌ Not authenticated with Google Cloud")
            print("   Run: gcloud auth login")
            return False
    except:
        print("❌ Authentication check failed")
        return False
    
    # Check project
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'], 
                              capture_output=True, text=True)
        project_id = result.stdout.strip()
        if project_id and project_id != '(unset)':
            print(f"✅ Project configured: {project_id}")
        else:
            print("❌ No project configured")
            print("   Run: gcloud config set project YOUR_PROJECT_ID")
            return False
    except:
        print("❌ Project check failed")
        return False
    
    # Check Vertex AI API
    try:
        result = subprocess.run(['gcloud', 'services', 'list', '--enabled', 
                               '--filter=name:aiplatform.googleapis.com'], 
                              capture_output=True, text=True)
        if 'aiplatform.googleapis.com' in result.stdout:
            print("✅ Vertex AI API enabled")
        else:
            print("❌ Vertex AI API not enabled")
            print("   Run: gcloud services enable aiplatform.googleapis.com")
            return False
    except:
        print("❌ API check failed")
        return False
    
    print("\n🎉 Vertex AI setup complete!")
    print("   You can now use Vertex AI for unlimited Veo-2 generation")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup incomplete. Please follow the instructions above.")
        sys.exit(1)
    else:
        print("\n✅ Ready to use Vertex AI!") 