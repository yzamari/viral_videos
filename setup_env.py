#!/usr/bin/env python3
"""
Environment Setup Script for Viral AI Video Generator
Automatically configures all required environment variables
"""

import os
import sys
import subprocess
from pathlib import Path


def setup_environment():
    """Set up all required environment variables"""

    print("🔧 Setting up environment variables for Viral AI Video Generator...")

    # Get current gcloud project
    try:
        result = subprocess.run(['gcloud', 'config', 'get-value', 'project'],
                                capture_output=True, text=True, timeout=5)
        current_project = result.stdout.strip() if result.returncode == 0 else None
    except BaseException:
        current_project = None

    # Default configuration
    default_config = {
        'GOOGLE_CLOUD_PROJECT_ID': current_project or 'viralgen-464411',
        'GOOGLE_CLOUD_PROJECT': current_project or 'viralgen-464411',
        'VERTEX_AI_PROJECT_ID': current_project or 'viralgen-464411',
        'VEO_PROJECT_ID': current_project or 'viralgen-464411',
        'GOOGLE_CLOUD_LOCATION': 'us-central1',
        'VERTEX_AI_LOCATION': 'us-central1',
        'VEO_LOCATION': 'us-central1',
        'VERTEX_AI_GCS_BUCKET': 'viral-veo2-results',
        'GCS_BUCKET': 'viral-veo2-results',
        'GOOGLE_CLOUD_STORAGE_BUCKET': 'viral-veo2-results',
        'USE_REAL_VEO2': 'true',
        'VEO_FALLBACK_ENABLED': 'true',
        'GOOGLE_TTS_ENABLED': 'true',
        'GOOGLE_TTS_VOICE_TYPE': 'en-US-Neural2-F',
        'DEFAULT_VIDEO_DURATION': '15',
        'DEFAULT_PLATFORM': 'youtube',
        'DEFAULT_CATEGORY': 'Comedy',
        'DEFAULT_FRAME_CONTINUITY': 'true',
        'ENABLE_COMPREHENSIVE_LOGGING': 'true',
        'DEBUG_MODE': 'false',
        'VERBOSE_LOGGING': 'false'
    }

    # Check if .env file exists
    env_file = Path('.env')
    env_content = {}

    if env_file.exists():
        print("📄 Reading existing .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_content[key.strip()] = value.strip()

    # Update with defaults (only if not already set)
    updated = False
    for key, default_value in default_config.items():
        if key not in env_content:
            env_content[key] = default_value
            updated = True
            print(f"✅ Set {key}={default_value}")

    # Handle API keys separately (don't overwrite)
    api_keys = ['GOOGLE_API_KEY', 'GEMINI_API_KEY', 'OPENAI_API_KEY', 'ELEVENLABS_API_KEY']
    for key in api_keys:
        if key not in env_content:
            env_content[key] = 'your_api_key_here'
            print(f"⚠️  Set {key}=your_api_key_here (PLEASE UPDATE THIS)")
            updated = True

    # Write updated .env file
    if updated:
        print("💾 Writing updated .env file...")
        with open(env_file, 'w') as f:
            f.write("# Viral AI Video Generator Environment Configuration\n")
            f.write("# Auto-generated by setup_env.py\n\n")

            # Group related settings
            f.write("# Core API Keys\n")
            for key in api_keys:
                f.write(f"{key}={env_content[key]}\n")

            f.write("\n# Google Cloud Configuration\n")
            gcp_keys = [k for k in env_content.keys(
            ) if 'GOOGLE_CLOUD' in k or 'VERTEX_AI' in k or 'VEO' in k or 'GCS' in k]
            for key in sorted(gcp_keys):
                f.write(f"{key}={env_content[key]}\n")

            f.write("\n# Application Settings\n")
            app_keys = [k for k in env_content.keys() if k not in api_keys and k not in gcp_keys]
            for key in sorted(app_keys):
                f.write(f"{key}={env_content[key]}\n")

        print("✅ Environment configuration updated!")
    else:
        print("✅ Environment already configured!")

    # Set environment variables for current session
    print("\n🔧 Setting environment variables for current session...")
    for key, value in env_content.items():
        os.environ[key] = value

    print("\n📋 Environment Summary:")
    print(f"   Project ID: {env_content.get('GOOGLE_CLOUD_PROJECT_ID', 'Not set')}")
    print(f"   Location: {env_content.get('GOOGLE_CLOUD_LOCATION', 'Not set')}")
    print(f"   GCS Bucket: {env_content.get('VERTEX_AI_GCS_BUCKET', 'Not set')}")
    print(
        f"   Google API Key: {
            'Set' if env_content.get(
                'GOOGLE_API_KEY',
                '').startswith('AIza') else 'Not set'}")

    # Check if we need to update API keys
    needs_api_keys = any(env_content.get(key, '').startswith('your_api_key_here')
                         for key in api_keys)

    if needs_api_keys:
        print("\n⚠️  ACTION REQUIRED:")
        print("   Please update your API keys in the .env file:")
        for key in api_keys:
            if env_content.get(key, '').startswith('your_api_key_here'):
                print(f"   - {key}=your_actual_api_key")
        print("\n   Then run: python check_auth.py")
    else:
        print("\n🚀 Ready to test authentication!")
        print("   Run: python check_auth.py")


def main():
    """Main function"""
    try:
        setup_environment()
    except KeyboardInterrupt:
        print("\n🛑 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
