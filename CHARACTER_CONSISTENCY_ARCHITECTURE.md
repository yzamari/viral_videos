# Character Consistency Architecture for ViralAI

## Overview
This document outlines the enhanced character consistency system leveraging Google's latest AI models (Gemini 2.5 Flash Image aka nano-banana, Veo 3, and Imagen 4) to enable consistent character generation across entire movies and video series.

## Core Technologies

### 1. Gemini 2.5 Flash Image (nano-banana)
- **Purpose**: Character-consistent image generation and editing
- **Key Features**:
  - Upload character reference photos and maintain appearance consistency
  - Multi-turn editing capabilities
  - Style transfer while preserving identity
  - Pricing: $0.039 per image
- **Use Case**: Generate character shots in different poses, outfits, and scenes

### 2. Veo 3
- **Purpose**: Reference-powered video generation
- **Key Features**:
  - Accepts up to 3 reference images for character preservation
  - Native audio integration (dialogue, ambient sounds, music)
  - 8-second clips with character consistency
  - Camera control (rotations, dollies, zooms)
- **Use Case**: Generate video clips with consistent characters

### 3. Imagen 4
- **Purpose**: High-quality scene generation
- **Key Features**:
  - 2K resolution output
  - Excellent text rendering
  - Multiple aspect ratios
- **Use Case**: Generate backgrounds and environments

## Architecture Components

### 1. Character Database Layer
```
character_profiles/
├── metadata.json          # Character registry
├── {character_id}/
│   ├── reference/         # Original reference images
│   ├── generated/         # Generated variations
│   ├── scenes/           # Scene-specific images
│   ├── videos/           # Generated video clips
│   └── character.json    # Character metadata
```

### 2. Character Profile Structure
```json
{
  "character_id": "unique_id",
  "name": "Character Name",
  "description": "Detailed physical description",
  "personality": {
    "traits": ["confident", "analytical"],
    "voice_profile": "en-US-News-F",
    "mannerisms": ["hand gestures when explaining"]
  },
  "appearance": {
    "age": "35",
    "ethnicity": "Asian-American",
    "hair": "black bob cut",
    "eyes": "dark brown",
    "typical_attire": ["navy blazer", "professional wear"]
  },
  "reference_images": {
    "primary": "path/to/main_reference.jpg",
    "alternates": ["path/to/alt1.jpg", "path/to/alt2.jpg"]
  },
  "generated_assets": {
    "images": [],
    "videos": []
  }
}
```

## Implementation Pipeline

### Phase 1: Character Creation
1. **Reference Generation**
   - Use Gemini 2.5 Flash Image to create initial character reference
   - Generate multiple angles and expressions
   - Store in character database

2. **Character Validation**
   - Test consistency across different prompts
   - Verify identity preservation
   - Build character consistency hash

### Phase 2: Scene Generation
1. **Image-to-Image Pipeline**
   ```python
   # Pseudo-code for character scene generation
   def generate_character_scene(character_id, scene_description):
       character = load_character(character_id)
       reference_image = character.reference_images.primary
       
       # Use Gemini 2.5 Flash Image
       scene_image = gemini_flash.edit_image(
           reference=reference_image,
           prompt=f"Same person, now {scene_description}",
           preserve_identity=True
       )
       return scene_image
   ```

2. **Image-to-Video Pipeline**
   ```python
   # Pseudo-code for video generation
   def generate_character_video(character_id, action_description):
       character = load_character(character_id)
       reference_images = character.get_best_references(3)
       
       # Use Veo 3
       video = veo3.generate_video(
           prompt=action_description,
           reference_images=reference_images,
           reference_type="asset",
           duration=8,
           include_audio=True
       )
       return video
   ```

### Phase 3: Multi-Scene Consistency
1. **Scene Planning**
   - Break movie/video into 8-second segments
   - Plan character appearances and actions
   - Generate scene-specific references

2. **Batch Generation**
   - Generate all character images first
   - Use generated images as references for videos
   - Maintain consistency hash across generations

## Workflow Example: 60-Minute Movie

### Pre-Production
1. Create 3-5 main characters using Gemini 2.5 Flash Image
2. Generate 10-15 reference poses per character
3. Create character interaction references

### Production Pipeline
```
For each scene (450 8-second clips for 60 minutes):
1. Generate scene-specific character image (Gemini 2.5)
2. Generate environment/background (Imagen 4)
3. Composite character into scene
4. Generate video clip (Veo 3) with references
5. Add dialogue and sound effects
6. Validate character consistency
```

### Post-Production
1. Stitch clips together
2. Add transitions
3. Final audio mixing
4. Character consistency verification

## API Integration Points

### 1. Gemini 2.5 Flash Image API
```python
class GeminiFlashImageClient:
    def __init__(self):
        self.api_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2-5-flash-image"
        self.price_per_image = 0.039
    
    def generate_character_variant(self, reference_image, prompt):
        # API call to generate character variant
        pass
```

### 2. Veo 3 API (via Vertex AI)
```python
class Veo3Client:
    def __init__(self):
        self.model = "veo-3.0-generate-preview"
        self.max_references = 3
        self.clip_duration = 8
    
    def generate_with_references(self, prompt, reference_images):
        # API call with reference images
        pass
```

## Character Consistency Guarantees

### 1. Identity Preservation
- Use same reference images across all generations
- Maintain character hash for validation
- Implement face detection and comparison

### 2. Style Consistency
- Lock artistic style per project
- Use style transfer for environment matching
- Maintain color grading profiles

### 3. Quality Control
- Automated consistency checking
- Manual review checkpoints
- Character drift detection

## Cost Optimization

### Estimated Costs for 60-minute movie:
- Character creation: 50 images × $0.039 = $1.95
- Scene images: 450 × $0.039 = $17.55
- Video generation (Veo 3): 450 clips × $0.10 = $45.00
- **Total: ~$65 per hour of content**

### Optimization Strategies:
1. Cache and reuse character references
2. Batch similar scenes
3. Use lower resolution for previews
4. Implement smart scene planning

## Next Steps

1. **Immediate Actions**:
   - Set up Vertex AI access for Veo 3
   - Implement Gemini 2.5 Flash Image client
   - Create character database schema

2. **Short-term Goals**:
   - Build character creation UI
   - Implement consistency validation
   - Create test characters

3. **Long-term Vision**:
   - Full movie generation pipeline
   - Multi-character interaction system
   - Automated character casting

## Technical Requirements

### Google Cloud Setup:
```bash
# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable generativelanguage.googleapis.com

# Set up authentication
gcloud auth application-default login

# Configure project
gcloud config set project viralgen-464411
```

### Python Dependencies:
```python
# requirements.txt additions
google-cloud-aiplatform>=1.60.0
google-generativeai>=0.5.0
vertexai>=1.60.0
```

## Conclusion

This architecture leverages Google's cutting-edge AI models to solve the character consistency challenge. By combining Gemini 2.5 Flash Image's identity preservation with Veo 3's reference-powered video generation, we can create full-length movies with consistent characters across all scenes.

The key innovation is the three-stage pipeline:
1. **Character Creation** (Gemini 2.5 Flash Image)
2. **Scene Generation** (Gemini 2.5 + Imagen 4)
3. **Video Production** (Veo 3 with references)

This approach ensures visual consistency while maintaining creative flexibility for different scenes, poses, and actions.