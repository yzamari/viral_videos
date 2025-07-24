# Frame Continuity and Fadeout Configuration

## Frame Continuity Verification

### How Frame Extraction Works

The system extracts the last frame for continuity using the following logic:

1. **Get exact video duration** using FFmpeg
2. **Calculate frame timestamp**:
   ```python
   fps = video_config.get_fps(platform)  # Platform-specific FPS
   frames_to_trim = 1  # Configurable, default is 1
   frame_time = duration - (frames_to_trim / fps)
   ```
3. **Extract frame at exact timestamp**:
   ```bash
   ffmpeg -ss {frame_time} -i video.mp4 -vframes 1 output.jpg
   ```

### Example Calculations
- **30 FPS**: Last frame at `duration - 0.033s`
- **25 FPS**: Last frame at `duration - 0.040s`
- **60 FPS**: Last frame at `duration - 0.017s`

This ensures we get the actual last frame (or second-to-last if `frames_to_trim=1`).

## Fadeout Configuration

### Current Settings
- **Duration**: 2.0 seconds (updated from 0.5 seconds)
- **Minimum video length**: 10 seconds (fadeout only applied to videos ≥10s)
- **Type**: Both video and audio fade

### How Fadeout Works

1. **No extra time added** - fadeout happens within existing video duration
2. **Fade starts at**: `video_duration - fade_duration`
3. **FFmpeg filter**: `fade=t=out:st={start_time}:d={duration}`

### Application Logic
```python
# Only apply fadeout if:
# 1. Video is at least 10 seconds long
# 2. Current duration is more than 1 second below target
if video_duration >= 10 and current_duration < target_duration - 1.0:
    apply_fadeout()
```

## Configuration Location

All settings are in `/src/config/video_config.py`:

```python
class AnimationTimingConfig:
    # Frame continuity
    frame_continuity_trim_frames: int = 1
    
    # Fadeout
    fade_out_duration: float = 2.0
    fade_in_duration: float = 0.5
```

## Testing Frame Continuity

To verify frame continuity is working:

1. Generate a video with `--visual-continuity`
2. Check `outputs/session/images/` for:
   - `last_frame_clip_N.jpg` files
   - `frame_continuity_N_to_N+1.jpg` files
3. Compare last frame of clip N with first frame of clip N+1

## Common Issues

### Frame Mismatch
If frames don't match:
- Check if video has variable frame rate
- Verify platform FPS settings
- Try increasing `frame_continuity_trim_frames` to 2 or 3

### Fadeout Too Abrupt
If 2-second fadeout feels too quick:
- Can increase to 3.0 seconds in config
- Consider video length when setting fadeout duration

### Performance
Frame extraction adds ~0.5s per clip to generation time.
For faster testing, use `--no-visual-continuity`.