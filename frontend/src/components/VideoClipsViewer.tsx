import React, { useState, useRef } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  IconButton,
  Chip,
  Dialog,
  DialogContent,
  DialogTitle,
  Button,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Fullscreen,
  Download,
  Visibility,
  VideoLibrary,
  Schedule,
  CheckCircle,
  Error,
  Movie,
  Close,
} from '@mui/icons-material';
import { VideoClip } from '../types';

interface VideoClipsViewerProps {
  videoClips: VideoClip[];
  isGenerating: boolean;
}

const VideoClipsViewer: React.FC<VideoClipsViewerProps> = ({ videoClips, isGenerating }) => {
  const [selectedClip, setSelectedClip] = useState<VideoClip | null>(null);
  const [isPlaying, setIsPlaying] = useState<{ [key: string]: boolean }>({});
  const [dialogOpen, setDialogOpen] = useState(false);
  const videoRefs = useRef<{ [key: string]: HTMLVideoElement | null }>({});

  const handlePlayPause = (clipId: string) => {
    const video = videoRefs.current[clipId];
    if (video) {
      if (isPlaying[clipId]) {
        video.pause();
      } else {
        video.play();
      }
      setIsPlaying(prev => ({ ...prev, [clipId]: !prev[clipId] }));
    }
  };

  const handleClipSelect = (clip: VideoClip) => {
    setSelectedClip(clip);
    setDialogOpen(true);
  };

  const handleDownload = (clip: VideoClip) => {
    const link = document.createElement('a');
    link.href = clip.path;
    link.download = clip.name;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-500" />;
      case 'generating':
        return <Schedule className="text-blue-500 animate-pulse" />;
      case 'error':
        return <Error className="text-red-500" />;
      default:
        return <Schedule className="text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'generating':
        return 'primary';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'veo':
        return '🎬';
      case 'gemini':
        return '💎';
      case 'fallback':
        return '🔄';
      default:
        return '🎥';
    }
  };

  const formatDuration = (seconds: number) => {
    return `${Math.floor(seconds / 60)}:${(seconds % 60).toString().padStart(2, '0')}`;
  };

  if (!isGenerating && videoClips.length === 0) {
    return (
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center mb-4">
            <VideoLibrary className="text-primary-500 mr-3" fontSize="large" />
            <Typography variant="h5" className="font-bold text-gray-800">
              Video Clips
            </Typography>
          </Box>
          
          <Box className="text-center py-12">
            <Movie className="text-gray-400 mb-4" style={{ fontSize: 64 }} />
            <Typography variant="h6" className="text-gray-600 mb-2">
              Video Clips Will Appear Here
            </Typography>
            <Typography variant="body2" className="text-gray-500">
              Generated video clips will be displayed here in real-time during generation
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const completedClips = videoClips.filter(clip => clip.status === 'completed');
  const generatingClips = videoClips.filter(clip => clip.status === 'generating');
  const errorClips = videoClips.filter(clip => clip.status === 'error');

  return (
    <>
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center justify-between mb-6">
            <Box className="flex items-center">
              <VideoLibrary className="text-primary-500 mr-3" fontSize="large" />
              <Typography variant="h5" className="font-bold text-gray-800">
                Video Clips
              </Typography>
            </Box>
            <Box className="flex space-x-2">
              {generatingClips.length > 0 && (
                <Chip
                  label={`${generatingClips.length} Generating`}
                  color="primary"
                  size="small"
                  icon={<Schedule />}
                />
              )}
              {completedClips.length > 0 && (
                <Chip
                  label={`${completedClips.length} Ready`}
                  color="success"
                  size="small"
                  icon={<CheckCircle />}
                />
              )}
              {errorClips.length > 0 && (
                <Chip
                  label={`${errorClips.length} Failed`}
                  color="error"
                  size="small"
                  icon={<Error />}
                />
              )}
            </Box>
          </Box>

          {videoClips.length === 0 && isGenerating && (
            <Box className="text-center py-8">
              <div className="animate-pulse">
                <Movie className="text-primary-500 mb-4" style={{ fontSize: 48 }} />
              </div>
              <Typography variant="h6" className="text-gray-700 mb-2">
                Generating Video Clips...
              </Typography>
              <Typography variant="body2" className="text-gray-500">
                AI agents are creating video clips for your content
              </Typography>
            </Box>
          )}

          <Grid container spacing={3}>
            {videoClips.map((clip) => (
              <Grid item xs={12} sm={6} md={4} key={clip.id}>
                <Card className="border border-gray-200 hover:shadow-lg transition-shadow">
                  <Box className="relative">
                    {clip.status === 'completed' ? (
                      <Box className="relative">
                        <video
                          ref={(el) => (videoRefs.current[clip.id] = el)}
                          className="w-full h-48 object-cover rounded-t-lg"
                          poster={clip.thumbnail}
                          onPlay={() => setIsPlaying(prev => ({ ...prev, [clip.id]: true }))}
                          onPause={() => setIsPlaying(prev => ({ ...prev, [clip.id]: false }))}
                          onEnded={() => setIsPlaying(prev => ({ ...prev, [clip.id]: false }))}
                        >
                          <source src={clip.path} type="video/mp4" />
                          Your browser does not support the video tag.
                        </video>
                        
                        {/* Play/Pause Overlay */}
                        <Box className="absolute inset-0 flex items-center justify-center">
                          <IconButton
                            onClick={() => handlePlayPause(clip.id)}
                            className="bg-black bg-opacity-50 text-white hover:bg-opacity-75"
                            size="large"
                          >
                            {isPlaying[clip.id] ? <Pause /> : <PlayArrow />}
                          </IconButton>
                        </Box>
                        
                        {/* Duration Badge */}
                        <Chip
                          label={formatDuration(clip.duration)}
                          size="small"
                          className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white"
                        />
                      </Box>
                    ) : clip.status === 'generating' ? (
                      <Box className="h-48 bg-gradient-to-br from-blue-100 to-blue-200 flex items-center justify-center">
                        <Box className="text-center">
                          <div className="animate-pulse mb-2">
                            <Movie className="text-blue-500" style={{ fontSize: 48 }} />
                          </div>
                          <Typography variant="body2" className="text-blue-700 font-medium">
                            Generating...
                          </Typography>
                          <LinearProgress className="mt-2 w-24 mx-auto" />
                        </Box>
                      </Box>
                    ) : (
                      <Box className="h-48 bg-gradient-to-br from-red-100 to-red-200 flex items-center justify-center">
                        <Box className="text-center">
                          <Error className="text-red-500 mb-2" style={{ fontSize: 48 }} />
                          <Typography variant="body2" className="text-red-700 font-medium">
                            Generation Failed
                          </Typography>
                        </Box>
                      </Box>
                    )}
                    
                    {/* Type Badge */}
                    <Box className="absolute top-2 left-2">
                      <Chip
                        label={`${getTypeIcon(clip.type)} ${clip.type.toUpperCase()}`}
                        size="small"
                        className="bg-white bg-opacity-90"
                      />
                    </Box>
                    
                    {/* Status Badge */}
                    <Box className="absolute top-2 right-2">
                      <Chip
                        icon={getStatusIcon(clip.status)}
                        label={clip.status.charAt(0).toUpperCase() + clip.status.slice(1)}
                        size="small"
                        color={getStatusColor(clip.status) as any}
                        variant="filled"
                      />
                    </Box>
                  </Box>

                  <CardContent className="p-4">
                    <Typography variant="subtitle1" className="font-semibold mb-2 truncate">
                      {clip.name}
                    </Typography>
                    
                    <Typography variant="caption" className="text-gray-500 block mb-3">
                      Generated: {new Date(clip.timestamp).toLocaleTimeString()}
                    </Typography>

                    <Box className="flex space-x-2">
                      {clip.status === 'completed' && (
                        <>
                          <Tooltip title="View Full Screen">
                            <IconButton
                              size="small"
                              onClick={() => handleClipSelect(clip)}
                              className="text-blue-600"
                            >
                              <Visibility />
                            </IconButton>
                          </Tooltip>
                          
                          <Tooltip title="Download Clip">
                            <IconButton
                              size="small"
                              onClick={() => handleDownload(clip)}
                              className="text-green-600"
                            >
                              <Download />
                            </IconButton>
                          </Tooltip>
                        </>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Full Screen Video Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle className="flex items-center justify-between">
          <Typography variant="h6">
            {selectedClip?.name}
          </Typography>
          <IconButton onClick={() => setDialogOpen(false)}>
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {selectedClip && (
            <Box>
              <video
                controls
                className="w-full rounded-lg"
                poster={selectedClip.thumbnail}
              >
                <source src={selectedClip.path} type="video/mp4" />
                Your browser does not support the video tag.
              </video>
              
              <Box className="mt-4 flex items-center justify-between">
                <Box>
                  <Typography variant="body2" className="text-gray-600">
                    Duration: {formatDuration(selectedClip.duration)} • 
                    Type: {selectedClip.type.toUpperCase()} • 
                    Generated: {new Date(selectedClip.timestamp).toLocaleString()}
                  </Typography>
                </Box>
                <Button
                  variant="contained"
                  startIcon={<Download />}
                  onClick={() => handleDownload(selectedClip)}
                >
                  Download
                </Button>
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
};

export default VideoClipsViewer;