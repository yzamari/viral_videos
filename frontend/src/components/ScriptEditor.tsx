import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  IconButton,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Divider,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  Paper,
} from '@mui/material';
import {
  Edit,
  Save,
  Cancel,
  Add,
  Delete,
  PlayArrow,
  Schedule,
  Description,
  ExpandMore,
  Timeline,
  Person,
  DirectionsRun,
  Visibility,
  VisibilityOff,
} from '@mui/icons-material';
import { Script, ScriptSegment } from '../types';

interface ScriptEditorProps {
  script: Script | null;
  onScriptUpdate: (script: Script) => void;
  isGenerating: boolean;
  readonly?: boolean;
}

const ScriptEditor: React.FC<ScriptEditorProps> = ({ 
  script, 
  onScriptUpdate, 
  isGenerating,
  readonly = false 
}) => {
  const [editingSegment, setEditingSegment] = useState<string | null>(null);
  const [tempSegmentText, setTempSegmentText] = useState('');
  const [showMetadata, setShowMetadata] = useState(false);
  const [addSegmentDialog, setAddSegmentDialog] = useState(false);
  const [newSegment, setNewSegment] = useState({
    text: '',
    startTime: 0,
    endTime: 0,
    speaker: '',
    action: '',
  });

  useEffect(() => {
    if (editingSegment && script) {
      const segment = script.segments.find(s => s.id === editingSegment);
      if (segment) {
        setTempSegmentText(segment.text);
      }
    }
  }, [editingSegment, script]);

  const handleStartEdit = (segmentId: string) => {
    if (readonly) return;
    setEditingSegment(segmentId);
  };

  const handleSaveEdit = () => {
    if (!script || !editingSegment) return;

    const updatedScript = {
      ...script,
      segments: script.segments.map(segment =>
        segment.id === editingSegment
          ? { ...segment, text: tempSegmentText }
          : segment
      ),
      lastModified: new Date(),
      version: script.version + 1,
    };

    onScriptUpdate(updatedScript);
    setEditingSegment(null);
    setTempSegmentText('');
  };

  const handleCancelEdit = () => {
    setEditingSegment(null);
    setTempSegmentText('');
  };

  const handleDeleteSegment = (segmentId: string) => {
    if (!script || readonly) return;

    const updatedScript = {
      ...script,
      segments: script.segments.filter(segment => segment.id !== segmentId),
      lastModified: new Date(),
      version: script.version + 1,
    };

    onScriptUpdate(updatedScript);
  };

  const handleAddSegment = () => {
    if (!script || readonly) return;

    const newId = `segment_${Date.now()}`;
    const segment: ScriptSegment = {
      id: newId,
      text: newSegment.text,
      startTime: newSegment.startTime,
      endTime: newSegment.endTime,
      speaker: newSegment.speaker || undefined,
      action: newSegment.action || undefined,
      isEditable: true,
    };

    const updatedScript = {
      ...script,
      segments: [...script.segments, segment].sort((a, b) => a.startTime - b.startTime),
      lastModified: new Date(),
      version: script.version + 1,
    };

    onScriptUpdate(updatedScript);
    setAddSegmentDialog(false);
    setNewSegment({ text: '', startTime: 0, endTime: 0, speaker: '', action: '' });
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSegmentDuration = (segment: ScriptSegment) => {
    return segment.endTime - segment.startTime;
  };

  const getTotalDuration = () => {
    if (!script || script.segments.length === 0) return 0;
    return Math.max(...script.segments.map(s => s.endTime));
  };

  const getWordCount = (text: string) => {
    return text.trim().split(/\s+/).length;
  };

  const getReadingTime = (text: string) => {
    const wordsPerMinute = 150; // Average reading speed
    const words = getWordCount(text);
    return Math.ceil(words / wordsPerMinute);
  };

  if (!script && !isGenerating) {
    return (
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center mb-4">
            <Description className="text-primary-500 mr-3" fontSize="large" />
            <Typography variant="h5" className="font-bold text-gray-800">
              Script Editor
            </Typography>
          </Box>
          
          <Box className="text-center py-12">
            <Description className="text-gray-400 mb-4" style={{ fontSize: 64 }} />
            <Typography variant="h6" className="text-gray-600 mb-2">
              Script Will Appear Here
            </Typography>
            <Typography variant="body2" className="text-gray-500">
              The generated script will be displayed here and can be edited in real-time
            </Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  if (!script && isGenerating) {
    return (
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center mb-4">
            <Description className="text-primary-500 mr-3" fontSize="large" />
            <Typography variant="h5" className="font-bold text-gray-800">
              Script Editor
            </Typography>
          </Box>
          
          <Box className="text-center py-8">
            <div className="animate-pulse">
              <Description className="text-primary-500 mb-4" style={{ fontSize: 48 }} />
            </div>
            <Typography variant="h6" className="text-gray-700 mb-2">
              Generating Script...
            </Typography>
            <Typography variant="body2" className="text-gray-500">
              AI agents are creating your video script
            </Typography>
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
              <Description className="text-primary-500 mr-3" fontSize="large" />
              <Typography variant="h5" className="font-bold text-gray-800">
                Script Editor
              </Typography>
              {readonly && (
                <Chip label="Read Only" size="small" color="secondary" className="ml-3" />
              )}
            </Box>
            <Box className="flex items-center space-x-2">
              <Tooltip title="Toggle Metadata">
                <IconButton onClick={() => setShowMetadata(!showMetadata)}>
                  {showMetadata ? <VisibilityOff /> : <Visibility />}
                </IconButton>
              </Tooltip>
              {!readonly && (
                <Button
                  variant="outlined"
                  startIcon={<Add />}
                  onClick={() => setAddSegmentDialog(true)}
                  size="small"
                >
                  Add Segment
                </Button>
              )}
              <Chip
                label={`v${script?.version || 1}`}
                size="small"
                variant="outlined"
              />
            </Box>
          </Box>

          {/* Script Metadata */}
          {showMetadata && script && (
            <Accordion className="mb-4">
              <AccordionSummary expandIcon={<ExpandMore />}>
                <Box className="flex items-center">
                  <Timeline className="mr-2" />
                  <Typography variant="h6">Script Metadata</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Box className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Paper className="p-4 text-center">
                    <Typography variant="h4" className="font-bold text-primary-600">
                      {formatTime(getTotalDuration())}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Total Duration
                    </Typography>
                  </Paper>
                  <Paper className="p-4 text-center">
                    <Typography variant="h4" className="font-bold text-green-600">
                      {getWordCount(script.content)}
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Word Count
                    </Typography>
                  </Paper>
                  <Paper className="p-4 text-center">
                    <Typography variant="h4" className="font-bold text-blue-600">
                      {getReadingTime(script.content)}m
                    </Typography>
                    <Typography variant="body2" className="text-gray-600">
                      Reading Time
                    </Typography>
                  </Paper>
                </Box>
                <Box className="mt-4 text-sm text-gray-500">
                  <Typography variant="caption">
                    Last modified: {script.lastModified.toLocaleString()}
                  </Typography>
                </Box>
              </AccordionDetails>
            </Accordion>
          )}

          {/* Script Content */}
          <Box className="space-y-4">
            {script?.segments.map((segment, index) => (
              <Card
                key={segment.id}
                className={`border-2 ${
                  editingSegment === segment.id
                    ? 'border-blue-300 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                } transition-colors`}
              >
                <CardContent className="p-4">
                  <Box className="flex items-center justify-between mb-3">
                    <Box className="flex items-center space-x-3">
                      <Chip
                        label={`${index + 1}`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                      <Box className="flex items-center space-x-2 text-sm text-gray-600">
                        <Schedule fontSize="small" />
                        <span>{formatTime(segment.startTime)} - {formatTime(segment.endTime)}</span>
                        <span>({formatTime(getSegmentDuration(segment))})</span>
                      </Box>
                      {segment.speaker && (
                        <Box className="flex items-center space-x-1 text-sm text-gray-600">
                          <Person fontSize="small" />
                          <span>{segment.speaker}</span>
                        </Box>
                      )}
                      {segment.action && (
                        <Box className="flex items-center space-x-1 text-sm text-gray-600">
                          <DirectionsRun fontSize="small" />
                          <span>{segment.action}</span>
                        </Box>
                      )}
                    </Box>
                    {!readonly && segment.isEditable && (
                      <Box className="flex space-x-1">
                        {editingSegment === segment.id ? (
                          <>
                            <IconButton
                              onClick={handleSaveEdit}
                              size="small"
                              className="text-green-600"
                            >
                              <Save />
                            </IconButton>
                            <IconButton
                              onClick={handleCancelEdit}
                              size="small"
                              className="text-gray-600"
                            >
                              <Cancel />
                            </IconButton>
                          </>
                        ) : (
                          <>
                            <IconButton
                              onClick={() => handleStartEdit(segment.id)}
                              size="small"
                              className="text-blue-600"
                            >
                              <Edit />
                            </IconButton>
                            <IconButton
                              onClick={() => handleDeleteSegment(segment.id)}
                              size="small"
                              className="text-red-600"
                            >
                              <Delete />
                            </IconButton>
                          </>
                        )}
                      </Box>
                    )}
                  </Box>

                  {editingSegment === segment.id ? (
                    <TextField
                      multiline
                      rows={3}
                      fullWidth
                      value={tempSegmentText}
                      onChange={(e) => setTempSegmentText(e.target.value)}
                      placeholder="Enter segment text..."
                      variant="outlined"
                      autoFocus
                    />
                  ) : (
                    <Typography
                      variant="body1"
                      className="text-gray-800 leading-relaxed"
                      style={{ whiteSpace: 'pre-wrap' }}
                    >
                      {segment.text}
                    </Typography>
                  )}

                  <Box className="mt-3 flex items-center justify-between">
                    <Typography variant="caption" className="text-gray-500">
                      {getWordCount(segment.text)} words
                    </Typography>
                    <Box className="flex items-center space-x-2">
                      <Tooltip title="Preview Audio">
                        <IconButton size="small" className="text-purple-600">
                          <PlayArrow />
                        </IconButton>
                      </Tooltip>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            ))}
          </Box>

          {/* Full Script View */}
          <Accordion className="mt-6">
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="h6">Full Script</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <Box className="p-4 bg-gray-50 rounded-lg">
                <Typography
                  variant="body1"
                  className="text-gray-800 leading-relaxed"
                  style={{ whiteSpace: 'pre-wrap' }}
                >
                  {script?.content}
                </Typography>
              </Box>
            </AccordionDetails>
          </Accordion>
        </CardContent>
      </Card>

      {/* Add Segment Dialog */}
      <Dialog open={addSegmentDialog} onClose={() => setAddSegmentDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Add New Segment</DialogTitle>
        <DialogContent>
          <Box className="space-y-4 pt-2">
            <TextField
              fullWidth
              label="Segment Text"
              multiline
              rows={3}
              value={newSegment.text}
              onChange={(e) => setNewSegment({ ...newSegment, text: e.target.value })}
              placeholder="Enter the text for this segment..."
            />
            <Box className="flex space-x-2">
              <TextField
                label="Start Time (seconds)"
                type="number"
                value={newSegment.startTime}
                onChange={(e) => setNewSegment({ ...newSegment, startTime: Number(e.target.value) })}
                size="small"
              />
              <TextField
                label="End Time (seconds)"
                type="number"
                value={newSegment.endTime}
                onChange={(e) => setNewSegment({ ...newSegment, endTime: Number(e.target.value) })}
                size="small"
              />
            </Box>
            <Box className="flex space-x-2">
              <TextField
                label="Speaker (optional)"
                value={newSegment.speaker}
                onChange={(e) => setNewSegment({ ...newSegment, speaker: e.target.value })}
                size="small"
              />
              <TextField
                label="Action (optional)"
                value={newSegment.action}
                onChange={(e) => setNewSegment({ ...newSegment, action: e.target.value })}
                size="small"
              />
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddSegmentDialog(false)}>Cancel</Button>
          <Button
            onClick={handleAddSegment}
            variant="contained"
            disabled={!newSegment.text.trim() || newSegment.startTime >= newSegment.endTime}
          >
            Add Segment
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default ScriptEditor;