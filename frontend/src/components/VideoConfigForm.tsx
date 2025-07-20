import React, { useState } from 'react';
import {
  Card,
  CardContent,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Switch,
  FormControlLabel,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Typography,
  Box,
  Grid,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore,
  PlayArrow,
  Settings,
  TrendingUp,
  Security,
  VideoCall,
} from '@mui/icons-material';
import { VideoGenerationConfig } from '../types';

interface VideoConfigFormProps {
  onGenerate: (config: VideoGenerationConfig) => void;
  isGenerating: boolean;
}

const VideoConfigForm: React.FC<VideoConfigFormProps> = ({ onGenerate, isGenerating }) => {
  const [config, setConfig] = useState<VideoGenerationConfig>({
    mission: "Create engaging content about Hila Pinto's Ashtanga Yoga journey, balancing family life with spiritual practice",
    category: 'Educational',
    platform: 'instagram',
    duration: 25,
    imageOnly: false,
    fallbackOnly: false,
    force: false,
    skipAuthTest: false,
    discussions: 'enhanced',
    discussionLog: false,
    frameContinuity: 'auto',
    mode: 'enhanced',
  });

  const handleConfigChange = (key: keyof VideoGenerationConfig, value: any) => {
    setConfig(prev => ({ ...prev, [key]: value }));
  };

  const handleSubmit = () => {
    onGenerate(config);
  };

  const getSystemAgentCount = (mode: string) => {
    switch (mode) {
      case 'simple': return 3;
      case 'enhanced': return 7;
      case 'advanced': return 15;
      case 'professional': return 19;
      default: return 7;
    }
  };

  return (
    <Card className="w-full max-w-4xl mx-auto shadow-lg">
      <CardContent className="p-6">
        <Box className="flex items-center mb-6">
          <VideoCall className="text-primary-500 mr-3" fontSize="large" />
          <Typography variant="h4" className="font-bold text-gray-800">
            Video Configuration
          </Typography>
        </Box>

        <Grid container spacing={3}>
          {/* Mission/Topic */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Mission/Topic"
              multiline
              rows={3}
              value={config.mission}
              onChange={(e) => handleConfigChange('mission', e.target.value)}
              placeholder="Enter your video mission or topic..."
              variant="outlined"
              className="mb-4"
            />
          </Grid>

          {/* Platform and Category */}
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Platform</InputLabel>
              <Select
                value={config.platform}
                onChange={(e) => handleConfigChange('platform', e.target.value)}
                label="Platform"
              >
                <MenuItem value="instagram">Instagram</MenuItem>
                <MenuItem value="tiktok">TikTok</MenuItem>
                <MenuItem value="youtube">YouTube</MenuItem>
                <MenuItem value="twitter">Twitter</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Category</InputLabel>
              <Select
                value={config.category}
                onChange={(e) => handleConfigChange('category', e.target.value)}
                label="Category"
              >
                <MenuItem value="Educational">Educational</MenuItem>
                <MenuItem value="Comedy">Comedy</MenuItem>
                <MenuItem value="Entertainment">Entertainment</MenuItem>
                <MenuItem value="News">News</MenuItem>
                <MenuItem value="Tech">Tech</MenuItem>
                <MenuItem value="Health">Health</MenuItem>
                <MenuItem value="Lifestyle">Lifestyle</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Duration and AI System */}
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>Duration: {config.duration} seconds</Typography>
            <Slider
              value={config.duration}
              onChange={(_, value) => handleConfigChange('duration', value)}
              min={10}
              max={60}
              step={5}
              marks={[
                { value: 10, label: '10s' },
                { value: 30, label: '30s' },
                { value: 60, label: '60s' },
              ]}
            />
          </Grid>

          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>AI System Mode</InputLabel>
              <Select
                value={config.mode}
                onChange={(e) => handleConfigChange('mode', e.target.value)}
                label="AI System Mode"
              >
                <MenuItem value="simple">
                  Simple (3 agents)
                </MenuItem>
                <MenuItem value="enhanced">
                  Enhanced (7 agents)
                </MenuItem>
                <MenuItem value="advanced">
                  Advanced (15 agents)
                </MenuItem>
                <MenuItem value="professional">
                  Professional (19 agents)
                </MenuItem>
              </Select>
            </FormControl>
            <Box className="mt-2">
              <Chip 
                label={`${getSystemAgentCount(config.mode)} AI Agents`} 
                color="primary" 
                size="small" 
              />
            </Box>
          </Grid>

          {/* Advanced Options */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Settings className="mr-2" />
                <Typography>Advanced Options</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.imageOnly}
                          onChange={(e) => handleConfigChange('imageOnly', e.target.checked)}
                        />
                      }
                      label="Image Only Mode"
                    />
                    <Typography variant="caption" className="block text-gray-600">
                      Generate using images only (Gemini images)
                    </Typography>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.fallbackOnly}
                          onChange={(e) => handleConfigChange('fallbackOnly', e.target.checked)}
                        />
                      }
                      label="Fallback Only"
                    />
                    <Typography variant="caption" className="block text-gray-600">
                      Use fallback generation methods
                    </Typography>
                  </Grid>

                  <Grid item xs={12} md={4}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.force}
                          onChange={(e) => handleConfigChange('force', e.target.checked)}
                        />
                      }
                      label="Force Generation"
                    />
                    <Typography variant="caption" className="block text-gray-600">
                      Force generation even with quota warnings
                    </Typography>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Frame Continuity</InputLabel>
                      <Select
                        value={config.frameContinuity}
                        onChange={(e) => handleConfigChange('frameContinuity', e.target.value)}
                        label="Frame Continuity"
                      >
                        <MenuItem value="auto">Auto (AI decides)</MenuItem>
                        <MenuItem value="on">Always enabled</MenuItem>
                        <MenuItem value="off">Disabled</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <FormControl fullWidth>
                      <InputLabel>Discussion Mode</InputLabel>
                      <Select
                        value={config.discussions}
                        onChange={(e) => handleConfigChange('discussions', e.target.value)}
                        label="Discussion Mode"
                      >
                        <MenuItem value="off">Off</MenuItem>
                        <MenuItem value="light">Light</MenuItem>
                        <MenuItem value="standard">Standard</MenuItem>
                        <MenuItem value="deep">Deep</MenuItem>
                        <MenuItem value="streamlined">Streamlined</MenuItem>
                        <MenuItem value="enhanced">Enhanced (Recommended)</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.discussionLog}
                          onChange={(e) => handleConfigChange('discussionLog', e.target.checked)}
                        />
                      }
                      label="Show Detailed Discussion Logs"
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>

          {/* Content Customization */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <TrendingUp className="mr-2" />
                <Typography>Content Customization</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Target Audience"
                      value={config.targetAudience || ''}
                      onChange={(e) => handleConfigChange('targetAudience', e.target.value)}
                      placeholder="e.g., young adults, professionals"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Content Style"
                      value={config.style || ''}
                      onChange={(e) => handleConfigChange('style', e.target.value)}
                      placeholder="e.g., viral, educational, professional"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Content Tone"
                      value={config.tone || ''}
                      onChange={(e) => handleConfigChange('tone', e.target.value)}
                      placeholder="e.g., engaging, professional, humorous"
                    />
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Visual Style"
                      value={config.visualStyle || ''}
                      onChange={(e) => handleConfigChange('visualStyle', e.target.value)}
                      placeholder="e.g., dynamic, minimalist, professional"
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>

          {/* Authentication Options */}
          <Grid item xs={12}>
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Security className="mr-2" />
                <Typography>Authentication & Session</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12} md={6}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.skipAuthTest}
                          onChange={(e) => handleConfigChange('skipAuthTest', e.target.checked)}
                        />
                      }
                      label="Skip Authentication Test"
                    />
                    <Typography variant="caption" className="block text-gray-600 text-red-600">
                      Not recommended - may cause generation failures
                    </Typography>
                  </Grid>
                  <Grid item xs={12} md={6}>
                    <TextField
                      fullWidth
                      label="Custom Session ID"
                      value={config.sessionId || ''}
                      onChange={(e) => handleConfigChange('sessionId', e.target.value)}
                      placeholder="Leave empty for auto-generated"
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>
          </Grid>

          {/* Generate Button */}
          <Grid item xs={12}>
            <Box className="flex justify-center mt-6">
              <Tooltip title={isGenerating ? "Generation in progress..." : "Start video generation"}>
                <span>
                  <Button
                    variant="contained"
                    size="large"
                    onClick={handleSubmit}
                    disabled={isGenerating || !config.mission.trim()}
                    startIcon={<PlayArrow />}
                    className="px-8 py-3 text-lg font-semibold"
                    sx={{
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      '&:hover': {
                        background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
                      },
                    }}
                  >
                    {isGenerating ? 'Generating...' : 'Generate Video'}
                  </Button>
                </span>
              </Tooltip>
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};

export default VideoConfigForm;