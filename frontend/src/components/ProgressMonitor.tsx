import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Box,
  Grid,
  Avatar,
  Chip,
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  PlayArrow,
  CheckCircle,
  RadioButtonChecked,
  Schedule,
  Group,
  Chat,
  TrendingUp,
  Psychology,
  VideoLibrary,
  MusicNote,
  Subtitles,
  Movie,
  Download,
  Settings,
  AutoAwesome,
  Palette,
} from '@mui/icons-material';
import { GenerationProgress, AgentStatus } from '../types';

interface ProgressMonitorProps {
  progress: GenerationProgress | null;
  isGenerating: boolean;
}

const ProgressMonitor: React.FC<ProgressMonitorProps> = ({ progress, isGenerating }) => {
  // Define the processing steps
  const processingSteps = [
    {
      id: 'initialization',
      label: 'Initialization',
      description: 'Setting up AI agents and analyzing requirements',
      icon: <Settings />,
      phases: ['initializing', 'setup']
    },
    {
      id: 'discussion',
      label: 'AI Discussion',
      description: '22 AI agents discussing and planning the video',
      icon: <Psychology />,
      phases: ['discussion', 'planning', 'analysis']
    },
    {
      id: 'script',
      label: 'Script Generation',
      description: 'Creating the video script and narrative',
      icon: <AutoAwesome />,
      phases: ['scripting', 'writing', 'narrative']
    },
    {
      id: 'video',
      label: 'Video Generation',
      description: 'AI generating video clips and visual content',
      icon: <VideoLibrary />,
      phases: ['video_generation', 'visual_creation', 'rendering']
    },
    {
      id: 'audio',
      label: 'Audio Production',
      description: 'Creating voiceover and background music',
      icon: <MusicNote />,
      phases: ['audio_generation', 'voice_synthesis', 'music']
    },
    {
      id: 'subtitles',
      label: 'Subtitles & Effects',
      description: 'Adding subtitles and visual effects',
      icon: <Subtitles />,
      phases: ['subtitles', 'effects', 'overlays']
    },
    {
      id: 'compilation',
      label: 'Final Compilation',
      description: 'Combining all elements into final video',
      icon: <Movie />,
      phases: ['compilation', 'final_render', 'processing']
    },
    {
      id: 'completion',
      label: 'Ready for Download',
      description: 'Video generation completed successfully',
      icon: <Download />,
      phases: ['completed', 'finished', 'ready']
    }
  ];

  const getCurrentStepIndex = () => {
    if (!progress?.currentPhase) return 0;
    
    const currentPhase = progress.currentPhase.toLowerCase();
    for (let i = 0; i < processingSteps.length; i++) {
      if (processingSteps[i].phases.some(phase => currentPhase.includes(phase))) {
        return i;
      }
    }
    return Math.min(Math.floor(progress.progress / 12.5), processingSteps.length - 1);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <RadioButtonChecked className="text-green-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="text-green-600" />;
      case 'error':
        return <CheckCircle className="text-red-500" />;
      default:
        return <Schedule className="text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'primary';
      case 'completed':
        return 'success';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  if (!isGenerating && !progress) {
    return (
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="text-center py-8">
            <TrendingUp className="text-gray-400 mb-4" style={{ fontSize: 64 }} />
            <Typography variant="h6" className="text-gray-600 mb-2">
              Ready to Generate
            </Typography>
            <Typography variant="body2" className="text-gray-500">
              Configure your video settings and click Generate to start
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!progress) {
    return (
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="text-center py-8">
            <div className="animate-pulse">
              <TrendingUp className="text-primary-500 mb-4" style={{ fontSize: 64 }} />
            </div>
            <Typography variant="h6" className="text-gray-700 mb-2">
              Initializing Generation...
            </Typography>
            <Typography variant="body2" className="text-gray-500">
              Setting up AI agents and preparing for video generation
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const completedDiscussions = progress.discussions?.filter(d => d.status === 'completed').length || 0;
  const totalDiscussions = progress.discussions?.length || 0;
  const activeAgents = progress.agents?.filter(a => a.status === 'active').length || 0;
  const completedAgents = progress.agents?.filter(a => a.status === 'completed').length || 0;

  return (
    <Card className="w-full shadow-lg">
      <CardContent className="p-6">
        {/* Header */}
        <Box className="flex items-center justify-between mb-6">
          <Typography variant="h5" className="font-bold text-gray-800">
            Generation Progress
          </Typography>
          <Chip
            label={progress.status.charAt(0).toUpperCase() + progress.status.slice(1)}
            color={getStatusColor(progress.status) as any}
            variant="outlined"
          />
        </Box>

        {/* Progress Bar */}
        <Box className="mb-6">
          <Box className="flex justify-between items-center mb-2">
            <Typography variant="h6" className="font-semibold">
              {progress.progress}%
            </Typography>
            <Typography variant="body2" className="text-gray-600">
              {progress.currentPhase}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={progress.progress}
            className="h-3 rounded-full"
            sx={{
              backgroundColor: '#e5e7eb',
              '& .MuiLinearProgress-bar': {
                background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
              },
            }}
          />
          <Typography variant="caption" className="text-gray-500 mt-1 block">
            {progress.message}
          </Typography>
        </Box>

        {/* Detailed Processing Steps */}
        <Box className="mb-6">
          <Typography variant="h6" className="font-semibold mb-4" sx={{ fontWeight: 700 }}>
            Processing Steps
          </Typography>
          <Paper elevation={0} sx={{ p: 3, border: '1px solid', borderColor: 'divider' }}>
            <List sx={{ py: 0 }}>
              {processingSteps.map((step, index) => {
                const currentStepIndex = getCurrentStepIndex();
                const isCompleted = index < currentStepIndex;
                const isActive = index === currentStepIndex;
                const isPending = index > currentStepIndex;
                
                return (
                  <ListItem
                    key={step.id}
                    sx={{
                      py: 2,
                      px: 1,
                      borderRadius: 2,
                      mb: 1,
                      backgroundColor: isActive 
                        ? 'primary.main' 
                        : isCompleted 
                          ? 'success.light' 
                          : 'transparent',
                      color: isActive || isCompleted ? 'white' : 'inherit',
                      opacity: isPending ? 0.6 : 1,
                      transition: 'all 0.3s ease',
                      '&:hover': {
                        backgroundColor: isActive 
                          ? 'primary.dark' 
                          : isCompleted 
                            ? 'success.main' 
                            : 'action.hover',
                      }
                    }}
                  >
                    <ListItemIcon sx={{ minWidth: 48 }}>
                      {isCompleted ? (
                        <CheckCircle sx={{ color: 'white', fontSize: 24 }} />
                      ) : isActive ? (
                        <Box sx={{ color: 'white', display: 'flex', alignItems: 'center' }}>
                          {React.cloneElement(step.icon, { sx: { fontSize: 24, animation: 'pulse 2s infinite' } })}
                        </Box>
                      ) : (
                        React.cloneElement(step.icon, { sx: { color: 'text.secondary', fontSize: 24 } })
                      )}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Typography 
                          variant="subtitle1" 
                          sx={{ 
                            fontWeight: isActive ? 700 : 600,
                            color: isActive || isCompleted ? 'white' : 'text.primary'
                          }}
                        >
                          {step.label}
                          {isActive && (
                            <Chip 
                              label="IN PROGRESS" 
                              size="small" 
                              sx={{ 
                                ml: 2, 
                                backgroundColor: 'rgba(255,255,255,0.2)',
                                color: 'white',
                                fontWeight: 600
                              }} 
                            />
                          )}
                          {isCompleted && (
                            <Chip 
                              label="COMPLETED" 
                              size="small" 
                              sx={{ 
                                ml: 2, 
                                backgroundColor: 'rgba(255,255,255,0.2)',
                                color: 'white',
                                fontWeight: 600
                              }} 
                            />
                          )}
                        </Typography>
                      }
                      secondary={
                        <Typography 
                          variant="body2" 
                          sx={{ 
                            color: isActive || isCompleted ? 'rgba(255,255,255,0.8)' : 'text.secondary',
                            mt: 0.5
                          }}
                        >
                          {step.description}
                        </Typography>
                      }
                    />
                    {isActive && (
                      <Box sx={{ ml: 2, minWidth: 60 }}>
                        <Typography variant="caption" sx={{ color: 'white', fontWeight: 600 }}>
                          {progress.progress}%
                        </Typography>
                        <LinearProgress 
                          variant="determinate" 
                          value={progress.progress} 
                          sx={{ 
                            width: 60,
                            height: 4,
                            mt: 0.5,
                            backgroundColor: 'rgba(255,255,255,0.3)',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: 'white'
                            }
                          }} 
                        />
                      </Box>
                    )}
                  </ListItem>
                );
              })}
            </List>
          </Paper>
        </Box>

        {/* Stats Grid */}
        <Grid container spacing={3} className="mb-6">
          <Grid item xs={12} sm={4}>
            <Box className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
              <Group className="text-blue-600 mb-2" fontSize="large" />
              <Typography variant="h4" className="font-bold text-blue-700">
                {progress.agents?.length || 0}
              </Typography>
              <Typography variant="body2" className="text-blue-600">
                AI Agents
              </Typography>
              <Typography variant="caption" className="text-blue-500">
                {completedAgents} completed, {activeAgents} active
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={4}>
            <Box className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
              <Chat className="text-green-600 mb-2" fontSize="large" />
              <Typography variant="h4" className="font-bold text-green-700">
                {completedDiscussions}/{totalDiscussions}
              </Typography>
              <Typography variant="body2" className="text-green-600">
                Discussions
              </Typography>
              <Typography variant="caption" className="text-green-500">
                Strategic AI conversations
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={4}>
            <Box className="text-center p-4 bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg">
              <TrendingUp className="text-purple-600 mb-2" fontSize="large" />
              <Typography variant="h4" className="font-bold text-purple-700">
                {progress.progress}%
              </Typography>
              <Typography variant="body2" className="text-purple-600">
                Progress
              </Typography>
              <Typography variant="caption" className="text-purple-500">
                Phase {progress.currentPhase}
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Agent Status */}
        {progress.agents && progress.agents.length > 0 && (
          <>
            <Divider className="mb-4" />
            <Typography variant="h6" className="font-semibold mb-4">
              AI Agent Status
            </Typography>
            <Grid container spacing={2}>
              {progress.agents.map((agent: AgentStatus) => (
                <Grid item xs={12} sm={6} md={4} key={agent.id}>
                  <Box className="flex items-center p-3 border rounded-lg hover:shadow-md transition-shadow">
                    <Avatar className="mr-3" sx={{ bgcolor: agent.status === 'completed' ? '#10b981' : agent.status === 'active' ? '#3b82f6' : '#9ca3af' }}>
                      {agent.emoji}
                    </Avatar>
                    <Box className="flex-1 min-w-0">
                      <Typography variant="subtitle2" className="font-semibold truncate">
                        {agent.name}
                      </Typography>
                      <Box className="flex items-center mt-1">
                        {getStatusIcon(agent.status)}
                        <Typography variant="caption" className="ml-1 text-gray-600">
                          {agent.status === 'active' ? agent.currentTask || 'Working...' : agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                        </Typography>
                      </Box>
                      {agent.status === 'active' && (
                        <LinearProgress
                          variant="determinate"
                          value={agent.progress}
                          size="small"
                          className="mt-1"
                        />
                      )}
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </>
        )}

        {/* Timing Information */}
        {progress.startTime && (
          <Box className="mt-4 p-3 bg-gray-50 rounded-lg">
            <Typography variant="body2" className="text-gray-600">
              <strong>Started:</strong> {new Date(progress.startTime).toLocaleTimeString()}
              {progress.estimatedCompletion && (
                <>
                  {' • '}
                  <strong>Estimated completion:</strong> {new Date(progress.estimatedCompletion).toLocaleTimeString()}
                </>
              )}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default ProgressMonitor;