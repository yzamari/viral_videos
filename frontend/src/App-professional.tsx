import { useState, useEffect, useMemo } from 'react';
import {
  ThemeProvider,
  CssBaseline,
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Snackbar,
  Alert,
  Chip,
  Tooltip,
  Drawer,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
  Avatar,
  Badge,
  Stack,
  useMediaQuery,
  Paper,
  LinearProgress,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Settings,
  Dashboard,
  Movie,
  Description,
  Subtitles,
  Palette,
  VolumeUp,
  CheckCircle,
  Error as ErrorIcon,
  Warning,
  TrendingUp,
  Campaign,
  PlayCircleOutline,
  DarkMode,
  LightMode,
  Notifications,
  AccountCircle,
  MoreVert,
  FiberManualRecord,
  Business,
  AutoGraph,
  VideoLibrary,
  MusicNote,
  TextFields,
  Layers,
  ClosedCaption,
} from '@mui/icons-material';

// Import professional theme
import { professionalTheme, professionalDarkTheme } from './theme/professional-theme';

// Import our components
import VideoConfigForm from './components/VideoConfigForm';
import ProgressMonitor from './components/ProgressMonitor';
import AIDiscussions from './components/AIDiscussions';
import VideoClipsViewer from './components/VideoClipsViewer';
import AudioViewer from './components/AudioViewer';
import ScriptEditor from './components/ScriptEditor';
import OverlayEditor from './components/OverlayEditor';
import SubtitleEditor from './components/SubtitleEditor';
import FinalVideoViewer from './components/FinalVideoViewer';

// Import services
import { websocketService } from './services/websocket';
import { apiService, checkServerHealth } from './services/api';

// Import types
import type {
  VideoGenerationConfig,
  GenerationSession,
  GenerationProgress,
  AgentDiscussion,
  VideoClip,
  AudioSegment,
  Script,
  Overlay,
  Subtitle,
  FinalVideo,
} from './types';

type TabType = 'config' | 'progress' | 'discussions' | 'video' | 'audio' | 'script' | 'overlays' | 'subtitles' | 'final';

interface AppState {
  currentSession: GenerationSession | null;
  isGenerating: boolean;
  progress: GenerationProgress | null;
  discussions: AgentDiscussion[];
  videoClips: VideoClip[];
  audioSegments: AudioSegment[];
  script: Script | null;
  overlays: Overlay[];
  subtitles: Subtitle[];
  finalVideo: FinalVideo | null;
  isConnected: boolean;
  serverHealth: boolean;
}

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('config');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({ open: false, message: '', severity: 'info' });
  
  // Use professional theme
  const theme = useMemo(() => darkMode ? professionalDarkTheme : professionalTheme, [darkMode]);
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  
  useEffect(() => {
    setDarkMode(prefersDarkMode);
  }, [prefersDarkMode]);

  const [state, setState] = useState<AppState>({
    currentSession: null,
    isGenerating: false,
    progress: null,
    discussions: [],
    videoClips: [],
    audioSegments: [],
    script: null,
    overlays: [],
    subtitles: [],
    finalVideo: null,
    isConnected: false,
    serverHealth: false,
  });

  // Initialize connections
  useEffect(() => {
    initializeApp();
    return () => {
      websocketService.disconnect();
    };
  }, []);

  const initializeApp = async () => {
    try {
      await checkServerHealth();
      setState(prev => ({ ...prev, serverHealth: true }));
      showNotification('System connected successfully', 'success');

      await websocketService.connect();
      setState(prev => ({ ...prev, isConnected: true }));
      setupWebSocketHandlers();

    } catch (error) {
      console.error('Failed to initialize app:', error);
      showNotification('Connection failed - Check server status', 'error');
      setState(prev => ({ ...prev, serverHealth: false, isConnected: false }));
    }
  };

  const setupWebSocketHandlers = () => {
    websocketService.onConnectionChange((connected) => {
      setState(prev => ({ ...prev, isConnected: connected }));
      if (connected) {
        showNotification('Real-time connection established', 'success');
      } else {
        showNotification('Connection interrupted', 'warning');
      }
    });

    websocketService.onProgressUpdate((progress) => {
      setState(prev => ({ ...prev, progress }));
    });

    websocketService.onAgentDiscussion((discussion) => {
      setState(prev => ({
        ...prev,
        discussions: [...prev.discussions.filter(d => d.id !== discussion.id), discussion]
      }));
    });

    websocketService.onVideoClipUpdate((clip) => {
      setState(prev => ({
        ...prev,
        videoClips: [...prev.videoClips.filter(c => c.id !== clip.id), clip]
      }));
    });

    websocketService.onAudioUpdate((audio) => {
      setState(prev => ({
        ...prev,
        audioSegments: [...prev.audioSegments.filter(a => a.id !== audio.id), audio]
      }));
    });

    websocketService.onScriptUpdate((script) => {
      setState(prev => ({ ...prev, script }));
    });

    websocketService.onOverlayUpdate((overlays) => {
      setState(prev => ({ ...prev, overlays }));
    });

    websocketService.onSubtitleUpdate((subtitles) => {
      setState(prev => ({ ...prev, subtitles }));
    });

    websocketService.onGenerationComplete((session) => {
      setState(prev => ({
        ...prev,
        currentSession: session,
        isGenerating: false,
        finalVideo: session.finalVideo || null
      }));
      showNotification('Video generation completed successfully', 'success');
      setActiveTab('final');
    });

    websocketService.onError((error) => {
      showNotification(error, 'error');
    });
  };

  const handleGenerate = async (config: VideoGenerationConfig) => {
    try {
      const session = await apiService.createSession(config);
      setState(prev => ({ 
        ...prev, 
        currentSession: session,
        isGenerating: true,
        progress: null,
        discussions: [],
        videoClips: [],
        audioSegments: [],
        script: null,
        overlays: [],
        subtitles: [],
        finalVideo: null
      }));

      websocketService.joinSession(session.id);
      await apiService.startGeneration(session.id, config);
      showNotification('Generation process started', 'info');
      setActiveTab('progress');

    } catch (error: any) {
      console.error('Failed to start generation:', error);
      showNotification(`Failed to start: ${error.message}`, 'error');
      setState(prev => ({ ...prev, isGenerating: false }));
    }
  };

  const handleStopGeneration = async () => {
    if (!state.currentSession) return;

    try {
      await apiService.stopGeneration(state.currentSession.id);
      setState(prev => ({ ...prev, isGenerating: false }));
      showNotification('Generation stopped', 'info');
    } catch (error: any) {
      console.error('Failed to stop generation:', error);
      showNotification(`Failed to stop: ${error.message}`, 'error');
    }
  };

  const handleScriptUpdate = async (script: Script) => {
    if (!state.currentSession) return;

    try {
      await apiService.updateScript(state.currentSession.id, script);
      setState(prev => ({ ...prev, script }));
      websocketService.updateScript(script);
      showNotification('Script updated', 'success');
    } catch (error: any) {
      console.error('Failed to update script:', error);
      showNotification(`Failed to update script: ${error.message}`, 'error');
    }
  };

  const handleOverlaysUpdate = async (overlays: Overlay[]) => {
    if (!state.currentSession) return;

    try {
      await apiService.updateOverlays(state.currentSession.id, overlays);
      setState(prev => ({ ...prev, overlays }));
      websocketService.updateOverlays(overlays);
      showNotification('Overlays updated', 'success');
    } catch (error: any) {
      console.error('Failed to update overlays:', error);
      showNotification(`Failed to update overlays: ${error.message}`, 'error');
    }
  };

  const handleSubtitlesUpdate = async (subtitles: Subtitle[]) => {
    if (!state.currentSession) return;

    try {
      await apiService.updateSubtitles(state.currentSession.id, subtitles);
      setState(prev => ({ ...prev, subtitles }));
      websocketService.updateSubtitles(subtitles);
      showNotification('Subtitles updated', 'success');
    } catch (error: any) {
      console.error('Failed to update subtitles:', error);
      showNotification(`Failed to update subtitles: ${error.message}`, 'error');
    }
  };

  const showNotification = (message: string, severity: 'success' | 'error' | 'warning' | 'info') => {
    setNotification({ open: true, message, severity });
  };

  const handleCloseNotification = () => {
    setNotification(prev => ({ ...prev, open: false }));
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'config':
        return (
          <VideoConfigForm
            onGenerate={handleGenerate}
            isGenerating={state.isGenerating}
          />
        );
      case 'progress':
        return (
          <ProgressMonitor
            progress={state.progress}
            isGenerating={state.isGenerating}
          />
        );
      case 'discussions':
        return (
          <AIDiscussions
            discussions={state.discussions}
            isGenerating={state.isGenerating}
          />
        );
      case 'video':
        return (
          <VideoClipsViewer
            videoClips={state.videoClips}
            isGenerating={state.isGenerating}
          />
        );
      case 'audio':
        return (
          <AudioViewer
            audioSegments={state.audioSegments}
            isGenerating={state.isGenerating}
          />
        );
      case 'script':
        return (
          <ScriptEditor
            script={state.script}
            onScriptUpdate={handleScriptUpdate}
            isGenerating={state.isGenerating}
          />
        );
      case 'overlays':
        return (
          <OverlayEditor
            overlays={state.overlays}
            onOverlaysUpdate={handleOverlaysUpdate}
            videoDuration={state.finalVideo?.duration || 60}
          />
        );
      case 'subtitles':
        return (
          <SubtitleEditor
            subtitles={state.subtitles}
            onSubtitlesUpdate={handleSubtitlesUpdate}
            videoDuration={state.finalVideo?.duration || 60}
          />
        );
      case 'final':
        return (
          <FinalVideoViewer
            finalVideo={state.finalVideo}
            isGenerating={state.isGenerating}
            sessionConfig={state.currentSession?.config}
            onDownload={(video) => {
              if (state.currentSession) {
                apiService.downloadVideo(state.currentSession.id, `${state.currentSession.id}.mp4`);
              }
            }}
            onShare={(video) => {
              showNotification('Share functionality coming soon', 'info');
            }}
          />
        );
      default:
        return null;
    }
  };

  const tabs: { key: TabType; label: string; icon: JSX.Element; disabled?: boolean }[] = [
    { key: 'config', label: 'Configuration', icon: <Settings /> },
    { key: 'progress', label: 'Progress', icon: <Dashboard />, disabled: !state.isGenerating && !state.progress },
    { key: 'discussions', label: 'AI Analysis', icon: <AutoGraph />, disabled: state.discussions.length === 0 },
    { key: 'video', label: 'Video Clips', icon: <VideoLibrary />, disabled: state.videoClips.length === 0 },
    { key: 'audio', label: 'Audio', icon: <MusicNote />, disabled: state.audioSegments.length === 0 },
    { key: 'script', label: 'Script', icon: <TextFields />, disabled: !state.script },
    { key: 'overlays', label: 'Overlays', icon: <Layers /> },
    { key: 'subtitles', label: 'Subtitles', icon: <ClosedCaption /> },
    { key: 'final', label: 'Final Output', icon: <PlayCircleOutline />, disabled: !state.finalVideo },
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        display: 'flex', 
        flexDirection: 'column',
        minHeight: '100vh',
        backgroundColor: theme.palette.background.default,
      }}>
        {/* Clean App Bar */}
        <AppBar 
          position="sticky" 
          elevation={0}
          sx={{ 
            backgroundColor: theme.palette.background.paper,
            borderBottom: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Toolbar>
            <IconButton
              edge="start"
              onClick={() => setDrawerOpen(true)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            
            <Stack direction="row" spacing={2} alignItems="center" sx={{ flexGrow: 1 }}>
              <Business sx={{ color: theme.palette.primary.main }} />
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600, color: theme.palette.text.primary }}>
                  ViralAI Platform
                </Typography>
                <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
                  Advertising Automation System
                </Typography>
              </Box>
            </Stack>

            {/* Status Section */}
            <Stack direction="row" spacing={2} alignItems="center">
              {/* Connection Status */}
              <Chip
                size="small"
                icon={
                  state.serverHealth ? (
                    <FiberManualRecord sx={{ fontSize: 12 }} />
                  ) : (
                    <ErrorIcon sx={{ fontSize: 16 }} />
                  )
                }
                label={state.isConnected ? 'Connected' : 'Offline'}
                color={state.serverHealth ? 'success' : 'default'}
                variant="outlined"
              />

              {/* Generation Status */}
              {state.isGenerating && (
                <Chip
                  size="small"
                  label="Processing"
                  color="primary"
                  variant="filled"
                />
              )}

              {/* Dark Mode */}
              <IconButton 
                onClick={() => setDarkMode(!darkMode)}
                size="small"
              >
                {darkMode ? <LightMode /> : <DarkMode />}
              </IconButton>

              {/* Notifications */}
              <IconButton size="small">
                <Badge badgeContent={0} color="error">
                  <Notifications />
                </Badge>
              </IconButton>

              {/* User Menu */}
              <IconButton 
                onClick={(e) => setAnchorEl(e.currentTarget)}
                size="small"
              >
                <AccountCircle />
              </IconButton>
              
              <Menu
                anchorEl={anchorEl}
                open={Boolean(anchorEl)}
                onClose={() => setAnchorEl(null)}
              >
                <MenuItem onClick={() => setAnchorEl(null)}>Profile</MenuItem>
                <MenuItem onClick={() => setAnchorEl(null)}>Settings</MenuItem>
                <Divider />
                <MenuItem onClick={() => setAnchorEl(null)}>Sign Out</MenuItem>
              </Menu>
            </Stack>
          </Toolbar>
          
          {/* Progress Bar */}
          {state.isGenerating && (
            <LinearProgress variant="indeterminate" sx={{ height: 2 }} />
          )}
        </AppBar>

        {/* Navigation Drawer */}
        <Drawer
          anchor="left"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          PaperProps={{
            sx: {
              width: 280,
              backgroundColor: theme.palette.background.paper,
            }
          }}
        >
          <Box sx={{ p: 2 }}>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
              <Business sx={{ color: theme.palette.primary.main, fontSize: 32 }} />
              <Typography variant="h6" fontWeight={600}>
                Navigation
              </Typography>
            </Stack>
            
            <Divider sx={{ mb: 2 }} />
            
            <List>
              {tabs.map((tab) => (
                <ListItemButton
                  key={tab.key}
                  selected={activeTab === tab.key}
                  disabled={tab.disabled}
                  onClick={() => {
                    setActiveTab(tab.key);
                    setDrawerOpen(false);
                  }}
                  sx={{ mb: 0.5 }}
                >
                  <ListItemIcon sx={{ minWidth: 40, color: activeTab === tab.key ? theme.palette.primary.main : 'inherit' }}>
                    {tab.icon}
                  </ListItemIcon>
                  <ListItemText 
                    primary={tab.label}
                    primaryTypographyProps={{
                      fontSize: '0.9rem',
                      fontWeight: activeTab === tab.key ? 600 : 400,
                    }}
                  />
                  {activeTab === tab.key && (
                    <CheckCircle sx={{ color: theme.palette.primary.main, fontSize: 18 }} />
                  )}
                </ListItemButton>
              ))}
            </List>

            <Divider sx={{ my: 2 }} />

            {/* Quick Actions */}
            <Stack spacing={1}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<TrendingUp />}
                sx={{ justifyContent: 'flex-start' }}
              >
                Analytics
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Campaign />}
                sx={{ justifyContent: 'flex-start' }}
              >
                Campaigns
              </Button>
            </Stack>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Container maxWidth="xl" sx={{ py: 3, flexGrow: 1 }}>
          <Paper
            elevation={0}
            sx={{
              p: 3,
              borderRadius: 2,
              border: `1px solid ${theme.palette.divider}`,
              backgroundColor: theme.palette.background.paper,
              minHeight: '60vh',
            }}
          >
            {renderTabContent()}
          </Paper>
        </Container>

        {/* Notifications */}
        <Snackbar
          open={notification.open}
          autoHideDuration={4000}
          onClose={handleCloseNotification}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            onClose={handleCloseNotification}
            severity={notification.severity}
            variant="filled"
            sx={{ borderRadius: 1 }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;