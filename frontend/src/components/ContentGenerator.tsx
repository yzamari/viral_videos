import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Stack,
  Grid,
  Card,
  CardContent,
  Chip,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Slider,
  Alert,
  LinearProgress,
  Divider,
  ToggleButton,
  ToggleButtonGroup,
  InputAdornment,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  VideoLibrary,
  Campaign,
  TrendingUp,
  PlayArrow,
  Stop,
  AutoAwesome,
  Psychology,
  Speed,
  AttachMoney,
  Timer,
  Language,
  Category,
  Style,
  Palette,
  MusicNote,
  Subtitles,
  Settings,
  Info,
  ContentCopy,
  Save,
  Upload,
} from '@mui/icons-material';

interface ContentConfig {
  mission: string;
  platform: string;
  category: string;
  style: string;
  visualStyle: string;
  musicStyle: string;
  duration: number;
  aspectRatio: string;
  language: string;
  voiceGender: string;
  voiceTone: string;
  aiMode: 'simple' | 'enhanced' | 'professional';
  cheapMode: boolean;
  includeSubtitles: boolean;
  includeWatermark: boolean;
  colorScheme: string;
  targetAudience: string;
  callToAction: string;
}

interface ContentGeneratorProps {
  onGenerate?: (config: ContentConfig) => void;
  isGenerating?: boolean;
}

const ContentGenerator: React.FC<ContentGeneratorProps> = ({ onGenerate, isGenerating = false }) => {
  const [config, setConfig] = useState<ContentConfig>({
    mission: '',
    platform: 'youtube',
    category: 'Technology',
    style: 'modern',
    visualStyle: 'cinematic',
    musicStyle: 'upbeat',
    duration: 60,
    aspectRatio: '16:9',
    language: 'en',
    voiceGender: 'female',
    voiceTone: 'professional',
    aiMode: 'enhanced',
    cheapMode: true,
    includeSubtitles: true,
    includeWatermark: false,
    colorScheme: 'vibrant',
    targetAudience: 'general',
    callToAction: '',
  });

  const platforms = [
    { id: 'youtube', name: 'YouTube', ratio: '16:9', duration: [15, 600] },
    { id: 'tiktok', name: 'TikTok', ratio: '9:16', duration: [15, 60] },
    { id: 'instagram', name: 'Instagram Reels', ratio: '9:16', duration: [15, 90] },
    { id: 'twitter', name: 'Twitter/X', ratio: '16:9', duration: [5, 140] },
    { id: 'linkedin', name: 'LinkedIn', ratio: '16:9', duration: [10, 300] },
  ];

  const categories = [
    'Technology', 'Business', 'Education', 'Entertainment',
    'Health & Fitness', 'Food & Cooking', 'Travel', 'Fashion',
    'Gaming', 'Science', 'News', 'Sports', 'Music', 'Art',
  ];

  const styles = [
    { id: 'modern', name: 'Modern', description: 'Clean and contemporary' },
    { id: 'vintage', name: 'Vintage', description: 'Retro and nostalgic' },
    { id: 'minimalist', name: 'Minimalist', description: 'Simple and elegant' },
    { id: 'bold', name: 'Bold', description: 'Eye-catching and dynamic' },
    { id: 'playful', name: 'Playful', description: 'Fun and energetic' },
    { id: 'professional', name: 'Professional', description: 'Corporate and serious' },
  ];

  const visualStyles = [
    'cinematic', 'documentary', 'animated', 'realistic',
    'abstract', 'cartoon', 'sketch', 'watercolor',
  ];

  const musicStyles = [
    'upbeat', 'calm', 'epic', 'corporate', 'ambient',
    'electronic', 'acoustic', 'orchestral', 'hip-hop', 'none',
  ];

  const colorSchemes = [
    'vibrant', 'pastel', 'monochrome', 'warm', 'cool',
    'earth', 'neon', 'gradient', 'dark', 'light',
  ];

  const handlePlatformChange = (platform: string) => {
    const platformConfig = platforms.find(p => p.id === platform);
    if (platformConfig) {
      setConfig({
        ...config,
        platform,
        aspectRatio: platformConfig.ratio,
        duration: Math.min(config.duration, platformConfig.duration[1]),
      });
    }
  };

  const handleGenerate = () => {
    if (onGenerate && config.mission) {
      onGenerate(config);
    }
  };

  const templates = [
    { name: 'Product Launch', mission: 'Create an exciting product launch video', style: 'bold', music: 'epic' },
    { name: 'Tutorial', mission: 'Educational step-by-step guide', style: 'modern', music: 'calm' },
    { name: 'Brand Story', mission: 'Tell our brand story', style: 'professional', music: 'corporate' },
    { name: 'Social Campaign', mission: 'Viral social media campaign', style: 'playful', music: 'upbeat' },
  ];

  const applyTemplate = (template: any) => {
    setConfig({
      ...config,
      mission: template.mission,
      style: template.style,
      musicStyle: template.music,
    });
  };

  return (
    <Box>
      <Paper elevation={0} sx={{ p: 3, border: '2px solid', borderColor: '#E5E7EB', backgroundColor: '#FFFFFF' }}>
        <Stack spacing={3}>
          {/* Header */}
          <Box>
            <Stack direction="row" alignItems="center" spacing={2}>
              <VideoLibrary sx={{ fontSize: 32, color: 'primary.main' }} />
              <Box>
                <Typography variant="h5" fontWeight={600}>
                  Content Generator
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Create AI-powered video content for any platform
                </Typography>
              </Box>
            </Stack>
          </Box>

          <Divider />

          {/* Quick Templates */}
          <Box>
            <Typography variant="subtitle2" gutterBottom sx={{ mb: 2 }}>
              Quick Start Templates
            </Typography>
            <Grid container spacing={2}>
              {templates.map((template) => (
                <Grid item xs={12} sm={6} md={3} key={template.name}>
                  <Card
                    variant="outlined"
                    sx={{
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      '&:hover': {
                        borderColor: 'primary.main',
                        transform: 'translateY(-2px)',
                        boxShadow: 2,
                      },
                    }}
                    onClick={() => applyTemplate(template)}
                  >
                    <CardContent>
                      <Typography variant="subtitle2" fontWeight={600}>
                        {template.name}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {template.mission}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Box>

          {/* Mission Input */}
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Content Mission"
            placeholder="Describe what you want to create... (e.g., 'Create a product demo video showcasing our new AI features')"
            value={config.mission}
            onChange={(e) => setConfig({ ...config, mission: e.target.value })}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Campaign />
                </InputAdornment>
              ),
            }}
          />

          {/* Configuration Grid */}
          <Grid container spacing={3}>
            {/* Left Column */}
            <Grid item xs={12} md={6}>
              <Stack spacing={3}>
                {/* Platform Selection */}
                <FormControl fullWidth>
                  <InputLabel>Platform</InputLabel>
                  <Select
                    value={config.platform}
                    onChange={(e) => handlePlatformChange(e.target.value)}
                    label="Platform"
                  >
                    {platforms.map(platform => (
                      <MenuItem key={platform.id} value={platform.id}>
                        {platform.name} ({platform.ratio})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {/* Category */}
                <FormControl fullWidth>
                  <InputLabel>Category</InputLabel>
                  <Select
                    value={config.category}
                    onChange={(e) => setConfig({ ...config, category: e.target.value })}
                    label="Category"
                  >
                    {categories.map(cat => (
                      <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {/* Style Selection */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Content Style
                  </Typography>
                  <ToggleButtonGroup
                    value={config.style}
                    exclusive
                    onChange={(e, value) => value && setConfig({ ...config, style: value })}
                    fullWidth
                    size="small"
                  >
                    {styles.slice(0, 3).map(style => (
                      <ToggleButton key={style.id} value={style.id}>
                        <Tooltip title={style.description}>
                          <span>{style.name}</span>
                        </Tooltip>
                      </ToggleButton>
                    ))}
                  </ToggleButtonGroup>
                  <ToggleButtonGroup
                    value={config.style}
                    exclusive
                    onChange={(e, value) => value && setConfig({ ...config, style: value })}
                    fullWidth
                    size="small"
                    sx={{ mt: 1 }}
                  >
                    {styles.slice(3).map(style => (
                      <ToggleButton key={style.id} value={style.id}>
                        <Tooltip title={style.description}>
                          <span>{style.name}</span>
                        </Tooltip>
                      </ToggleButton>
                    ))}
                  </ToggleButtonGroup>
                </Box>

                {/* Visual Style */}
                <FormControl fullWidth>
                  <InputLabel>Visual Style</InputLabel>
                  <Select
                    value={config.visualStyle}
                    onChange={(e) => setConfig({ ...config, visualStyle: e.target.value })}
                    label="Visual Style"
                  >
                    {visualStyles.map(style => (
                      <MenuItem key={style} value={style}>
                        {style.charAt(0).toUpperCase() + style.slice(1)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {/* Duration Slider */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    Duration: {config.duration} seconds
                  </Typography>
                  <Slider
                    value={config.duration}
                    onChange={(e, value) => setConfig({ ...config, duration: value as number })}
                    min={15}
                    max={platforms.find(p => p.id === config.platform)?.duration[1] || 300}
                    step={5}
                    marks={[
                      { value: 15, label: '15s' },
                      { value: 60, label: '1m' },
                      { value: 180, label: '3m' },
                    ]}
                    valueLabelDisplay="auto"
                  />
                </Box>
              </Stack>
            </Grid>

            {/* Right Column */}
            <Grid item xs={12} md={6}>
              <Stack spacing={3}>
                {/* AI Mode */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom>
                    AI Processing Mode
                  </Typography>
                  <ToggleButtonGroup
                    value={config.aiMode}
                    exclusive
                    onChange={(e, value) => value && setConfig({ ...config, aiMode: value })}
                    fullWidth
                  >
                    <ToggleButton value="simple">
                      <Stack alignItems="center" spacing={0.5}>
                        <Speed fontSize="small" />
                        <Typography variant="caption">Simple</Typography>
                      </Stack>
                    </ToggleButton>
                    <ToggleButton value="enhanced">
                      <Stack alignItems="center" spacing={0.5}>
                        <Psychology fontSize="small" />
                        <Typography variant="caption">Enhanced</Typography>
                      </Stack>
                    </ToggleButton>
                    <ToggleButton value="professional">
                      <Stack alignItems="center" spacing={0.5}>
                        <AutoAwesome fontSize="small" />
                        <Typography variant="caption">Professional</Typography>
                      </Stack>
                    </ToggleButton>
                  </ToggleButtonGroup>
                </Box>

                {/* Music Style */}
                <FormControl fullWidth>
                  <InputLabel>Music Style</InputLabel>
                  <Select
                    value={config.musicStyle}
                    onChange={(e) => setConfig({ ...config, musicStyle: e.target.value })}
                    label="Music Style"
                  >
                    {musicStyles.map(style => (
                      <MenuItem key={style} value={style}>
                        {style.charAt(0).toUpperCase() + style.slice(1)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {/* Color Scheme */}
                <FormControl fullWidth>
                  <InputLabel>Color Scheme</InputLabel>
                  <Select
                    value={config.colorScheme}
                    onChange={(e) => setConfig({ ...config, colorScheme: e.target.value })}
                    label="Color Scheme"
                  >
                    {colorSchemes.map(scheme => (
                      <MenuItem key={scheme} value={scheme}>
                        {scheme.charAt(0).toUpperCase() + scheme.slice(1)}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                {/* Voice Settings */}
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Voice Gender</InputLabel>
                      <Select
                        value={config.voiceGender}
                        onChange={(e) => setConfig({ ...config, voiceGender: e.target.value })}
                        label="Voice Gender"
                      >
                        <MenuItem value="female">Female</MenuItem>
                        <MenuItem value="male">Male</MenuItem>
                        <MenuItem value="neutral">Neutral</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={6}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Voice Tone</InputLabel>
                      <Select
                        value={config.voiceTone}
                        onChange={(e) => setConfig({ ...config, voiceTone: e.target.value })}
                        label="Voice Tone"
                      >
                        <MenuItem value="professional">Professional</MenuItem>
                        <MenuItem value="friendly">Friendly</MenuItem>
                        <MenuItem value="energetic">Energetic</MenuItem>
                        <MenuItem value="calm">Calm</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                </Grid>

                {/* Call to Action */}
                <TextField
                  fullWidth
                  label="Call to Action"
                  placeholder="e.g., Visit our website, Subscribe now, Learn more..."
                  value={config.callToAction}
                  onChange={(e) => setConfig({ ...config, callToAction: e.target.value })}
                />

                {/* Options */}
                <Box>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.cheapMode}
                        onChange={(e) => setConfig({ ...config, cheapMode: e.target.checked })}
                        color="warning"
                      />
                    }
                    label={
                      <Stack direction="row" spacing={1} alignItems="center">
                        <AttachMoney />
                        <span>Cost-Optimized Mode</span>
                      </Stack>
                    }
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.includeSubtitles}
                        onChange={(e) => setConfig({ ...config, includeSubtitles: e.target.checked })}
                      />
                    }
                    label="Include Subtitles"
                  />
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.includeWatermark}
                        onChange={(e) => setConfig({ ...config, includeWatermark: e.target.checked })}
                      />
                    }
                    label="Add Watermark"
                  />
                </Box>
              </Stack>
            </Grid>
          </Grid>

          <Divider />

          {/* Cost Estimation */}
          {config.cheapMode && (
            <Alert severity="info" icon={<AttachMoney />}>
              <Typography variant="body2">
                <strong>Cost-Optimized Mode Active:</strong> Using efficient AI models and optimized processing.
                Estimated cost: ~${config.aiMode === 'simple' ? '0.05' : config.aiMode === 'enhanced' ? '0.15' : '0.30'} per video
              </Typography>
            </Alert>
          )}

          {/* Action Buttons */}
          <Stack direction="row" spacing={2} justifyContent="space-between">
            <Stack direction="row" spacing={2}>
              <Button
                variant="outlined"
                startIcon={<Save />}
                disabled={isGenerating}
              >
                Save Template
              </Button>
              <Button
                variant="outlined"
                startIcon={<Upload />}
                disabled={isGenerating}
              >
                Load Template
              </Button>
            </Stack>
            
            <Stack direction="row" spacing={2}>
              <Button
                variant="outlined"
                startIcon={<ContentCopy />}
                disabled={isGenerating || !config.mission}
              >
                Duplicate
              </Button>
              <Button
                variant="contained"
                startIcon={isGenerating ? <Stop /> : <PlayArrow />}
                onClick={handleGenerate}
                disabled={!config.mission}
                sx={{
                  minWidth: 180,
                  background: isGenerating 
                    ? 'linear-gradient(45deg, #ff6b6b 30%, #ff8787 90%)'
                    : undefined,
                }}
              >
                {isGenerating ? 'Stop Generation' : 'Generate Content'}
              </Button>
            </Stack>
          </Stack>

          {/* Generation Progress */}
          {isGenerating && (
            <Box>
              <LinearProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Generating content with {config.aiMode} AI mode...
              </Typography>
            </Box>
          )}
        </Stack>
      </Paper>
    </Box>
  );
};

export default ContentGenerator;