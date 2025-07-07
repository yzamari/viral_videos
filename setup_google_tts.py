#!/usr/bin/env python3
"""
Google Cloud TTS Setup Script
Helps configure and test Google Cloud Text-to-Speech
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_google_cloud_cli():
    """Check if gcloud CLI is installed"""
    try:
        result = subprocess.run(['gcloud', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Google Cloud CLI is installed")
            return True
    except:
        pass
    
    print("❌ Google Cloud CLI not found")
    print("   Install from: https://cloud.google.com/sdk/docs/install")
    return False

def check_credentials():
    """Check for existing credentials"""
    cred_paths = [
        os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', ''),
        'google-tts-credentials.json',
        os.path.expanduser('~/google-tts-credentials.json'),
        '.env'
    ]
    
    for path in cred_paths:
        if path and os.path.exists(path):
            if path.endswith('.json'):
                print(f"✅ Found credentials at: {path}")
                return path
            elif path == '.env':
                with open(path, 'r') as f:
                    content = f.read()
                    if 'GOOGLE_TTS_CREDENTIALS' in content:
                        print("✅ Found credentials in .env file")
                        return True
    
    print("❌ No Google Cloud credentials found")
    return None

def test_tts_connection():
    """Test Google Cloud TTS connection"""
    try:
        from google.cloud import texttospeech
        
        print("\n🧪 Testing Google Cloud TTS connection...")
        client = texttospeech.TextToSpeechClient()
        
        # List voices
        voices = client.list_voices()
        voice_count = len(voices.voices)
        
        print(f"✅ Connected successfully!")
        print(f"📢 Found {voice_count} available voices")
        
        # Show some neural voices
        neural_voices = [v for v in voices.voices if 'Neural2' in v.name or 'Journey' in v.name]
        print(f"\n🎤 Premium voices available:")
        for voice in neural_voices[:5]:
            print(f"   - {voice.name} ({voice.ssml_gender.name})")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_generate_audio():
    """Test generating audio with Google Cloud TTS"""
    try:
        from google.cloud import texttospeech
        
        print("\n🎤 Testing audio generation...")
        
        client = texttospeech.TextToSpeechClient()
        
        # Test text
        text = "Hello! This is a test of Google Cloud neural voices. The quality should be much better than basic text to speech."
        
        # Configure request
        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Neural2-F"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        
        # Generate
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Save test file
        test_file = "test_google_tts.mp3"
        with open(test_file, "wb") as out:
            out.write(response.audio_content)
        
        if os.path.exists(test_file) and os.path.getsize(test_file) > 0:
            print(f"✅ Audio generated successfully: {test_file}")
            print(f"   Size: {os.path.getsize(test_file) / 1024:.1f} KB")
            
            # Try to play it
            if sys.platform == "darwin":  # macOS
                subprocess.run(["afplay", test_file], capture_output=True)
                print("   🔊 Playing audio...")
            
            return True
        
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        return False

def setup_env_file():
    """Set up .env file with credentials"""
    cred_path = input("\n📁 Enter path to your google-tts-credentials.json file: ").strip()
    
    if not os.path.exists(cred_path):
        print(f"❌ File not found: {cred_path}")
        return False
    
    # Add to .env
    env_line = f'GOOGLE_APPLICATION_CREDENTIALS="{os.path.abspath(cred_path)}"\n'
    
    with open('.env', 'a') as f:
        f.write(env_line)
    
    print(f"✅ Added credentials to .env file")
    
    # Also set for current session
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(cred_path)
    
    return True

def main():
    """Main setup flow"""
    print("🎤 Google Cloud Text-to-Speech Setup")
    print("=" * 50)
    
    # Check prerequisites
    print("\n📋 Checking prerequisites...")
    
    # Check if already configured
    cred_path = check_credentials()
    if cred_path:
        if test_tts_connection():
            print("\n✅ Google Cloud TTS is already configured and working!")
            test_generate_audio()
            return
    
    # Not configured, help set up
    print("\n🚀 Let's set up Google Cloud TTS!")
    print("\nYou'll need:")
    print("1. A Google Cloud account")
    print("2. Text-to-Speech API enabled")
    print("3. Service account credentials (JSON file)")
    
    print("\n📖 Follow the guide at: GOOGLE_TTS_SETUP.md")
    
    # Check for gcloud CLI
    has_gcloud = check_google_cloud_cli()
    
    # Offer to configure credentials
    choice = input("\n🔧 Do you have a google-tts-credentials.json file? (y/n): ").lower()
    
    if choice == 'y':
        if setup_env_file():
            # Test connection
            if test_tts_connection():
                print("\n✅ Setup complete!")
                test_generate_audio()
            else:
                print("\n❌ Setup failed. Check your credentials and API permissions.")
    else:
        print("\n📚 Please follow these steps:")
        print("1. Go to: https://console.cloud.google.com")
        print("2. Create a project and enable Text-to-Speech API")
        print("3. Create a service account with TTS permissions")
        print("4. Download the JSON key file")
        print("5. Run this script again")
        
        print("\n📖 Detailed instructions in: GOOGLE_TTS_SETUP.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc() 