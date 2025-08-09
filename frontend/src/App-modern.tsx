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
  Fab,
  Avatar,
  Badge,
  Stack,
  useMediaQuery,
  Paper,
  Grow,
  Fade,
  Zoom,
  Card,
  CardContent,
  LinearProgress,
  Skeleton,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Settings,
  Dashboard,
  Movie,
  Description,
  Subtitles,
  FormatColorText,
  VolumeUp,
  CloudSync,
  CheckCircle,
  Error,
  Warning,
  AutoAwesome,
  TrendingUp,
  Campaign,
  Analytics,
  PlayCircleOutline,
  DarkMode,
  LightMode,
  Notifications,
  AccountCircle,
  Add,
  Rocket,
  Psychology,
  SmartToy,
  Palette,
  WifiTethering,
  Circle,
} from '@mui/icons-material';

// Import M3 theme
import { m3Theme, m3DarkTheme } from './theme/m3-theme';

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
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({ open: false, message: '', severity: 'info' });
  
  // Use M3 theme based on dark mode
  const theme = useMemo(() => darkMode ? m3DarkTheme : m3Theme, [darkMode]);
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

  // Initialize connections and check server health
  useEffect(() => {
    initializeApp();
    return () => {
      websocketService.disconnect();
    };
  }, []);

  const initializeApp = async () => {
    try {
      // Check server health
      await checkServerHealth();
      setState(prev => ({ ...prev, serverHealth: true }));
      showNotification('🚀 System ready! AI engines online', 'success');

      // Initialize WebSocket connection
      await websocketService.connect();
      setState(prev => ({ ...prev, isConnected: true }));

      // Setup WebSocket event handlers
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
        showNotification('✨ Real-time sync activated', 'success');
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
      showNotification('🎉 Video generation complete!', 'success');
      setActiveTab('final');
    });

    websocketService.onError((error) => {
      showNotification(error, 'error');
    });
  };

  const handleGenerate = async (config: VideoGenerationConfig) => {
    try {
      // Create new session
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

      // Join WebSocket session
      websocketService.joinSession(session.id);

      // Start generation
      await apiService.startGeneration(session.id, config);
      showNotification('🚀 AI generation started!', 'info');
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
    const content = (() => {
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
                showNotification('Share functionality coming soon!', 'info');
              }}
            />
          );
        default:
          return null;
      }
    })();

    return (
      <Fade in timeout={300}>
        <Box>{content}</Box>
      </Fade>
    );
  };

  const getTabIcon = (tab: TabType) => {
    const icons = {
      config: <Settings />,
      progress: <Dashboard />,
      discussions: <Psychology />,
      video: <Movie />,
      audio: <VolumeUp />,
      script: <Description />,
      overlays: <Palette />,
      subtitles: <Subtitles />,
      final: <PlayCircleOutline />,
    };
    return icons[tab] || <Settings />;
  };

  const getConnectionStatus = () => {
    if (!state.serverHealth) return { icon: <Error />, color: 'error.main', pulse: false };
    if (!state.isConnected) return { icon: <Warning />, color: 'warning.main', pulse: false };
    return { icon: <WifiTethering />, color: 'success.main', pulse: true };
  };

  const connectionStatus = getConnectionStatus();

  const tabs: { key: TabType; label: string; icon: JSX.Element; disabled?: boolean }[] = [
    { key: 'config', label: 'Configuration', icon: <AutoAwesome /> },
    { key: 'progress', label: 'Progress', icon: <Dashboard />, disabled: !state.isGenerating && !state.progress },
    { key: 'discussions', label: 'AI Discussions', icon: <SmartToy />, disabled: state.discussions.length === 0 },
    { key: 'video', label: 'Video Clips', icon: <Movie />, disabled: state.videoClips.length === 0 },
    { key: 'audio', label: 'Audio', icon: <VolumeUp />, disabled: state.audioSegments.length === 0 },
    { key: 'script', label: 'Script', icon: <Description />, disabled: !state.script },
    { key: 'overlays', label: 'Overlays', icon: <Palette /> },
    { key: 'subtitles', label: 'Subtitles', icon: <Subtitles /> },
    { key: 'final', label: 'Final Video', icon: <PlayCircleOutline />, disabled: !state.finalVideo },
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ 
        flexGrow: 1, 
        minHeight: '100vh',
        background: darkMode 
          ? 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)'
          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}>
        {/* Modern App Bar with Glassmorphism */}
        <AppBar 
          position="sticky" 
          elevation={0} 
          sx={{ 
            backdropFilter: 'blur(20px)',
            backgroundColor: darkMode 
              ? 'rgba(28, 27, 31, 0.8)' 
              : 'rgba(255, 255, 255, 0.9)',
            borderBottom: '1px solid',
            borderColor: darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
          }}
        >
          <Toolbar sx={{ py: 1 }}>
            <IconButton
              edge="start"
              onClick={() => setDrawerOpen(true)}
              sx={{ 
                mr: 2,
                color: theme.palette.primary.main,
                '&:hover': {
                  transform: 'rotate(90deg)',
                  transition: 'transform 0.3s ease',
                }
              }}
            >
              <MenuIcon />
            </IconButton>
            
            <Stack direction="row" spacing={1} alignItems="center" sx={{ flexGrow: 1 }}>
              <Box sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 40,
                height: 40,
                borderRadius: '12px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
              }}>
                <Rocket sx={{ color: 'white' }} />
              </Box>
              <Box>
                <Typography 
                  variant="h6" 
                  sx={{ 
                    fontWeight: 600,
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    WebkitTextFillColor: 'transparent',
                  }}
                >
                  ViralAI Studio
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Advertising Automation Platform
                </Typography>
              </Box>
            </Stack>

            {/* Status Indicators */}
            <Stack direction="row" spacing={2} alignItems="center">
              {/* Connection Status with Animation */}
              <Tooltip title={
                !state.serverHealth ? 'Server offline' :
                !state.isConnected ? 'Reconnecting...' :
                'Connected'
              }>
                <Box sx={{ position: 'relative' }}>
                  {connectionStatus.pulse && (
                    <Circle
                      sx={{
                        position: 'absolute',
                        color: connectionStatus.color,
                        animation: 'pulse 2s infinite',
                        '@keyframes pulse': {
                          '0%': { transform: 'scale(0.95)', opacity: 1 },
                          '70%': { transform: 'scale(1.3)', opacity: 0 },
                          '100%': { transform: 'scale(0.95)', opacity: 0 },
                        },
                      }}
                    />
                  )}
                  <IconButton size="small" sx={{ color: connectionStatus.color }}>
                    {connectionStatus.icon}
                  </IconButton>
                </Box>
              </Tooltip>

              {/* Generation Status */}
              {state.isGenerating && (
                <Chip
                  icon={<AutoAwesome />}
                  label="AI Generating"
                  color="primary"
                  variant="filled"
                  sx={{
                    animation: 'glow 2s ease-in-out infinite',
                    '@keyframes glow': {
                      '0%, 100%': { boxShadow: '0 0 5px rgba(102, 126, 234, 0.5)' },
                      '50%': { boxShadow: '0 0 20px rgba(102, 126, 234, 0.8)' },
                    },
                  }}
                />
              )}

              {/* Dark Mode Toggle */}
              <IconButton 
                onClick={() => setDarkMode(!darkMode)}
                sx={{ 
                  color: theme.palette.primary.main,
                  transition: 'transform 0.3s ease',
                  '&:hover': { transform: 'rotate(180deg)' }
                }}
              >
                {darkMode ? <LightMode /> : <DarkMode />}
              </IconButton>

              {/* Notifications */}
              <IconButton sx={{ color: theme.palette.primary.main }}>
                <Badge badgeContent={3} color="error">
                  <Notifications />
                </Badge>
              </IconButton>

              {/* User Avatar */}
              <Avatar 
                sx={{ 
                  width: 36, 
                  height: 36,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)',
                }}
              >
                <AccountCircle />
              </Avatar>
            </Stack>
          </Toolbar>
          
          {/* Loading Progress */}
          {state.isGenerating && (
            <LinearProgress 
              variant="indeterminate" 
              sx={{ 
                height: 2,
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(90deg, #667eea 0%, #764ba2 50%, #667eea 100%)',
                  backgroundSize: '200% 100%',
                  animation: 'gradient 2s ease infinite',
                  '@keyframes gradient': {
                    '0%': { backgroundPosition: '0% 50%' },
                    '100%': { backgroundPosition: '200% 50%' },
                  },
                },
              }}
            />
          )}
        </AppBar>

        {/* Modern Navigation Drawer */}
        <Drawer
          anchor="left"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
          PaperProps={{
            sx: {
              width: 320,
              backgroundImage: 'none',
              backgroundColor: theme.palette.background.paper,
            }
          }}
        >
          <Box sx={{ p: 3 }}>
            <Stack direction="row" spacing={2} alignItems="center" sx={{ mb: 3 }}>
              <Box sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 48,
                height: 48,
                borderRadius: '16px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
              }}>
                <Rocket sx={{ color: 'white', fontSize: 28 }} />
              </Box>
              <Box>
                <Typography variant="h6" fontWeight={600}>
                  Navigation
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Video Generation Pipeline
                </Typography>
              </Box>
            </Stack>
            
            <Divider sx={{ mb: 2 }} />
            
            <List>
              {tabs.map((tab, index) => (
                <Zoom in style={{ transitionDelay: `${index * 50}ms` }} key={tab.key}>
                  <ListItemButton
                    selected={activeTab === tab.key}
                    disabled={tab.disabled}
                    onClick={() => {
                      setActiveTab(tab.key);
                      setDrawerOpen(false);
                    }}
                    sx={{
                      borderRadius: 3,
                      mb: 1,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        transform: 'translateX(8px)',
                      },
                      '&.Mui-selected': {
                        background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
                        borderLeft: '4px solid',
                        borderColor: theme.palette.primary.main,
                      },
                    }}
                  >
                    <ListItemIcon sx={{ color: activeTab === tab.key ? theme.palette.primary.main : 'inherit' }}>
                      {tab.icon}
                    </ListItemIcon>
                    <ListItemText 
                      primary={tab.label}
                      primaryTypographyProps={{
                        fontWeight: activeTab === tab.key ? 600 : 400,
                      }}
                    />
                    {activeTab === tab.key && (
                      <CheckCircle sx={{ color: theme.palette.primary.main, fontSize: 20 }} />
                    )}
                  </ListItemButton>
                </Zoom>
              ))}
            </List>

            <Divider sx={{ my: 2 }} />

            {/* Quick Actions */}
            <Typography variant="overline" color="text.secondary" sx={{ px: 2 }}>
              Quick Actions
            </Typography>
            <Stack spacing={1} sx={{ mt: 2 }}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<TrendingUp />}
                sx={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  fontWeight: 600,
                  py: 1.5,
                  borderRadius: 2,
                  '&:hover': {
                    background: 'linear-gradient(135deg, #5a67d8 0%, #6b4299 100%)',
                  }
                }}
              >
                View Analytics
              </Button>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<Campaign />}
                sx={{ py: 1.5, borderRadius: 2 }}
              >
                Manage Campaigns
              </Button>
            </Stack>
          </Box>
        </Drawer>

        {/* Main Content Area */}
        <Container maxWidth="xl" sx={{ py: 4, px: { xs: 2, sm: 3, md: 4 } }}>
          <Grow in timeout={500}>
            <Paper
              elevation={0}
              sx={{
                p: { xs: 2, sm: 3, md: 4 },
                borderRadius: 4,
                background: theme.palette.background.paper,
                backdropFilter: 'blur(20px)',
                border: '1px solid',
                borderColor: darkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
                minHeight: '70vh',
              }}
            >
              {renderTabContent()}
            </Paper>
          </Grow>
        </Container>

        {/* Floating Action Button */}
        {!state.isGenerating && activeTab === 'config' && (
          <Zoom in>
            <Fab
              color="primary"
              sx={{
                position: 'fixed',
                bottom: 24,
                right: 24,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4)',
                '&:hover': {
                  transform: 'scale(1.1)',
                  boxShadow: '0 12px 48px rgba(102, 126, 234, 0.6)',
                }
              }}
              onClick={() => showNotification('Quick action triggered!', 'info')}
            >
              <Add />
            </Fab>
          </Zoom>
        )}

        {/* Modern Notifications */}
        <Snackbar
          open={notification.open}
          autoHideDuration={4000}
          onClose={handleCloseNotification}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
          TransitionComponent={Zoom}
        >
          <Alert
            onClose={handleCloseNotification}
            severity={notification.severity}
            variant="filled"
            sx={{ 
              borderRadius: 2,
              boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
            }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;