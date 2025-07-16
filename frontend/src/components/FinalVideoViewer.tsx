import React, { useState, useRef } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Button,
  IconButton,
  Chip,
  Grid,
  Paper,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Fullscreen,
  Download,
  Share,
  Movie,
  CheckCircle,
  Schedule,
  Error,
  VideoFile,
  CloudDownload,
  Analytics,
  Info,
  Close,
  VolumeUp,
  VolumeOff,
  SkipNext,
  SkipPrevious,
  Replay,
} from '@mui/icons-material';
import { FinalVideo, VideoGenerationConfig } from '../types';

interface FinalVideoViewerProps {
  finalVideo: FinalVideo | null;
  isGenerating: boolean;
  sessionConfig?: VideoGenerationConfig;
  onDownload?: (video: FinalVideo) => void;
  onShare?: (video: FinalVideo) => void;
}

const FinalVideoViewer: React.FC<FinalVideoViewerProps> = ({
  finalVideo,
  isGenerating,
  sessionConfig,
  onDownload,
  onShare,
}) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showMetadata, setShowMetadata] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [isDownloading, setIsDownloading] = useState(false);

  const videoRef = useRef<HTMLVideoElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleMuteToggle = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (newVolume: number) => {
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
      setVolume(newVolume);
      setIsMuted(newVolume === 0);
    }
  };

  const handleSeek = (newTime: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const handleFullscreen = () => {
    if (!document.fullscreenElement && containerRef.current) {
      containerRef.current.requestFullscreen();
      setIsFullscreen(true);
    } else if (document.fullscreenElement) {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const handleDownload = async () => {
    if (!finalVideo || !onDownload) return;

    setIsDownloading(true);
    setDownloadProgress(0);

    try {
      // Simulate download progress
      const interval = setInterval(() => {
        setDownloadProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            setIsDownloading(false);
            onDownload(finalVideo);
            return 100;
          }
          return prev + 10;
        });
      }, 200);
    } catch (error) {
      console.error('Download failed:', error);
      setIsDownloading(false);
      setDownloadProgress(0);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="text-green-500" />;
      case 'processing':
        return <Schedule className="text-blue-500 animate-pulse" />;
      case 'error':
        return <Error className="text-red-500" />;
      default:
        return <Schedule className="text-gray-400" />;
    }
  };

  if (!finalVideo && !isGenerating) {
    return (
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center mb-4">
            <Movie className="text-primary-500 mr-3" fontSize="large" />
            <Typography variant="h5" className="font-bold text-gray-800">
              Final Video
            </Typography>
          </Box>
          
          <Box className="text-center py-12">
            <VideoFile className="text-gray-400 mb-4" style={{ fontSize: 64 }} />
            <Typography variant="h6" className="text-gray-600 mb-2">
              Final Video Will Appear Here
            </Typography>
            <Typography variant="body2" className="text-gray-500">
              The completed video will be available for preview and download after generation
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!finalVideo && isGenerating) {
    return (
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center mb-4">
            <Movie className="text-primary-500 mr-3" fontSize="large" />
            <Typography variant="h5" className="font-bold text-gray-800">
              Final Video
            </Typography>
          </Box>
          
          <Box className="text-center py-8">
            <div className="animate-pulse">
              <Movie className="text-primary-500 mb-4" style={{ fontSize: 48 }} />
            </div>
            <Typography variant="h6" className="text-gray-700 mb-2">
              Finalizing Video...
            </Typography>
            <Typography variant="body2" className="text-gray-500 mb-4">
              AI agents are assembling the final video with all components
            </Typography>
            <LinearProgress className="w-64 mx-auto" />
          </Box>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center justify-between mb-6">
            <Box className="flex items-center">
              <Movie className="text-primary-500 mr-3" fontSize="large" />
              <Typography variant="h5" className="font-bold text-gray-800">
                Final Video
              </Typography>
              <Chip
                icon={getStatusIcon(finalVideo!.status)}
                label={finalVideo!.status.charAt(0).toUpperCase() + finalVideo!.status.slice(1)}
                color={finalVideo!.status === 'completed' ? 'success' : 'primary'}
                className="ml-3"
              />
            </Box>
            <Box className="flex items-center space-x-2">
              <Tooltip title="Video Information">
                <IconButton onClick={() => setShowMetadata(true)}>
                  <Info />
                </IconButton>
              </Tooltip>
              {finalVideo!.status === 'completed' && (
                <>
                  <Button
                    variant="outlined"
                    startIcon={<Share />}
                    onClick={() => onShare?.(finalVideo!)}
                    size="small"
                  >
                    Share
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={isDownloading ? <CloudDownload /> : <Download />}
                    onClick={handleDownload}
                    disabled={isDownloading}
                    size="small"
                  >
                    {isDownloading ? 'Downloading...' : 'Download'}
                  </Button>
                </>
              )}
            </Box>
          </Box>

          {/* Download Progress */}
          {isDownloading && (
            <Box className="mb-4">
              <Box className="flex justify-between items-center mb-2">
                <Typography variant="body2">Downloading video...</Typography>
                <Typography variant="body2">{downloadProgress}%</Typography>
              </Box>
              <LinearProgress variant="determinate" value={downloadProgress} />
            </Box>
          )}

          {/* Video Player */}
          <Box ref={containerRef} className="relative bg-black rounded-lg overflow-hidden">
            {finalVideo!.status === 'completed' ? (
              <>
                <video
                  ref={videoRef}
                  className="w-full h-auto"
                  poster={finalVideo!.thumbnail}
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  onTimeUpdate={(e) => setCurrentTime((e.target as HTMLVideoElement).currentTime)}
                  onLoadedMetadata={(e) => setDuration((e.target as HTMLVideoElement).duration)}
                  onEnded={() => setIsPlaying(false)}
                  controls={false}
                >
                  <source src={finalVideo!.path} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>

                {/* Custom Controls Overlay */}
                <Box className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4">
                  {/* Progress Bar */}
                  <Box className="mb-3">
                    <input
                      type="range"
                      min={0}
                      max={duration}
                      value={currentTime}
                      onChange={(e) => handleSeek(Number(e.target.value))}
                      className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                      style={{
                        background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(currentTime / duration) * 100}%, #4b5563 ${(currentTime / duration) * 100}%, #4b5563 100%)`
                      }}
                    />
                    <Box className="flex justify-between text-xs text-gray-300 mt-1">
                      <span>{formatTime(currentTime)}</span>
                      <span>{formatTime(duration)}</span>
                    </Box>
                  </Box>

                  {/* Control Buttons */}
                  <Box className="flex items-center justify-between">
                    <Box className="flex items-center space-x-3">
                      <IconButton
                        onClick={() => handleSeek(Math.max(0, currentTime - 10))}
                        className="text-white hover:text-blue-400"
                      >
                        <SkipPrevious />
                      </IconButton>
                      
                      <IconButton
                        onClick={handlePlayPause}
                        className="text-white hover:text-blue-400 bg-blue-600 hover:bg-blue-700"
                        size="large"
                      >
                        {isPlaying ? <Pause /> : <PlayArrow />}
                      </IconButton>
                      
                      <IconButton
                        onClick={() => handleSeek(Math.min(duration, currentTime + 10))}
                        className="text-white hover:text-blue-400"
                      >
                        <SkipNext />
                      </IconButton>

                      <IconButton
                        onClick={() => handleSeek(0)}
                        className="text-white hover:text-blue-400"
                      >
                        <Replay />
                      </IconButton>
                    </Box>

                    <Box className="flex items-center space-x-3">
                      {/* Volume Control */}
                      <Box className="flex items-center space-x-2">
                        <IconButton
                          onClick={handleMuteToggle}
                          className="text-white hover:text-blue-400"
                          size="small"
                        >
                          {isMuted ? <VolumeOff /> : <VolumeUp />}
                        </IconButton>
                        <input
                          type="range"
                          min={0}
                          max={1}
                          step={0.1}
                          value={isMuted ? 0 : volume}
                          onChange={(e) => handleVolumeChange(Number(e.target.value))}
                          className="w-20 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                        />
                      </Box>

                      <IconButton
                        onClick={handleFullscreen}
                        className="text-white hover:text-blue-400"
                      >
                        <Fullscreen />
                      </IconButton>
                    </Box>
                  </Box>
                </Box>
              </>
            ) : (
              <Box className="h-64 flex items-center justify-center">
                <Box className="text-center text-white">
                  {finalVideo!.status === 'processing' ? (
                    <>
                      <Schedule className="mb-2" style={{ fontSize: 48 }} />
                      <Typography variant="h6">Processing Video...</Typography>
                      <LinearProgress className="mt-2 w-64" />
                    </>
                  ) : (
                    <>
                      <Error className="mb-2" style={{ fontSize: 48 }} />
                      <Typography variant="h6">Video Processing Failed</Typography>
                    </>
                  )}
                </Box>
              </Box>
            )}
          </Box>

          {/* Video Information */}
          <Box className="mt-6">
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6} md={3}>
                <Paper className="p-4 text-center">
                  <Typography variant="h4" className="font-bold text-blue-600">
                    {formatTime(finalVideo!.duration)}
                  </Typography>
                  <Typography variant="body2" className="text-gray-600">
                    Duration
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Paper className="p-4 text-center">
                  <Typography variant="h4" className="font-bold text-green-600">
                    {formatFileSize(finalVideo!.size)}
                  </Typography>
                  <Typography variant="body2" className="text-gray-600">
                    File Size
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Paper className="p-4 text-center">
                  <Typography variant="h4" className="font-bold text-purple-600">
                    {finalVideo!.resolution}
                  </Typography>
                  <Typography variant="body2" className="text-gray-600">
                    Resolution
                  </Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Paper className="p-4 text-center">
                  <Typography variant="h4" className="font-bold text-orange-600">
                    {finalVideo!.format.toUpperCase()}
                  </Typography>
                  <Typography variant="body2" className="text-gray-600">
                    Format
                  </Typography>
                </Paper>
              </Grid>
            </Grid>
          </Box>

          {/* Generation Summary */}
          <Box className="mt-6">
            <Typography variant="h6" className="mb-3">Generation Summary</Typography>
            <Paper className="p-4">
              <Grid container spacing={2}>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" className="text-gray-600">
                    <strong>Generated:</strong> {new Date(finalVideo!.metadata.generatedAt).toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" className="text-gray-600">
                    <strong>Session ID:</strong> {finalVideo!.metadata.sessionId}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" className="text-gray-600">
                    <strong>Platform:</strong> {sessionConfig?.platform || 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={12} sm={6}>
                  <Typography variant="body2" className="text-gray-600">
                    <strong>Category:</strong> {sessionConfig?.category || 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="body2" className="text-gray-600">
                    <strong>Components:</strong> {finalVideo!.metadata.clips.length} video clips, {finalVideo!.metadata.audio.length} audio segments, {finalVideo!.metadata.overlays.length} overlays, {finalVideo!.metadata.subtitles.length} subtitles
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          </Box>
        </CardContent>
      </Card>

      {/* Metadata Dialog */}
      <Dialog open={showMetadata} onClose={() => setShowMetadata(false)} maxWidth="md" fullWidth>
        <DialogTitle className="flex items-center justify-between">
          <Typography variant="h6">Video Metadata</Typography>
          <IconButton onClick={() => setShowMetadata(false)}>
            <Close />
          </IconButton>
        </DialogTitle>
        <DialogContent>
          {finalVideo && (
            <Box className="space-y-4">
              {/* Basic Info */}
              <Box>
                <Typography variant="h6" className="mb-2">Basic Information</Typography>
                <List dense>
                  <ListItem>
                    <ListItemIcon><VideoFile /></ListItemIcon>
                    <ListItemText
                      primary="File Path"
                      secondary={finalVideo.path}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Schedule /></ListItemIcon>
                    <ListItemText
                      primary="Duration"
                      secondary={`${formatTime(finalVideo.duration)} (${finalVideo.duration.toFixed(2)} seconds)`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemIcon><Analytics /></ListItemIcon>
                    <ListItemText
                      primary="File Size"
                      secondary={`${formatFileSize(finalVideo.size)} (${finalVideo.size.toLocaleString()} bytes)`}
                    />
                  </ListItem>
                </List>
              </Box>

              <Divider />

              {/* Generation Config */}
              <Box>
                <Typography variant="h6" className="mb-2">Generation Configuration</Typography>
                <List dense>
                  <ListItem>
                    <ListItemText
                      primary="Mission"
                      secondary={finalVideo.metadata.config.mission}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Platform & Category"
                      secondary={`${finalVideo.metadata.config.platform} • ${finalVideo.metadata.config.category}`}
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="AI System Mode"
                      secondary={`${finalVideo.metadata.config.mode} (${finalVideo.metadata.config.discussions} discussions)`}
                    />
                  </ListItem>
                </List>
              </Box>

              <Divider />

              {/* Components */}
              <Box>
                <Typography variant="h6" className="mb-2">Video Components</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6} sm={3}>
                    <Paper className="p-3 text-center">
                      <Typography variant="h5" className="font-bold text-blue-600">
                        {finalVideo.metadata.clips.length}
                      </Typography>
                      <Typography variant="caption">Video Clips</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Paper className="p-3 text-center">
                      <Typography variant="h5" className="font-bold text-green-600">
                        {finalVideo.metadata.audio.length}
                      </Typography>
                      <Typography variant="caption">Audio Segments</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Paper className="p-3 text-center">
                      <Typography variant="h5" className="font-bold text-purple-600">
                        {finalVideo.metadata.overlays.length}
                      </Typography>
                      <Typography variant="caption">Overlays</Typography>
                    </Paper>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Paper className="p-3 text-center">
                      <Typography variant="h5" className="font-bold text-orange-600">
                        {finalVideo.metadata.subtitles.length}
                      </Typography>
                      <Typography variant="caption">Subtitles</Typography>
                    </Paper>
                  </Grid>
                </Grid>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMetadata(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default FinalVideoViewer;