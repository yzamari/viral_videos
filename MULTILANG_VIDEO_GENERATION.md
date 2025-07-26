# Multi-Language Video Generation

## How It Works

The system generates separate complete videos for each language by:

1. **Single Video Generation**: First generates the base video content (clips) once
2. **Language-Specific Processing**: For each language:
   - Translates the script
   - Generates audio in the target language
   - Creates subtitles with proper formatting
   - Combines the base video with translated audio and subtitles

## Default Fallback Chain

The video generation follows this fallback chain automatically:
1. **VEO Generation** (2 attempts)
2. **Image Generation** (2 attempts, 3-4 images per second)
3. **Colored Fallback** (if all else fails)

## Shell Scripts

All scripts use the same pattern:
- `--languages en-US --languages he` for multiple languages
- `--no-cheap` to ensure quality generation
- Each language gets its own complete video file

### Example Usage

```bash
# Israeli PM Marvel Series
./run_israeli_pm_multilang.sh

# Nuclear News Series
./run_nuclear_news_multilang.sh

# Iranian Water Crisis News
./run_iranian_news_multilang.sh
```

## Output Structure

```
outputs/
└── session_name/
    ├── languages/
    │   ├── en_US/
    │   │   ├── video_en_US.mp4  # Complete video with English audio/subtitles
    │   │   ├── audio_en_US.mp3
    │   │   └── subtitles_en_US.srt
    │   └── he/
    │       ├── video_he.mp4     # Complete video with Hebrew audio/subtitles
    │       ├── audio_he.mp3
    │       └── subtitles_he.srt
    └── final_output/
        └── final_video.mp4       # Primary language version
```

## Features

- **Automatic Translation**: Scripts are translated to target languages
- **Native TTS**: Each language uses appropriate text-to-speech
- **Embedded Subtitles**: Subtitles are burned into the video
- **RTL Support**: Hebrew, Arabic, and Persian handled automatically
- **Quality Generation**: Uses VEO or image generation, not cheap mode

## Technical Details

The `WorkingOrchestrator._create_multilingual_files` method:
1. Translates the script for each language
2. Generates TTS audio
3. Creates SRT subtitles
4. Combines video + audio + subtitles using ffmpeg

This ensures each language version is a complete, standalone video file with proper audio and subtitles embedded.