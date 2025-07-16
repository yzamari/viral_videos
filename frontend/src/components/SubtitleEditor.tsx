import React, { useState, useRef } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  IconButton,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Grid,
  Paper,
  Tooltip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Save,
  Cancel,
  PlayArrow,
  Pause,
  Subtitles,
  Download,
  Upload,
  FormatSize,
  Timeline,
  Sync,
  Translate,
} from '@mui/icons-material';
import { Subtitle } from '../types';

interface SubtitleEditorProps {
  subtitles: Subtitle[];
  onSubtitlesUpdate: (subtitles: Subtitle[]) => void;
  videoDuration?: number;
  videoRef?: React.RefObject<HTMLVideoElement>;
  readonly?: boolean;
}

const SubtitleEditor: React.FC<SubtitleEditorProps> = ({
  subtitles,
  onSubtitlesUpdate,
  videoDuration = 60,
  videoRef,
  readonly = false,
}) => {
  const [editingSubtitle, setEditingSubtitle] = useState<Subtitle | null>(null);
  const [addDialog, setAddDialog] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [selectedSubtitle, setSelectedSubtitle] = useState<string | null>(null);
  const [autoSyncMode, setAutoSyncMode] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [newSubtitle, setNewSubtitle] = useState<Partial<Subtitle>>({
    text: '',
    startTime: 0,
    endTime: 3,
    position: 'bottom',
    style: {
      fontSize: 16,
      color: '#ffffff',
      backgroundColor: 'rgba(0,0,0,0.7)',
      fontFamily: 'Arial',
    },
    isEditable: true,
  });

  const positions = [
    { value: 'bottom', label: 'Bottom' },
    { value: 'top', label: 'Top' },
    { value: 'center', label: 'Center' },
  ];

  const fontFamilies = [
    'Arial',
    'Arial Black',
    'Helvetica',
    'Times New Roman',
    'Courier New',
    'Verdana',
    'Georgia',
  ];

  const handleAddSubtitle = () => {
    if (!newSubtitle.text?.trim()) return;

    const subtitle: Subtitle = {
      id: `subtitle_${Date.now()}`,
      text: newSubtitle.text!,
      startTime: newSubtitle.startTime!,
      endTime: newSubtitle.endTime!,
      position: newSubtitle.position!,
      style: newSubtitle.style!,
      isEditable: true,
    };

    const updatedSubtitles = [...subtitles, subtitle].sort((a, b) => a.startTime - b.startTime);
    onSubtitlesUpdate(updatedSubtitles);
    setAddDialog(false);
    setNewSubtitle({
      text: '',
      startTime: newSubtitle.endTime! + 0.5,
      endTime: newSubtitle.endTime! + 3.5,
      position: 'bottom',
      style: {
        fontSize: 16,
        color: '#ffffff',
        backgroundColor: 'rgba(0,0,0,0.7)',
        fontFamily: 'Arial',
      },
      isEditable: true,
    });
  };

  const handleEditSubtitle = (subtitle: Subtitle) => {
    setEditingSubtitle({ ...subtitle });
  };

  const handleSaveEdit = () => {
    if (!editingSubtitle) return;

    const updatedSubtitles = subtitles.map(subtitle =>
      subtitle.id === editingSubtitle.id ? editingSubtitle : subtitle
    ).sort((a, b) => a.startTime - b.startTime);
    
    onSubtitlesUpdate(updatedSubtitles);
    setEditingSubtitle(null);
  };

  const handleDeleteSubtitle = (subtitleId: string) => {
    const updatedSubtitles = subtitles.filter(subtitle => subtitle.id !== subtitleId);
    onSubtitlesUpdate(updatedSubtitles);
    if (selectedSubtitle === subtitleId) {
      setSelectedSubtitle(null);
    }
  };

  const handleAutoSync = () => {
    // This would typically integrate with speech recognition or timing analysis
    console.log('Auto-sync feature would be implemented here');
  };

  const handleImportSRT = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      const content = e.target?.result as string;
      const importedSubtitles = parseSRT(content);
      onSubtitlesUpdate([...subtitles, ...importedSubtitles]);
    };
    reader.readAsText(file);
  };

  const parseSRT = (content: string): Subtitle[] => {
    const blocks = content.trim().split('\n\n');
    const subtitles: Subtitle[] = [];

    blocks.forEach((block, index) => {
      const lines = block.split('\n');
      if (lines.length >= 3) {
        const timeMatch = lines[1].match(/(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})/);
        if (timeMatch) {
          const startTime = parseInt(timeMatch[1]) * 3600 + parseInt(timeMatch[2]) * 60 + parseInt(timeMatch[3]) + parseInt(timeMatch[4]) / 1000;
          const endTime = parseInt(timeMatch[5]) * 3600 + parseInt(timeMatch[6]) * 60 + parseInt(timeMatch[7]) + parseInt(timeMatch[8]) / 1000;
          const text = lines.slice(2).join('\n');

          subtitles.push({
            id: `imported_${Date.now()}_${index}`,
            text,
            startTime,
            endTime,
            position: 'bottom',
            style: {
              fontSize: 16,
              color: '#ffffff',
              backgroundColor: 'rgba(0,0,0,0.7)',
              fontFamily: 'Arial',
            },
            isEditable: true,
          });
        }
      }
    });

    return subtitles;
  };

  const exportSRT = () => {
    let srtContent = '';
    subtitles.forEach((subtitle, index) => {
      const startTime = formatSRTTime(subtitle.startTime);
      const endTime = formatSRTTime(subtitle.endTime);
      srtContent += `${index + 1}\n${startTime} --> ${endTime}\n${subtitle.text}\n\n`;
    });

    const blob = new Blob([srtContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'subtitles.srt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatSRTTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    const millis = Math.floor((seconds % 1) * 1000);
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')},${millis.toString().padStart(3, '0')}`;
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getSubtitleAtTime = (time: number) => {
    return subtitles.find(subtitle => 
      time >= subtitle.startTime && time <= subtitle.endTime
    );
  };

  const getCurrentSubtitle = () => {
    return getSubtitleAtTime(currentTime);
  };

  return (
    <>
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center justify-between mb-6">
            <Box className="flex items-center">
              <Subtitles className="text-primary-500 mr-3" fontSize="large" />
              <Typography variant="h5" className="font-bold text-gray-800">
                Subtitle Editor
              </Typography>
              {readonly && (
                <Chip label="Read Only" size="small" color="secondary" className="ml-3" />
              )}
            </Box>
            <Box className="flex items-center space-x-2">
              <Tooltip title="Import SRT File">
                <IconButton onClick={handleImportSRT} disabled={readonly}>
                  <Upload />
                </IconButton>
              </Tooltip>
              <Tooltip title="Export SRT File">
                <IconButton onClick={exportSRT} disabled={subtitles.length === 0}>
                  <Download />
                </IconButton>
              </Tooltip>
              <Tooltip title="Auto Sync">
                <IconButton onClick={handleAutoSync} disabled={readonly}>
                  <Sync />
                </IconButton>
              </Tooltip>
              {!readonly && (
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setAddDialog(true)}
                  size="small"
                >
                  Add Subtitle
                </Button>
              )}
              <Chip
                label={`${subtitles.length} subtitles`}
                size="small"
                variant="outlined"
              />
            </Box>
          </Box>

          {/* Video Preview with Subtitles */}
          <Box className="mb-6">
            <Paper className="p-4 bg-gray-100">
              <Box className="flex items-center justify-between mb-4">
                <Typography variant="h6">Preview</Typography>
                <Box className="flex items-center space-x-2">
                  <Typography variant="body2" className="text-gray-600">
                    Time: {formatTime(currentTime)}
                  </Typography>
                  <IconButton size="small">
                    <PlayArrow />
                  </IconButton>
                </Box>
              </Box>
              
              <Box className="relative">
                {/* Video Preview Area */}
                <Box
                  className="relative w-full h-64 bg-black rounded-lg overflow-hidden flex items-end justify-center"
                  style={{ aspectRatio: '16/9' }}
                >
                  {/* Current Subtitle Display */}
                  {(() => {
                    const currentSubtitle = getCurrentSubtitle();
                    if (currentSubtitle) {
                      return (
                        <Box
                          className={`absolute ${
                            currentSubtitle.position === 'top' ? 'top-4' :
                            currentSubtitle.position === 'center' ? 'top-1/2 transform -translate-y-1/2' :
                            'bottom-4'
                          } left-1/2 transform -translate-x-1/2 max-w-4/5 text-center`}
                          style={{
                            color: currentSubtitle.style.color,
                            backgroundColor: currentSubtitle.style.backgroundColor,
                            fontSize: `${currentSubtitle.style.fontSize}px`,
                            fontFamily: currentSubtitle.style.fontFamily,
                            padding: '8px 16px',
                            borderRadius: '4px',
                            lineHeight: 1.2,
                          }}
                        >
                          {currentSubtitle.text}
                        </Box>
                      );
                    }
                    return (
                      <Box className="absolute inset-0 flex items-center justify-center">
                        <Typography variant="body2" className="text-gray-400">
                          No subtitle at current time
                        </Typography>
                      </Box>
                    );
                  })()}
                </Box>

                {/* Timeline Scrubber */}
                <Box className="mt-4">
                  <Slider
                    value={currentTime}
                    onChange={(_, value) => setCurrentTime(value as number)}
                    min={0}
                    max={videoDuration}
                    step={0.1}
                    valueLabelDisplay="auto"
                    valueLabelFormat={formatTime}
                    className="text-primary-500"
                  />
                  
                  {/* Subtitle Timeline */}
                  <Box className="relative h-2 bg-gray-200 rounded mt-2">
                    {subtitles.map(subtitle => (
                      <Box
                        key={subtitle.id}
                        className="absolute h-full bg-blue-500 rounded cursor-pointer hover:bg-blue-600"
                        style={{
                          left: `${(subtitle.startTime / videoDuration) * 100}%`,
                          width: `${((subtitle.endTime - subtitle.startTime) / videoDuration) * 100}%`,
                        }}
                        onClick={() => setCurrentTime(subtitle.startTime)}
                        title={`${formatTime(subtitle.startTime)} - ${formatTime(subtitle.endTime)}: ${subtitle.text.substring(0, 50)}...`}
                      />
                    ))}
                  </Box>
                  
                  <Box className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>0:00</span>
                    <span>{formatTime(videoDuration)}</span>
                  </Box>
                </Box>
              </Box>
            </Paper>
          </Box>

          {/* Subtitles List */}
          <Box>
            {subtitles.length === 0 ? (
              <Box className="text-center py-8">
                <Subtitles className="text-gray-400 mb-4" style={{ fontSize: 48 }} />
                <Typography variant="h6" className="text-gray-600 mb-2">
                  No Subtitles Added
                </Typography>
                <Typography variant="body2" className="text-gray-500">
                  Add subtitles to make your video accessible and engaging
                </Typography>
              </Box>
            ) : (
              <List>
                {subtitles.map((subtitle, index) => (
                  <React.Fragment key={subtitle.id}>
                    <ListItem
                      className={`${
                        selectedSubtitle === subtitle.id ? 'bg-blue-50' : ''
                      } hover:bg-gray-50 cursor-pointer rounded-lg transition-colors`}
                      onClick={() => {
                        setSelectedSubtitle(subtitle.id);
                        setCurrentTime(subtitle.startTime);
                      }}
                    >
                      <Box className="flex-1">
                        <Box className="flex items-center space-x-3 mb-2">
                          <Chip
                            label={index + 1}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                          <Typography variant="body2" className="text-gray-600">
                            {formatTime(subtitle.startTime)} - {formatTime(subtitle.endTime)}
                          </Typography>
                          <Chip
                            label={subtitle.position}
                            size="small"
                            variant="outlined"
                          />
                        </Box>
                        <Typography
                          variant="body1"
                          className="font-medium"
                          style={{
                            color: subtitle.style.color === '#ffffff' ? 'inherit' : subtitle.style.color,
                            fontFamily: subtitle.style.fontFamily,
                          }}
                        >
                          {subtitle.text}
                        </Typography>
                        <Typography variant="caption" className="text-gray-500 mt-1 block">
                          Duration: {formatTime(subtitle.endTime - subtitle.startTime)} • 
                          Font: {subtitle.style.fontFamily} {subtitle.style.fontSize}px
                        </Typography>
                      </Box>
                      
                      {!readonly && subtitle.isEditable && (
                        <ListItemSecondaryAction>
                          <Box className="flex space-x-1">
                            <IconButton
                              onClick={(e) => {
                                e.stopPropagation();
                                handleEditSubtitle(subtitle);
                              }}
                              size="small"
                              className="text-blue-600"
                            >
                              <Edit />
                            </IconButton>
                            <IconButton
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteSubtitle(subtitle.id);
                              }}
                              size="small"
                              className="text-red-600"
                            >
                              <Delete />
                            </IconButton>
                          </Box>
                        </ListItemSecondaryAction>
                      )}
                    </ListItem>
                    {index < subtitles.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Hidden File Input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".srt,.vtt"
        style={{ display: 'none' }}
        onChange={handleFileUpload}
      />

      {/* Add Subtitle Dialog */}
      <Dialog open={addDialog} onClose={() => setAddDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Subtitle</DialogTitle>
        <DialogContent>
          <Box className="space-y-4 pt-2">
            <TextField
              fullWidth
              label="Subtitle Text"
              multiline
              rows={2}
              value={newSubtitle.text}
              onChange={(e) => setNewSubtitle({ ...newSubtitle, text: e.target.value })}
              placeholder="Enter subtitle text..."
            />

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Start Time (seconds)"
                  type="number"
                  value={newSubtitle.startTime}
                  onChange={(e) => setNewSubtitle({ ...newSubtitle, startTime: Number(e.target.value) })}
                  inputProps={{ step: 0.1 }}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="End Time (seconds)"
                  type="number"
                  value={newSubtitle.endTime}
                  onChange={(e) => setNewSubtitle({ ...newSubtitle, endTime: Number(e.target.value) })}
                  inputProps={{ step: 0.1 }}
                />
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Position</InputLabel>
                  <Select
                    value={newSubtitle.position || 'bottom'}
                    onChange={(e) => setNewSubtitle({ ...newSubtitle, position: e.target.value as any })}
                  >
                    {positions.map(pos => (
                      <MenuItem key={pos.value} value={pos.value}>
                        {pos.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Font Family</InputLabel>
                  <Select
                    value={newSubtitle.style?.fontFamily || 'Arial'}
                    onChange={(e) => setNewSubtitle({
                      ...newSubtitle,
                      style: { ...newSubtitle.style!, fontFamily: e.target.value }
                    })}
                  >
                    {fontFamilies.map(font => (
                      <MenuItem key={font} value={font} style={{ fontFamily: font }}>
                        {font}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography gutterBottom>Font Size: {newSubtitle.style?.fontSize}px</Typography>
                <Slider
                  value={newSubtitle.style?.fontSize || 16}
                  onChange={(_, value) => setNewSubtitle({
                    ...newSubtitle,
                    style: { ...newSubtitle.style!, fontSize: value as number }
                  })}
                  min={10}
                  max={32}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  label="Text Color"
                  type="color"
                  value={newSubtitle.style?.color || '#ffffff'}
                  onChange={(e) => setNewSubtitle({
                    ...newSubtitle,
                    style: { ...newSubtitle.style!, color: e.target.value }
                  })}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  label="Background (optional)"
                  placeholder="rgba(0,0,0,0.7)"
                  value={newSubtitle.style?.backgroundColor || ''}
                  onChange={(e) => setNewSubtitle({
                    ...newSubtitle,
                    style: { ...newSubtitle.style!, backgroundColor: e.target.value }
                  })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialog(false)}>Cancel</Button>
          <Button
            onClick={handleAddSubtitle}
            variant="contained"
            disabled={!newSubtitle.text?.trim() || (newSubtitle.startTime! >= newSubtitle.endTime!)}
          >
            Add Subtitle
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Subtitle Dialog */}
      <Dialog
        open={!!editingSubtitle}
        onClose={() => setEditingSubtitle(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit Subtitle</DialogTitle>
        <DialogContent>
          {editingSubtitle && (
            <Box className="space-y-4 pt-2">
              <TextField
                fullWidth
                label="Subtitle Text"
                multiline
                rows={2}
                value={editingSubtitle.text}
                onChange={(e) => setEditingSubtitle({ ...editingSubtitle, text: e.target.value })}
              />

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Start Time (seconds)"
                    type="number"
                    value={editingSubtitle.startTime}
                    onChange={(e) => setEditingSubtitle({ ...editingSubtitle, startTime: Number(e.target.value) })}
                    inputProps={{ step: 0.1 }}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="End Time (seconds)"
                    type="number"
                    value={editingSubtitle.endTime}
                    onChange={(e) => setEditingSubtitle({ ...editingSubtitle, endTime: Number(e.target.value) })}
                    inputProps={{ step: 0.1 }}
                  />
                </Grid>
              </Grid>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Position</InputLabel>
                    <Select
                      value={editingSubtitle.position}
                      onChange={(e) => setEditingSubtitle({ ...editingSubtitle, position: e.target.value as any })}
                    >
                      {positions.map(pos => (
                        <MenuItem key={pos.value} value={pos.value}>
                          {pos.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Font Family</InputLabel>
                    <Select
                      value={editingSubtitle.style.fontFamily}
                      onChange={(e) => setEditingSubtitle({
                        ...editingSubtitle,
                        style: { ...editingSubtitle.style, fontFamily: e.target.value }
                      })}
                    >
                      {fontFamilies.map(font => (
                        <MenuItem key={font} value={font} style={{ fontFamily: font }}>
                          {font}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography gutterBottom>Font Size: {editingSubtitle.style.fontSize}px</Typography>
                  <Slider
                    value={editingSubtitle.style.fontSize}
                    onChange={(_, value) => setEditingSubtitle({
                      ...editingSubtitle,
                      style: { ...editingSubtitle.style, fontSize: value as number }
                    })}
                    min={10}
                    max={32}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Text Color"
                    type="color"
                    value={editingSubtitle.style.color}
                    onChange={(e) => setEditingSubtitle({
                      ...editingSubtitle,
                      style: { ...editingSubtitle.style, color: e.target.value }
                    })}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Background (optional)"
                    value={editingSubtitle.style.backgroundColor || ''}
                    onChange={(e) => setEditingSubtitle({
                      ...editingSubtitle,
                      style: { ...editingSubtitle.style, backgroundColor: e.target.value }
                    })}
                  />
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingSubtitle(null)}>Cancel</Button>
          <Button onClick={handleSaveEdit} variant="contained">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default SubtitleEditor;