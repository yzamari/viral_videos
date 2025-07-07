#!/usr/bin/env python3
"""
Test Google Cloud Text-to-Speech Setup
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_google_tts():
    """Test Google Cloud TTS configuration and voices"""
    
    print("🎤 Google Cloud Text-to-Speech Test")
    print("=" * 50)
    
    # Check environment
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path:
        print(f"✅ Credentials path set: {creds_path}")
        if os.path.exists(creds_path):
            print("✅ Credentials file exists")
        else:
            print("❌ Credentials file not found!")
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not set")
        print("\nTo fix:")
        print("1. Create service account in Google Cloud Console")
        print("2. Download JSON key file")
        print("3. Set: export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        return
    
    # Try to import and test
    try:
        from google.cloud import texttospeech
        print("\n✅ Google Cloud TTS library imported successfully")
        
        # Create client
        client = texttospeech.TextToSpeechClient()
        print("✅ TTS client created successfully")
        
        # List available voices
        print("\n📢 Available English (US) Voices:")
        print("-" * 50)
        
        voices = client.list_voices(language_code="en-US")
        
        neural_voices = []
        journey_voices = []
        studio_voices = []
        standard_voices = []
        
        for voice in voices.voices:
            if "Neural2" in voice.name:
                neural_voices.append(voice.name)
            elif "Journey" in voice.name:
                journey_voices.append(voice.name)
            elif "Studio" in voice.name:
                studio_voices.append(voice.name)
            else:
                standard_voices.append(voice.name)
        
        print(f"\n🧠 Neural2 Voices ({len(neural_voices)}):")
        for v in sorted(neural_voices)[:10]:  # Show first 10
            print(f"   - {v}")
            
        print(f"\n🚀 Journey Voices ({len(journey_voices)}):")
        for v in sorted(journey_voices):
            print(f"   - {v}")
            
        print(f"\n🎙️ Studio Voices ({len(studio_voices)}):")
        for v in sorted(studio_voices):
            print(f"   - {v}")
            
        print(f"\n📻 Standard Voices: {len(standard_voices)} available")
        
        # Test generation
        print("\n🎯 Testing Voice Generation...")
        print("-" * 50)
        
        test_text = "Hello! This is a test of Google Cloud Text-to-Speech with high-quality neural voices."
        
        # Test different voices
        test_voices = [
            ("en-US-Neural2-F", "Neural2 Female"),
            ("en-US-Neural2-D", "Neural2 Male"),
            ("en-US-Journey-F", "Journey Female (if available)"),
        ]
        
        for voice_name, description in test_voices:
            try:
                print(f"\n🎤 Testing {description}: {voice_name}")
                
                synthesis_input = texttospeech.SynthesisInput(text=test_text)
                
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name=voice_name
                )
                
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.0,
                    pitch=0.0
                )
                
                response = client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                # Save test file
                output_file = f"test_tts_{voice_name.replace('-', '_')}.mp3"
                with open(output_file, "wb") as out:
                    out.write(response.audio_content)
                
                file_size = os.path.getsize(output_file) / 1024
                print(f"   ✅ Generated: {output_file} ({file_size:.1f} KB)")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
        
        # Test with video generator
        print("\n🎬 Testing with Video Generator...")
        print("-" * 50)
        
        try:
            from src.generators.google_tts_client import GoogleTTSClient
            
            tts_client = GoogleTTSClient()
            
            # Test different emotions
            emotions = ["neutral", "funny", "excited", "dramatic"]
            
            for emotion in emotions:
                print(f"\n😊 Testing {emotion} emotion...")
                
                test_script = f"This is a test of the {emotion} voice setting. Notice how the tone and pace change!"
                
                audio_path = tts_client.generate_speech(
                    text=test_script,
                    feeling=emotion,
                    use_ssml=True
                )
                
                if os.path.exists(audio_path):
                    file_size = os.path.getsize(audio_path) / 1024
                    print(f"   ✅ Generated: {os.path.basename(audio_path)} ({file_size:.1f} KB)")
                else:
                    print(f"   ❌ Failed to generate audio")
                    
        except Exception as e:
            print(f"❌ Video generator TTS test failed: {e}")
            
    except ImportError:
        print("\n❌ Google Cloud TTS library not installed")
        print("Run: pip install google-cloud-texttospeech")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nPossible issues:")
        print("1. API not enabled in Google Cloud Console")
        print("2. Service account doesn't have Text-to-Speech permissions")
        print("3. Invalid credentials file")
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
    
    # Show pricing info
    print("\n💰 Pricing Information:")
    print("- Neural2 Voices: ~$16 per 1 million characters")
    print("- Journey Voices: ~$16 per 1 million characters")
    print("- Studio Voices: ~$160 per 1 million characters")
    print("- Typical 60s video: ~$0.012 (Neural2/Journey)")

if __name__ == "__main__":
    test_google_tts() 