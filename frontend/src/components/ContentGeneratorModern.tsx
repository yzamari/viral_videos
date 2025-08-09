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
  Container,
  Avatar,
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
  Lightbulb,
  Rocket,
  Star,
  EmojiEvents,
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
  // Advanced options
  imageOnly: boolean;
  fallbackOnly: boolean;
  forceGeneration: boolean;
  skipAuthTest: boolean;
  discussionMode: 'simple' | 'enhanced' | 'professional';
  showDiscussionLogs: boolean;
}

interface ContentGeneratorProps {
  onGenerate?: (config: ContentConfig) => void;
  isGenerating?: boolean;
}

const ContentGeneratorModern: React.FC<ContentGeneratorProps> = ({ onGenerate, isGenerating = false }) => {
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
    // Advanced options
    imageOnly: false,
    fallbackOnly: false,
    forceGeneration: false,
    skipAuthTest: false,
    discussionMode: 'enhanced',
    showDiscussionLogs: false,
  });

  const templates = [
    { 
      id: 'product',
      name: 'Product Launch', 
      icon: <Rocket />,
      color: '#FF6B35',
      mission: 'Create an exciting product launch video',
      description: 'Perfect for new product announcements'
    },
    { 
      id: 'tutorial',
      name: 'Tutorial', 
      icon: <Lightbulb />,
      color: '#004E89',
      mission: 'Educational step-by-step guide',
      description: 'Teach your audience something new'
    },
    { 
      id: 'brand',
      name: 'Brand Story', 
      icon: <Star />,
      color: '#7B2CBF',
      mission: 'Tell our brand story',
      description: 'Share your company values and mission'
    },
    { 
      id: 'social',
      name: 'Social Campaign', 
      icon: <EmojiEvents />,
      color: '#00BF63',
      mission: 'Viral social media campaign',
      description: 'Create engaging social content'
    },
  ];

  const applyTemplate = (template: any) => {
    setConfig({
      ...config,
      mission: template.mission,
    });
  };

  const handleGenerate = () => {
    if (onGenerate && config.mission) {
      onGenerate(config);
    }
  };

  return (
    <Box>
      {/* Header Section */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h4" fontWeight={900} gutterBottom>
          Content Generator
        </Typography>
        <Typography variant="body1" color="text.secondary" fontWeight={600}>
          Create professional AI-powered videos for any platform
        </Typography>
      </Box>

      {/* Quick Start Templates */}
      <Box sx={{ mb: 6 }}>
        <Typography variant="h6" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
          Quick Start Templates
        </Typography>
        <Grid container spacing={3}>
          {templates.map((template) => (
            <Grid size={{ xs: 12, sm: 6, md: 3 }} key={template.id}>
              <Card
                elevation={0}
                sx={{
                  height: '100%',
                  cursor: 'pointer',
                  position: 'relative',
                  overflow: 'visible',
                  border: '2px solid transparent',
                  transition: 'all 0.3s ease',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: 4,
                    borderColor: template.color,
                    '& .template-icon': {
                      transform: 'scale(1.1) rotate(5deg)',
                    },
                  },
                }}
                onClick={() => applyTemplate(template)}
              >
                <CardContent sx={{ textAlign: 'center', p: 3 }}>
                  <Box
                    className="template-icon"
                    sx={{
                      width: 64,
                      height: 64,
                      borderRadius: 2,
                      background: `linear-gradient(135deg, ${template.color}20 0%, ${template.color}10 100%)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mx: 'auto',
                      mb: 2,
                      transition: 'transform 0.3s ease',
                      color: template.color,
                    }}
                  >
                    {React.cloneElement(template.icon, { fontSize: 'large' })}
                  </Box>
                  <Typography variant="h6" fontWeight={700} gutterBottom>
                    {template.name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" fontWeight={500}>
                    {template.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>

      {/* Main Configuration */}
      <Paper elevation={0} sx={{ p: 4, borderRadius: 3, mb: 4 }}>
        <Grid container spacing={4}>
          {/* Mission Input */}
          <Grid size={{ xs: 12 }}>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="What do you want to create?"
              placeholder="Describe your video idea... (e.g., 'Create a product demo video showcasing our new AI features')"
              value={config.mission}
              onChange={(e) => setConfig({ ...config, mission: e.target.value })}
              sx={{
                '& .MuiOutlinedInput-root': {
                  fontSize: '1.1rem',
                },
              }}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <Campaign color="primary" />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>

          {/* Platform and Settings */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Stack spacing={3}>
              <FormControl fullWidth>
                <InputLabel>Platform</InputLabel>
                <Select
                  value={config.platform}
                  onChange={(e) => setConfig({ ...config, platform: e.target.value })}
                  label="Platform"
                >
                  <MenuItem value="youtube">YouTube (16:9)</MenuItem>
                  <MenuItem value="tiktok">TikTok (9:16)</MenuItem>
                  <MenuItem value="instagram">Instagram Reels (9:16)</MenuItem>
                  <MenuItem value="twitter">Twitter/X (16:9)</MenuItem>
                  <MenuItem value="linkedin">LinkedIn (16:9)</MenuItem>
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={config.category}
                  onChange={(e) => setConfig({ ...config, category: e.target.value })}
                  label="Category"
                >
                  {['Technology', 'Business', 'Education', 'Entertainment', 'Health', 'Travel'].map(cat => (
                    <MenuItem key={cat} value={cat}>{cat}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Box>
                <Typography variant="subtitle2" gutterBottom sx={{ mb: 2, fontWeight: 600 }}>
                  Duration: {config.duration} seconds
                </Typography>
                <Slider
                  value={config.duration}
                  onChange={(e, value) => setConfig({ ...config, duration: value as number })}
                  min={15}
                  max={300}
                  step={5}
                  marks={[
                    { value: 15, label: '15s' },
                    { value: 60, label: '1m' },
                    { value: 180, label: '3m' },
                    { value: 300, label: '5m' },
                  ]}
                  valueLabelDisplay="auto"
                />
              </Box>
            </Stack>
          </Grid>

          {/* AI Settings */}
          <Grid size={{ xs: 12, md: 6 }}>
            <Stack spacing={3}>
              <Box>
                <Typography variant="subtitle2" gutterBottom sx={{ mb: 2, fontWeight: 600 }}>
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
                      <Speed />
                      <Typography variant="caption">Fast</Typography>
                    </Stack>
                  </ToggleButton>
                  <ToggleButton value="enhanced">
                    <Stack alignItems="center" spacing={0.5}>
                      <Psychology />
                      <Typography variant="caption">Smart</Typography>
                    </Stack>
                  </ToggleButton>
                  <ToggleButton value="professional">
                    <Stack alignItems="center" spacing={0.5}>
                      <AutoAwesome />
                      <Typography variant="caption">Pro</Typography>
                    </Stack>
                  </ToggleButton>
                </ToggleButtonGroup>
              </Box>

              <FormControl fullWidth>
                <InputLabel>Visual Style</InputLabel>
                <Select
                  value={config.visualStyle}
                  onChange={(e) => setConfig({ ...config, visualStyle: e.target.value })}
                  label="Visual Style"
                >
                  {['cinematic', 'animated', 'realistic', 'abstract', 'minimal'].map(style => (
                    <MenuItem key={style} value={style}>
                      {style.charAt(0).toUpperCase() + style.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl fullWidth>
                <InputLabel>Music Style</InputLabel>
                <Select
                  value={config.musicStyle}
                  onChange={(e) => setConfig({ ...config, musicStyle: e.target.value })}
                  label="Music Style"
                >
                  {['upbeat', 'calm', 'epic', 'corporate', 'none'].map(style => (
                    <MenuItem key={style} value={style}>
                      {style.charAt(0).toUpperCase() + style.slice(1)}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Stack>
          </Grid>

          {/* Additional Options */}
          <Grid size={{ xs: 12 }}>
            <Box sx={{ 
              p: 3, 
              borderRadius: 2, 
              background: 'transparent',
              border: '2px solid #E1E5E9',
            }}>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 4 }}>
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
                        <Typography variant="body2" fontWeight={600}>Cost-Optimized Mode</Typography>
                      </Stack>
                    }
                  />
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.includeSubtitles}
                        onChange={(e) => setConfig({ ...config, includeSubtitles: e.target.checked })}
                      />
                    }
                    label={
                      <Stack direction="row" spacing={1} alignItems="center">
                        <Subtitles />
                        <Typography variant="body2" fontWeight={600}>Include Subtitles</Typography>
                      </Stack>
                    }
                  />
                </Grid>
                <Grid size={{ xs: 12, md: 4 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.includeWatermark}
                        onChange={(e) => setConfig({ ...config, includeWatermark: e.target.checked })}
                      />
                    }
                    label={<Typography variant="body2" fontWeight={600}>Add Watermark</Typography>}
                  />
                </Grid>
              </Grid>
            </Box>
          </Grid>

          {/* Advanced Options Section */}
          <Grid size={{ xs: 12 }}>
            <Box sx={{ 
              p: 3, 
              borderRadius: 2, 
              background: 'transparent',
              border: '2px solid #FFA726',
              borderStyle: 'dashed',
            }}>
              <Typography variant="h6" fontWeight={700} gutterBottom sx={{ color: '#FF6B35', mb: 3 }}>
                🔧 Advanced Options
              </Typography>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.imageOnly}
                        onChange={(e) => setConfig({ ...config, imageOnly: e.target.checked })}
                        color="warning"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2" fontWeight={600}>Image Only Mode</Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>
                          Generate using images only (Gemini images)
                        </Typography>
                      </Box>
                    }
                  />
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.fallbackOnly}
                        onChange={(e) => setConfig({ ...config, fallbackOnly: e.target.checked })}
                        color="warning"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2" fontWeight={600}>Fallback Only</Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>
                          Use fallback generation methods
                        </Typography>
                      </Box>
                    }
                  />
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.forceGeneration}
                        onChange={(e) => setConfig({ ...config, forceGeneration: e.target.checked })}
                        color="error"
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2" fontWeight={600}>Force Generation</Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>
                          Force generation even with quota warnings
                        </Typography>
                      </Box>
                    }
                  />
                </Grid>
                <Grid size={{ xs: 12, md: 6 }}>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={config.showDiscussionLogs}
                        onChange={(e) => setConfig({ ...config, showDiscussionLogs: e.target.checked })}
                      />
                    }
                    label={
                      <Box>
                        <Typography variant="body2" fontWeight={600}>Show Discussion Logs</Typography>
                        <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>
                          Show detailed AI discussion logs
                        </Typography>
                      </Box>
                    }
                  />
                </Grid>
              </Grid>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Cost Estimation */}
      {config.cheapMode && (
        <Alert 
          severity="info" 
          icon={<AttachMoney />}
          sx={{ mb: 4, borderRadius: 2 }}
        >
          <Typography variant="body2">
            <strong>Cost-Optimized Mode:</strong> Estimated cost ~${
              config.aiMode === 'simple' ? '0.05' : 
              config.aiMode === 'enhanced' ? '0.15' : '0.30'
            } per video
          </Typography>
        </Alert>
      )}

      {/* Action Buttons */}
      <Box sx={{ textAlign: 'center' }}>
        <Button
          variant="contained"
          size="large"
          startIcon={isGenerating ? <Stop /> : <PlayArrow />}
          onClick={handleGenerate}
          disabled={!config.mission}
          sx={{
            px: 6,
            py: 2,
            fontSize: '1.1rem',
            borderRadius: 50,
            minWidth: 250,
          }}
        >
          {isGenerating ? 'Stop Generation' : 'Generate Video'}
        </Button>
      </Box>

      {/* Generation Progress */}
      {isGenerating && (
        <Box sx={{ mt: 4 }}>
          <LinearProgress />
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1, textAlign: 'center' }}>
            Generating your video with {config.aiMode} AI mode...
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ContentGeneratorModern;