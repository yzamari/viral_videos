import React, { useState, useRef, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Grid,
  IconButton,
  Chip,
  Slider,
  LinearProgress,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Button,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  VolumeUp,
  VolumeOff,
  Download,
  AudioFile,
  Schedule,
  CheckCircle,
  Error,
  MusicNote,
  VoiceChat,
  GraphicEq,
  ExpandMore,
} from '@mui/icons-material';
import { AudioSegment } from '../types';

interface AudioViewerProps {
  audioSegments: AudioSegment[];
  isGenerating: boolean;
}

const AudioViewer: React.FC<AudioViewerProps> = ({ audioSegments, isGenerating }) => {
  const [isPlaying, setIsPlaying] = useState<{ [key: string]: boolean }>({});
  const [currentTime, setCurrentTime] = useState<{ [key: string]: number }>({});
  const [volume, setVolume] = useState<{ [key: string]: number }>({});
  const [isMuted, setIsMuted] = useState<{ [key: string]: boolean }>({});
  const audioRefs = useRef<{ [key: string]: HTMLAudioElement | null }>({});

  useEffect(() => {
    // Initialize volume for all audio segments
    audioSegments.forEach(segment => {
      if (!volume[segment.id]) {
        setVolume(prev => ({ ...prev, [segment.id]: 0.7 }));
      }
    });
  }, [audioSegments]);

  const handlePlayPause = (segmentId: string) => {
    const audio = audioRefs.current[segmentId];
    if (audio) {
      if (isPlaying[segmentId]) {
        audio.pause();
      } else {
        // Pause all other audio segments
        Object.keys(audioRefs.current).forEach(id => {
          if (id !== segmentId && audioRefs.current[id]) {
            audioRefs.current[id]!.pause();
            setIsPlaying(prev => ({ ...prev, [id]: false }));
          }
        });
        audio.play();
      }
      setIsPlaying(prev => ({ ...prev, [segmentId]: !prev[segmentId] }));
    }
  };

  const handleVolumeChange = (segmentId: string, newVolume: number) => {
    const audio = audioRefs.current[segmentId];
    if (audio) {
      audio.volume = newVolume;
      setVolume(prev => ({ ...prev, [segmentId]: newVolume }));
      setIsMuted(prev => ({ ...prev, [segmentId]: newVolume === 0 }));
    }
  };

  const handleMuteToggle = (segmentId: string) => {
    const audio = audioRefs.current[segmentId];
    if (audio) {
      const newMuted = !isMuted[segmentId];
      audio.volume = newMuted ? 0 : volume[segmentId] || 0.7;
      setIsMuted(prev => ({ ...prev, [segmentId]: newMuted }));
    }
  };

  const handleTimeUpdate = (segmentId: string) => {
    const audio = audioRefs.current[segmentId];
    if (audio) {
      setCurrentTime(prev => ({ ...prev, [segmentId]: audio.currentTime }));
    }
  };

  const handleSeek = (segmentId: string, newTime: number) => {
    const audio = audioRefs.current[segmentId];
    if (audio) {
      audio.currentTime = newTime;
      setCurrentTime(prev => ({ ...prev, [segmentId]: newTime }));
    }
  };

  const handleDownload = (segment: AudioSegment) => {
    const link = document.createElement('a');
    link.href = segment.path;
    link.download = segment.name;
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

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'voice':
        return <VoiceChat className="text-blue-600" />;
      case 'music':
        return <MusicNote className="text-purple-600" />;
      case 'effects':
        return <GraphicEq className="text-green-600" />;
      default:
        return <AudioFile className="text-gray-600" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'voice':
        return 'bg-blue-100 border-blue-300';
      case 'music':
        return 'bg-purple-100 border-purple-300';
      case 'effects':
        return 'bg-green-100 border-green-300';
      default:
        return 'bg-gray-100 border-gray-300';
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!isGenerating && audioSegments.length === 0) {
    return (
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center mb-4">
            <AudioFile className="text-primary-500 mr-3" fontSize="large" />
            <Typography variant="h5" className="font-bold text-gray-800">
              Audio Segments
            </Typography>
          </Box>
          
          <Box className="text-center py-12">
            <VoiceChat className="text-gray-400 mb-4" style={{ fontSize: 64 }} />
            <Typography variant="h6" className="text-gray-600 mb-2">
              Audio Segments Will Appear Here
            </Typography>
            <Typography variant="body2" className="text-gray-500">
              Generated audio segments will be displayed here in real-time during generation
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  const completedSegments = audioSegments.filter(segment => segment.status === 'completed');
  const generatingSegments = audioSegments.filter(segment => segment.status === 'generating');
  const errorSegments = audioSegments.filter(segment => segment.status === 'error');

  // Group segments by type
  const voiceSegments = audioSegments.filter(segment => segment.type === 'voice');
  const musicSegments = audioSegments.filter(segment => segment.type === 'music');
  const effectSegments = audioSegments.filter(segment => segment.type === 'effects');

  return (
    <Card className="w-full shadow-lg">
      <CardContent className="p-6">
        <Box className="flex items-center justify-between mb-6">
          <Box className="flex items-center">
            <AudioFile className="text-primary-500 mr-3" fontSize="large" />
            <Typography variant="h5" className="font-bold text-gray-800">
              Audio Segments
            </Typography>
          </Box>
          <Box className="flex space-x-2">
            {generatingSegments.length > 0 && (
              <Chip
                label={`${generatingSegments.length} Generating`}
                color="primary"
                size="small"
                icon={<Schedule />}
              />
            )}
            {completedSegments.length > 0 && (
              <Chip
                label={`${completedSegments.length} Ready`}
                color="success"
                size="small"
                icon={<CheckCircle />}
              />
            )}
            {errorSegments.length > 0 && (
              <Chip
                label={`${errorSegments.length} Failed`}
                color="error"
                size="small"
                icon={<Error />}
              />
            )}
          </Box>
        </Box>

        {audioSegments.length === 0 && isGenerating && (
          <Box className="text-center py-8">
            <div className="animate-pulse">
              <VoiceChat className="text-primary-500 mb-4" style={{ fontSize: 48 }} />
            </div>
            <Typography variant="h6" className="text-gray-700 mb-2">
              Generating Audio...
            </Typography>
            <Typography variant="body2" className="text-gray-500">
              AI agents are creating audio segments for your content
            </Typography>
          </Box>
        )}

        {/* Voice Segments */}
        {voiceSegments.length > 0 && (
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box className="flex items-center">
                <VoiceChat className="text-blue-600 mr-2" />
                <Typography variant="h6">Voice Segments ({voiceSegments.length})</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <AudioSegmentsList 
                segments={voiceSegments}
                audioRefs={audioRefs}
                isPlaying={isPlaying}
                currentTime={currentTime}
                volume={volume}
                isMuted={isMuted}
                onPlayPause={handlePlayPause}
                onVolumeChange={handleVolumeChange}
                onMuteToggle={handleMuteToggle}
                onTimeUpdate={handleTimeUpdate}
                onSeek={handleSeek}
                onDownload={handleDownload}
              />
            </AccordionDetails>
          </Accordion>
        )}

        {/* Music Segments */}
        {musicSegments.length > 0 && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box className="flex items-center">
                <MusicNote className="text-purple-600 mr-2" />
                <Typography variant="h6">Music Segments ({musicSegments.length})</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <AudioSegmentsList 
                segments={musicSegments}
                audioRefs={audioRefs}
                isPlaying={isPlaying}
                currentTime={currentTime}
                volume={volume}
                isMuted={isMuted}
                onPlayPause={handlePlayPause}
                onVolumeChange={handleVolumeChange}
                onMuteToggle={handleMuteToggle}
                onTimeUpdate={handleTimeUpdate}
                onSeek={handleSeek}
                onDownload={handleDownload}
              />
            </AccordionDetails>
          </Accordion>
        )}

        {/* Effect Segments */}
        {effectSegments.length > 0 && (
          <Accordion>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box className="flex items-center">
                <GraphicEq className="text-green-600 mr-2" />
                <Typography variant="h6">Sound Effects ({effectSegments.length})</Typography>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <AudioSegmentsList 
                segments={effectSegments}
                audioRefs={audioRefs}
                isPlaying={isPlaying}
                currentTime={currentTime}
                volume={volume}
                isMuted={isMuted}
                onPlayPause={handlePlayPause}
                onVolumeChange={handleVolumeChange}
                onMuteToggle={handleMuteToggle}
                onTimeUpdate={handleTimeUpdate}
                onSeek={handleSeek}
                onDownload={handleDownload}
              />
            </AccordionDetails>
          </Accordion>
        )}

        {/* All segments in one list if no categorization needed */}
        {voiceSegments.length === 0 && musicSegments.length === 0 && effectSegments.length === 0 && audioSegments.length > 0 && (
          <AudioSegmentsList 
            segments={audioSegments}
            audioRefs={audioRefs}
            isPlaying={isPlaying}
            currentTime={currentTime}
            volume={volume}
            isMuted={isMuted}
            onPlayPause={handlePlayPause}
            onVolumeChange={handleVolumeChange}
            onMuteToggle={handleMuteToggle}
            onTimeUpdate={handleTimeUpdate}
            onSeek={handleSeek}
            onDownload={handleDownload}
          />
        )}
      </CardContent>
    </Card>
  );
};

interface AudioSegmentsListProps {
  segments: AudioSegment[];
  audioRefs: React.MutableRefObject<{ [key: string]: HTMLAudioElement | null }>;
  isPlaying: { [key: string]: boolean };
  currentTime: { [key: string]: number };
  volume: { [key: string]: number };
  isMuted: { [key: string]: boolean };
  onPlayPause: (segmentId: string) => void;
  onVolumeChange: (segmentId: string, volume: number) => void;
  onMuteToggle: (segmentId: string) => void;
  onTimeUpdate: (segmentId: string) => void;
  onSeek: (segmentId: string, time: number) => void;
  onDownload: (segment: AudioSegment) => void;
}

const AudioSegmentsList: React.FC<AudioSegmentsListProps> = ({
  segments,
  audioRefs,
  isPlaying,
  currentTime,
  volume,
  isMuted,
  onPlayPause,
  onVolumeChange,
  onMuteToggle,
  onTimeUpdate,
  onSeek,
  onDownload,
}) => {
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

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'voice':
        return <VoiceChat className="text-blue-600" />;
      case 'music':
        return <MusicNote className="text-purple-600" />;
      case 'effects':
        return <GraphicEq className="text-green-600" />;
      default:
        return <AudioFile className="text-gray-600" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'voice':
        return 'bg-blue-100 border-blue-300';
      case 'music':
        return 'bg-purple-100 border-purple-300';
      case 'effects':
        return 'bg-green-100 border-green-300';
      default:
        return 'bg-gray-100 border-gray-300';
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Grid container spacing={2}>
      {segments.map((segment) => (
        <Grid item xs={12} key={segment.id}>
          <Card className={`border-2 ${getTypeColor(segment.type)} hover:shadow-md transition-shadow`}>
            <CardContent className="p-4">
              <Box className="flex items-center justify-between mb-3">
                <Box className="flex items-center space-x-3">
                  {getTypeIcon(segment.type)}
                  <Typography variant="subtitle1" className="font-semibold">
                    {segment.name}
                  </Typography>
                  <Chip
                    label={segment.type}
                    size="small"
                    variant="outlined"
                  />
                </Box>
                <Box className="flex items-center space-x-2">
                  {getStatusIcon(segment.status)}
                  <Typography variant="caption" className="text-gray-500">
                    {new Date(segment.timestamp).toLocaleTimeString()}
                  </Typography>
                </Box>
              </Box>

              {segment.status === 'completed' && (
                <>
                  <audio
                    ref={(el) => (audioRefs.current[segment.id] = el)}
                    onTimeUpdate={() => onTimeUpdate(segment.id)}
                    onEnded={() => onPlayPause(segment.id)}
                    src={segment.path}
                  />

                  {/* Audio Controls */}
                  <Box className="flex items-center space-x-3 mb-3">
                    <IconButton
                      onClick={() => onPlayPause(segment.id)}
                      className="bg-primary-100 hover:bg-primary-200"
                    >
                      {isPlaying[segment.id] ? <Pause /> : <PlayArrow />}
                    </IconButton>

                    <Box className="flex-1">
                      <Slider
                        value={currentTime[segment.id] || 0}
                        max={segment.duration}
                        onChange={(_, value) => onSeek(segment.id, value as number)}
                        size="small"
                        className="text-primary-500"
                      />
                      <Box className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>{formatTime(currentTime[segment.id] || 0)}</span>
                        <span>{formatTime(segment.duration)}</span>
                      </Box>
                    </Box>

                    <Box className="flex items-center space-x-2 min-w-[120px]">
                      <IconButton
                        onClick={() => onMuteToggle(segment.id)}
                        size="small"
                      >
                        {isMuted[segment.id] ? <VolumeOff /> : <VolumeUp />}
                      </IconButton>
                      <Slider
                        value={isMuted[segment.id] ? 0 : (volume[segment.id] || 0.7)}
                        onChange={(_, value) => onVolumeChange(segment.id, value as number)}
                        min={0}
                        max={1}
                        step={0.1}
                        size="small"
                        className="w-16"
                      />
                    </Box>

                    <Tooltip title="Download Audio">
                      <IconButton
                        onClick={() => onDownload(segment)}
                        size="small"
                        className="text-green-600"
                      >
                        <Download />
                      </IconButton>
                    </Tooltip>
                  </Box>

                  {/* Transcript */}
                  {segment.transcript && (
                    <Box className="p-3 bg-gray-50 rounded-lg">
                      <Typography variant="caption" className="text-gray-600 font-semibold block mb-1">
                        Transcript:
                      </Typography>
                      <Typography variant="body2" className="text-gray-700">
                        {segment.transcript}
                      </Typography>
                    </Box>
                  )}
                </>
              )}

              {segment.status === 'generating' && (
                <Box className="text-center py-4">
                  <LinearProgress className="mb-2" />
                  <Typography variant="body2" className="text-blue-600">
                    Generating audio segment...
                  </Typography>
                </Box>
              )}

              {segment.status === 'error' && (
                <Box className="text-center py-4">
                  <Error className="text-red-500 mb-2" />
                  <Typography variant="body2" className="text-red-600">
                    Failed to generate audio segment
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default AudioViewer;