# 🎬 Hollywood Movie Generation - Setup Guide

## Quick Start (Test Mode)

Test the system with minimal resources (30 seconds, no API calls):
```bash
python generate_hollywood_movie.py "Robot discovers art" --test
```

## Full Production Mode

Generate a complete 5-minute Hollywood movie:
```bash
python generate_hollywood_movie.py "Epic space adventure" --genre sci-fi --style cinematic
```

## System Architecture

### Laptop Optimizations
- **Batched Processing**: Scenes generated in groups of 5
- **Limited Parallelism**: Max 2 concurrent VEO API calls
- **Aggressive Caching**: Reuses character references and similar scenes
- **Memory Management**: Automatic cleanup every 10 scenes
- **1080p Resolution**: Optimized for laptop processing (not 4K)

### Resource Usage
- **RAM**: ~4-8 GB during generation
- **Disk**: ~10 GB for cache and temp files
- **Network**: ~100-200 API calls for full movie
- **Time**: 30-45 minutes for 5-minute movie

## GCP Configuration

Your credentials are configured:
- **Email**: admin@al-ai.net
- **Project**: viralgen-464411
- **APIs Required**: VEO 3, Imagen 4, Gemini 1.5 Pro

## Pipeline Components

### 1. Scene Planning (Gemini)
- Generates 40-50 scene Hollywood script
- Three-act structure with emotional beats
- Optimized prompts for VEO generation

### 2. Character References (Imagen 4)
- Creates consistent character appearances
- Uses Imagen 4 Fast (10x speed)
- Cached for reuse across scenes

### 3. Video Generation (VEO 3)
- 6-8 second clips per scene
- Reference-based consistency
- Audio generation included

### 4. Music (Placeholder)
- Lyria 2 integration ready
- Currently uses placeholder audio
- Will auto-update when API available

### 5. Assembly (FFmpeg)
- Professional transitions
- 24fps cinema standard
- Optimized encoding for laptops

## Example Commands

### Test Modes
```bash
# Quick 30-second test
python generate_hollywood_movie.py "Test concept" --test

# Test with specific genre
python generate_hollywood_movie.py "AI love story" --genre romance --test
```

### Production Modes
```bash
# Sci-fi epic
python generate_hollywood_movie.py "Aliens visit Earth" --genre sci-fi --style vibrant

# Film noir
python generate_hollywood_movie.py "Digital detective" --genre thriller --style noir

# Comedy
python generate_hollywood_movie.py "Robot comedian" --genre comedy --style cinematic
```

### Advanced Options
```bash
# Disable cache (regenerate everything)
python generate_hollywood_movie.py "New story" --no-cache

# Show examples
python generate_hollywood_movie.py --examples
```

## Troubleshooting

### Common Issues

1. **API Quota Exceeded**
   - Solution: Wait 1 minute, use --test mode
   - Enable caching (default)

2. **Memory Issues**
   - Solution: Close other applications
   - Use test mode first

3. **Slow Generation**
   - Normal: 30-45 minutes for full movie
   - Use cached assets when possible

4. **Authentication Errors**
   ```bash
   gcloud auth login --account admin@al-ai.net
   gcloud config set project viralgen-464411
   ```

## Cache Management

Cache location: `outputs/session_*/hollywood_cache/`

Clear cache:
```bash
rm -rf outputs/*/hollywood_cache/
```

## Output Structure

```
outputs/
└── session_[timestamp]/
    ├── hollywood_output/       # Final movies
    ├── hollywood_cache/        # Cached assets
    ├── scenes/                 # Individual scene clips
    ├── audio/                  # Music tracks
    └── temp/                   # Temporary files
```

## Performance Tips

1. **First Run**: Use --test to verify setup
2. **Cache Assets**: Keep cache between runs
3. **Batch Generation**: Process multiple movies sequentially
4. **Network**: Stable connection required for API calls
5. **Storage**: Keep 10GB free for temp files

## Next Steps

1. Run test mode to verify setup
2. Generate your first 5-minute movie
3. Review and iterate on concepts
4. Share your Hollywood creations!

---

**Note**: Full Lyria 2 music generation will be enabled automatically when the API becomes publicly available.