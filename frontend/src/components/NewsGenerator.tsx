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
  CardActions,
  Chip,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Alert,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Tooltip,
  Tab,
  Tabs,
  Avatar,
} from '@mui/material';
import {
  Newspaper,
  Language,
  TrendingUp,
  Add,
  Delete,
  PlayArrow,
  Stop,
  Refresh,
  Link as LinkIcon,
  RssFeed,
  Telegram,
  Twitter,
  YouTube,
  Article,
  Public,
  CheckCircle,
  Error as ErrorIcon,
  Schedule,
  AutoAwesome,
  Source,
  Translate,
  VideoLibrary,
  Download,
} from '@mui/icons-material';

interface NewsSource {
  id: string;
  type: 'url' | 'rss' | 'telegram' | 'config';
  value: string;
  name: string;
  language?: string;
  enabled: boolean;
}

interface NewsConfig {
  sources: NewsSource[];
  aggregateMode: 'trending' | 'recent' | 'viral' | 'manual';
  outputLanguage: string;
  videoDuration: number;
  autoGenerate: boolean;
  includeAnalysis: boolean;
  voiceoverLanguage: string;
  platform: string;
}

interface NewsGeneratorProps {
  onGenerate?: (config: NewsConfig) => void;
  isGenerating?: boolean;
}

const NewsGenerator: React.FC<NewsGeneratorProps> = ({ onGenerate, isGenerating = false }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [config, setConfig] = useState<NewsConfig>({
    sources: [
      { id: '1', type: 'url', value: '', name: 'Custom URL', enabled: true },
    ],
    aggregateMode: 'trending',
    outputLanguage: 'en',
    videoDuration: 60,
    autoGenerate: false,
    includeAnalysis: true,
    voiceoverLanguage: 'en',
    platform: 'youtube',
  });

  const [newSourceUrl, setNewSourceUrl] = useState('');
  const [newSourceType, setNewSourceType] = useState<'url' | 'rss' | 'telegram' | 'config'>('url');

  const predefinedSources = [
    { name: 'BBC News', type: 'rss', value: 'http://feeds.bbci.co.uk/news/rss.xml', language: 'en' },
    { name: 'CNN Top Stories', type: 'rss', value: 'http://rss.cnn.com/rss/cnn_topstories.rss', language: 'en' },
    { name: 'Reuters', type: 'url', value: 'https://www.reuters.com', language: 'en' },
    { name: 'Al Jazeera', type: 'url', value: 'https://www.aljazeera.com', language: 'en' },
    { name: 'Tech News', type: 'config', value: 'tech_news_aggregator', language: 'en' },
    { name: 'Trending Twitter', type: 'config', value: 'twitter_trends', language: 'multi' },
  ];

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'ru', name: 'Russian' },
    { code: 'zh', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ar', name: 'Arabic' },
    { code: 'he', name: 'Hebrew' },
    { code: 'hi', name: 'Hindi' },
  ];

  const platforms = [
    { id: 'youtube', name: 'YouTube', icon: <YouTube /> },
    { id: 'tiktok', name: 'TikTok', icon: <VideoLibrary /> },
    { id: 'instagram', name: 'Instagram Reels', icon: <VideoLibrary /> },
    { id: 'twitter', name: 'Twitter/X', icon: <Twitter /> },
    { id: 'all', name: 'All Platforms', icon: <Public /> },
  ];

  const addSource = (source?: any) => {
    const newSource: NewsSource = {
      id: Date.now().toString(),
      type: source?.type || newSourceType,
      value: source?.value || newSourceUrl,
      name: source?.name || `Source ${config.sources.length + 1}`,
      language: source?.language,
      enabled: true,
    };

    setConfig({
      ...config,
      sources: [...config.sources, newSource],
    });
    setNewSourceUrl('');
  };

  const removeSource = (id: string) => {
    setConfig({
      ...config,
      sources: config.sources.filter(s => s.id !== id),
    });
  };

  const toggleSource = (id: string) => {
    setConfig({
      ...config,
      sources: config.sources.map(s => 
        s.id === id ? { ...s, enabled: !s.enabled } : s
      ),
    });
  };

  const updateSource = (id: string, value: string) => {
    setConfig({
      ...config,
      sources: config.sources.map(s => 
        s.id === id ? { ...s, value } : s
      ),
    });
  };

  const handleGenerate = () => {
    if (onGenerate) {
      onGenerate(config);
    }
  };

  const getSourceIcon = (type: string) => {
    switch (type) {
      case 'rss': return <RssFeed />;
      case 'telegram': return <Telegram />;
      case 'config': return <AutoAwesome />;
      default: return <LinkIcon />;
    }
  };

  return (
    <Box>
      <Paper elevation={0} sx={{ 
        p: 3, 
        border: '2px solid', 
        borderColor: '#E5E7EB', 
        backgroundColor: 'transparent',
        backgroundImage: 'none'
      }}>
        <Stack spacing={3}>
          {/* Header */}
          <Box>
            <Stack direction="row" alignItems="center" spacing={2}>
              <Newspaper sx={{ fontSize: 32, color: 'primary.main' }} />
              <Box>
                <Typography variant="h5" fontWeight={600}>
                  News Video Generator
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Aggregate news from multiple sources and create viral video content
                </Typography>
              </Box>
            </Stack>
          </Box>

          <Divider />

          {/* Tabs */}
          <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)}>
            <Tab label="Sources" icon={<Source />} iconPosition="start" />
            <Tab label="Configuration" icon={<Article />} iconPosition="start" />
            <Tab label="Templates" icon={<AutoAwesome />} iconPosition="start" />
          </Tabs>

          {/* Tab Content */}
          {activeTab === 0 && (
            <Stack spacing={3}>
              {/* Quick Add Predefined Sources */}
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Quick Add Popular Sources
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" sx={{ gap: 1 }}>
                  {predefinedSources.map((source) => (
                    <Chip
                      key={source.value}
                      label={source.name}
                      icon={getSourceIcon(source.type)}
                      onClick={() => addSource(source)}
                      variant="outlined"
                      clickable
                    />
                  ))}
                </Stack>
              </Box>

              {/* Add Custom Source */}
              <Paper variant="outlined" sx={{ 
                p: 2, 
                backgroundColor: 'transparent', 
                border: '2px solid #E5E7EB',
                backgroundImage: 'none'
              }}>
                <Stack spacing={2}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#111827' }}>Add Custom Source</Typography>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={3}>
                      <FormControl fullWidth size="small">
                        <InputLabel sx={{ fontWeight: 500 }}>Type</InputLabel>
                        <Select
                          value={newSourceType}
                          onChange={(e) => setNewSourceType(e.target.value as any)}
                          label="Type"
                        >
                          <MenuItem value="url">URL</MenuItem>
                          <MenuItem value="rss">RSS Feed</MenuItem>
                          <MenuItem value="telegram">Telegram Channel</MenuItem>
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={7}>
                      <TextField
                        fullWidth
                        size="small"
                        label="Source URL or Channel"
                        value={newSourceUrl}
                        onChange={(e) => setNewSourceUrl(e.target.value)}
                        placeholder={
                          newSourceType === 'telegram' 
                            ? '@channelname' 
                            : 'https://example.com'
                        }
                      />
                    </Grid>
                    <Grid item xs={12} sm={2}>
                      <Button
                        fullWidth
                        variant="contained"
                        onClick={() => addSource()}
                        startIcon={<Add />}
                        disabled={!newSourceUrl}
                      >
                        Add
                      </Button>
                    </Grid>
                  </Grid>
                </Stack>
              </Paper>

              {/* Active Sources */}
              <Box>
                <Typography variant="subtitle2" gutterBottom>
                  Active Sources ({config.sources.filter(s => s.enabled).length}/{config.sources.length})
                </Typography>
                <List>
                  {config.sources.map((source) => (
                    <ListItem
                      key={source.id}
                      secondaryAction={
                        <Stack direction="row" spacing={1}>
                          <Switch
                            checked={source.enabled}
                            onChange={() => toggleSource(source.id)}
                            size="small"
                          />
                          <IconButton
                            size="small"
                            onClick={() => removeSource(source.id)}
                          >
                            <Delete />
                          </IconButton>
                        </Stack>
                      }
                    >
                      <ListItemIcon>
                        {getSourceIcon(source.type)}
                      </ListItemIcon>
                      <ListItemText
                        primary={source.name}
                        secondary={
                          <Stack direction="row" spacing={1} alignItems="center">
                            <Typography variant="caption">{source.value || 'No URL set'}</Typography>
                            {source.language && (
                              <Chip label={source.language} size="small" />
                            )}
                          </Stack>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>
            </Stack>
          )}

          {activeTab === 1 && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Stack spacing={3}>
                  {/* Aggregation Mode */}
                  <FormControl fullWidth>
                    <InputLabel>Aggregation Mode</InputLabel>
                    <Select
                      value={config.aggregateMode}
                      onChange={(e) => setConfig({ ...config, aggregateMode: e.target.value as any })}
                      label="Aggregation Mode"
                    >
                      <MenuItem value="trending">
                        <Stack direction="row" spacing={1} alignItems="center">
                          <TrendingUp fontSize="small" />
                          <span>Trending Topics</span>
                        </Stack>
                      </MenuItem>
                      <MenuItem value="recent">Recent News</MenuItem>
                      <MenuItem value="viral">Viral Potential</MenuItem>
                      <MenuItem value="manual">Manual Selection</MenuItem>
                    </Select>
                  </FormControl>

                  {/* Output Language */}
                  <FormControl fullWidth>
                    <InputLabel>Output Language</InputLabel>
                    <Select
                      value={config.outputLanguage}
                      onChange={(e) => setConfig({ ...config, outputLanguage: e.target.value })}
                      label="Output Language"
                    >
                      {languages.map(lang => (
                        <MenuItem key={lang.code} value={lang.code}>
                          {lang.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  {/* Platform */}
                  <FormControl fullWidth>
                    <InputLabel>Target Platform</InputLabel>
                    <Select
                      value={config.platform}
                      onChange={(e) => setConfig({ ...config, platform: e.target.value })}
                      label="Target Platform"
                    >
                      {platforms.map(platform => (
                        <MenuItem key={platform.id} value={platform.id}>
                          <Stack direction="row" spacing={1} alignItems="center">
                            {platform.icon}
                            <span>{platform.name}</span>
                          </Stack>
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Stack>
              </Grid>

              <Grid item xs={12} md={6}>
                <Stack spacing={3}>
                  {/* Video Duration */}
                  <TextField
                    fullWidth
                    type="number"
                    label="Video Duration (seconds)"
                    value={config.videoDuration}
                    onChange={(e) => setConfig({ ...config, videoDuration: parseInt(e.target.value) })}
                    InputProps={{
                      inputProps: { min: 15, max: 300 }
                    }}
                  />

                  {/* Voiceover Language */}
                  <FormControl fullWidth>
                    <InputLabel>Voiceover Language</InputLabel>
                    <Select
                      value={config.voiceoverLanguage}
                      onChange={(e) => setConfig({ ...config, voiceoverLanguage: e.target.value })}
                      label="Voiceover Language"
                    >
                      {languages.map(lang => (
                        <MenuItem key={lang.code} value={lang.code}>
                          {lang.name}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>

                  {/* Options */}
                  <Box>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.includeAnalysis}
                          onChange={(e) => setConfig({ ...config, includeAnalysis: e.target.checked })}
                        />
                      }
                      label="Include AI Analysis"
                    />
                    <FormControlLabel
                      control={
                        <Switch
                          checked={config.autoGenerate}
                          onChange={(e) => setConfig({ ...config, autoGenerate: e.target.checked })}
                        />
                      }
                      label="Auto-generate on schedule"
                    />
                  </Box>
                </Stack>
              </Grid>
            </Grid>
          )}

          {activeTab === 2 && (
            <Grid container spacing={2}>
              {['Breaking News', 'Daily Digest', 'Tech Roundup', 'Viral Trends'].map((template) => (
                <Grid item xs={12} sm={6} md={4} key={template}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        {template}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        Pre-configured template for {template.toLowerCase()} videos
                      </Typography>
                    </CardContent>
                    <CardActions>
                      <Button size="small" startIcon={<PlayArrow />}>
                        Use Template
                      </Button>
                    </CardActions>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}

          <Divider />

          {/* Action Buttons */}
          <Stack direction="row" spacing={2} justifyContent="flex-end">
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              disabled={isGenerating}
            >
              Test Sources
            </Button>
            <Button
              variant="contained"
              startIcon={isGenerating ? <Stop /> : <PlayArrow />}
              onClick={handleGenerate}
              disabled={config.sources.filter(s => s.enabled).length === 0}
              sx={{
                background: isGenerating 
                  ? 'linear-gradient(45deg, #ff6b6b 30%, #ff8787 90%)'
                  : 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
              }}
            >
              {isGenerating ? 'Stop Generation' : 'Generate News Video'}
            </Button>
          </Stack>

          {/* Status */}
          {isGenerating && (
            <Box>
              <LinearProgress />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Aggregating news from {config.sources.filter(s => s.enabled).length} sources...
              </Typography>
            </Box>
          )}
        </Stack>
      </Paper>
    </Box>
  );
};

export default NewsGenerator;