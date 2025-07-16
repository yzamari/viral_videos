import { useState, useEffect } from 'react';
import {
  ThemeProvider,
  createTheme,
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
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
} from '@mui/material';
import {
  VideoCall,
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
} from '@mui/icons-material';

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

// Create Material-UI theme
const theme = createTheme({
  palette: {
    primary: {
      main: '#0ea5e9',
      light: '#38bdf8',
      dark: '#0284c7',
    },
    secondary: {
      main: '#8b5cf6',
    },
    background: {
      default: '#f8fafc',
      paper: '#ffffff',
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, sans-serif',
    h4: {
      fontWeight: 700,
    },
    h5: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 600,
    },
  },
  shape: {
    borderRadius: 12,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        },
      },
    },
  },
});

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
  const [notification, setNotification] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'warning' | 'info';
  }>({ open: false, message: '', severity: 'info' });

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
      showNotification('Server connected successfully', 'success');

      // Initialize WebSocket connection
      await websocketService.connect();
      setState(prev => ({ ...prev, isConnected: true }));

      // Setup WebSocket event handlers
      setupWebSocketHandlers();

    } catch (error) {
      console.error('Failed to initialize app:', error);
      showNotification('Failed to connect to server', 'error');
      setState(prev => ({ ...prev, serverHealth: false, isConnected: false }));
    }
  };

  const setupWebSocketHandlers = () => {
    websocketService.onConnectionChange((connected) => {
      setState(prev => ({ ...prev, isConnected: connected }));
      if (connected) {
        showNotification('Real-time connection established', 'success');
      } else {
        showNotification('Real-time connection lost', 'warning');
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
      showNotification('Video generation completed!', 'success');
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
      showNotification('Video generation started!', 'info');
      setActiveTab('progress');

    } catch (error: any) {
      console.error('Failed to start generation:', error);
      showNotification(`Failed to start generation: ${error.message}`, 'error');
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
      showNotification(`Failed to stop generation: ${error.message}`, 'error');
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
              showNotification('Share functionality coming soon!', 'info');
            }}
          />
        );
      default:
        return null;
    }
  };

  const getTabIcon = (tab: TabType) => {
    switch (tab) {
      case 'config': return <Settings />;
      case 'progress': return <Dashboard />;
      case 'discussions': return <VideoCall />;
      case 'video': return <Movie />;
      case 'audio': return <VolumeUp />;
      case 'script': return <Description />;
      case 'overlays': return <FormatColorText />;
      case 'subtitles': return <Subtitles />;
      case 'final': return <CheckCircle />;
      default: return <Settings />;
    }
  };

  const getConnectionStatusIcon = () => {
    if (!state.serverHealth) {
      return <Error className="text-red-500" />;
    }
    if (!state.isConnected) {
      return <Warning className="text-yellow-500" />;
    }
    return <CheckCircle className="text-green-500" />;
  };

  const tabs: { key: TabType; label: string; disabled?: boolean }[] = [
    { key: 'config', label: 'Configuration' },
    { key: 'progress', label: 'Progress', disabled: !state.isGenerating && !state.progress },
    { key: 'discussions', label: 'AI Discussions', disabled: state.discussions.length === 0 },
    { key: 'video', label: 'Video Clips', disabled: state.videoClips.length === 0 },
    { key: 'audio', label: 'Audio', disabled: state.audioSegments.length === 0 },
    { key: 'script', label: 'Script', disabled: !state.script },
    { key: 'overlays', label: 'Overlays' },
    { key: 'subtitles', label: 'Subtitles' },
    { key: 'final', label: 'Final Video', disabled: !state.finalVideo },
  ];

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1, minHeight: '100vh', backgroundColor: '#f8fafc' }}>
        {/* App Bar */}
        <AppBar position="static" elevation={0} sx={{ backgroundColor: 'white', borderBottom: '1px solid #e2e8f0' }}>
          <Toolbar>
            <IconButton
              edge="start"
              color="primary"
              onClick={() => setDrawerOpen(true)}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            
            <VideoCall sx={{ mr: 2, color: '#0ea5e9' }} />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: '#1e293b', fontWeight: 700 }}>
              Viral AI Video Generator
            </Typography>

            {/* Connection Status */}
            <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
              <Tooltip title={
                !state.serverHealth ? 'Server disconnected' :
                !state.isConnected ? 'Real-time connection lost' :
                'Connected'
              }>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  {getConnectionStatusIcon()}
                  <Typography variant="body2" sx={{ ml: 1, color: '#64748b' }}>
                    {state.isConnected ? 'Connected' : 'Disconnected'}
                  </Typography>
                </Box>
              </Tooltip>
            </Box>

            {/* Generation Status */}
            {state.isGenerating && (
              <Box sx={{ display: 'flex', alignItems: 'center', mr: 2 }}>
                <CloudSync className="animate-pulse text-blue-500 mr-2" />
                <Chip
                  label="Generating"
                  color="primary"
                  size="small"
                  variant="outlined"
                />
                <Button
                  onClick={handleStopGeneration}
                  size="small"
                  color="error"
                  sx={{ ml: 1 }}
                >
                  Stop
                </Button>
              </Box>
            )}
          </Toolbar>
        </AppBar>

        {/* Navigation Drawer */}
        <Drawer
          anchor="left"
          open={drawerOpen}
          onClose={() => setDrawerOpen(false)}
        >
          <Box sx={{ width: 300, p: 2 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Navigation
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <List>
              {tabs.map((tab) => (
                <ListItem
                  key={tab.key}
                  button
                  selected={activeTab === tab.key}
                  disabled={tab.disabled}
                  onClick={() => {
                    setActiveTab(tab.key);
                    setDrawerOpen(false);
                  }}
                  sx={{
                    borderRadius: 2,
                    mb: 1,
                    '&.Mui-selected': {
                      backgroundColor: '#e0f2fe',
                      '&:hover': {
                        backgroundColor: '#b3e5fc',
                      },
                    },
                  }}
                >
                  <ListItemIcon>
                    {getTabIcon(tab.key)}
                  </ListItemIcon>
                  <ListItemText primary={tab.label} />
                </ListItem>
              ))}
            </List>
          </Box>
        </Drawer>

        {/* Main Content */}
        <Container maxWidth="xl" sx={{ py: 4 }}>
          {renderTabContent()}
        </Container>

        {/* Notifications */}
        <Snackbar
          open={notification.open}
          autoHideDuration={6000}
          onClose={handleCloseNotification}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            onClose={handleCloseNotification}
            severity={notification.severity}
            variant="filled"
            sx={{ width: '100%' }}
          >
            {notification.message}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App;