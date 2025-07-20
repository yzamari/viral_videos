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
  ColorPicker,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Save,
  Cancel,
  PlayArrow,
  Pause,
  Visibility,
  VisibilityOff,
  FormatColorText,
  FormatSize,
  Timeline,
  AspectRatio,
} from '@mui/icons-material';
import { Overlay } from '../types';

interface OverlayEditorProps {
  overlays: Overlay[];
  onOverlaysUpdate: (overlays: Overlay[]) => void;
  videoDuration?: number;
  videoRef?: React.RefObject<HTMLVideoElement>;
  readonly?: boolean;
}

const OverlayEditor: React.FC<OverlayEditorProps> = ({
  overlays,
  onOverlaysUpdate,
  videoDuration = 60,
  videoRef,
  readonly = false,
}) => {
  const [editingOverlay, setEditingOverlay] = useState<Overlay | null>(null);
  const [addDialog, setAddDialog] = useState(false);
  const [selectedOverlay, setSelectedOverlay] = useState<string | null>(null);
  const [currentTime, setCurrentTime] = useState(0);
  const [showPreview, setShowPreview] = useState(true);
  const previewRef = useRef<HTMLDivElement>(null);

  const [newOverlay, setNewOverlay] = useState<Partial<Overlay>>({
    text: '',
    startTime: 0,
    endTime: 5,
    position: { x: 50, y: 50 },
    style: {
      fontSize: 24,
      color: '#ffffff',
      backgroundColor: 'rgba(0,0,0,0.5)',
      fontFamily: 'Arial',
      fontWeight: 'bold',
    },
    animation: 'fade',
    isEditable: true,
  });

  const fontFamilies = [
    'Arial',
    'Arial Black',
    'Helvetica',
    'Times New Roman',
    'Courier New',
    'Verdana',
    'Georgia',
    'Comic Sans MS',
    'Impact',
    'Trebuchet MS',
  ];

  const animations = [
    { value: 'none', label: 'None' },
    { value: 'fade', label: 'Fade In/Out' },
    { value: 'slide', label: 'Slide' },
    { value: 'zoom', label: 'Zoom' },
  ];

  const handleAddOverlay = () => {
    if (!newOverlay.text?.trim()) return;

    const overlay: Overlay = {
      id: `overlay_${Date.now()}`,
      text: newOverlay.text!,
      startTime: newOverlay.startTime!,
      endTime: newOverlay.endTime!,
      position: newOverlay.position!,
      style: newOverlay.style!,
      animation: newOverlay.animation,
      isEditable: true,
    };

    onOverlaysUpdate([...overlays, overlay]);
    setAddDialog(false);
    setNewOverlay({
      text: '',
      startTime: 0,
      endTime: 5,
      position: { x: 50, y: 50 },
      style: {
        fontSize: 24,
        color: '#ffffff',
        backgroundColor: 'rgba(0,0,0,0.5)',
        fontFamily: 'Arial',
        fontWeight: 'bold',
      },
      animation: 'fade',
      isEditable: true,
    });
  };

  const handleEditOverlay = (overlay: Overlay) => {
    setEditingOverlay({ ...overlay });
  };

  const handleSaveEdit = () => {
    if (!editingOverlay) return;

    const updatedOverlays = overlays.map(overlay =>
      overlay.id === editingOverlay.id ? editingOverlay : overlay
    );
    onOverlaysUpdate(updatedOverlays);
    setEditingOverlay(null);
  };

  const handleDeleteOverlay = (overlayId: string) => {
    const updatedOverlays = overlays.filter(overlay => overlay.id !== overlayId);
    onOverlaysUpdate(updatedOverlays);
    if (selectedOverlay === overlayId) {
      setSelectedOverlay(null);
    }
  };

  const handlePositionChange = (overlayId: string, position: { x: number; y: number }) => {
    if (readonly) return;

    const updatedOverlays = overlays.map(overlay =>
      overlay.id === overlayId ? { ...overlay, position } : overlay
    );
    onOverlaysUpdate(updatedOverlays);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const isOverlayVisible = (overlay: Overlay, time: number) => {
    return time >= overlay.startTime && time <= overlay.endTime;
  };

  const getOverlayAtTime = (time: number) => {
    return overlays.filter(overlay => isOverlayVisible(overlay, time));
  };

  return (
    <>
      <Card className="w-full shadow-lg">
        <CardContent className="p-6">
          <Box className="flex items-center justify-between mb-6">
            <Box className="flex items-center">
              <FormatColorText className="text-primary-500 mr-3" fontSize="large" />
              <Typography variant="h5" className="font-bold text-gray-800">
                Overlay Editor
              </Typography>
              {readonly && (
                <Chip label="Read Only" size="small" color="secondary" className="ml-3" />
              )}
            </Box>
            <Box className="flex items-center space-x-2">
              <Tooltip title="Toggle Preview">
                <IconButton onClick={() => setShowPreview(!showPreview)}>
                  {showPreview ? <Visibility /> : <VisibilityOff />}
                </IconButton>
              </Tooltip>
              {!readonly && (
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  onClick={() => setAddDialog(true)}
                  size="small"
                >
                  Add Overlay
                </Button>
              )}
              <Chip
                label={`${overlays.length} overlays`}
                size="small"
                variant="outlined"
              />
            </Box>
          </Box>

          {/* Video Preview with Overlays */}
          {showPreview && (
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
                    ref={previewRef}
                    className="relative w-full h-64 bg-black rounded-lg overflow-hidden"
                    style={{ aspectRatio: '16/9' }}
                  >
                    {/* Render visible overlays */}
                    {getOverlayAtTime(currentTime).map(overlay => (
                      <Box
                        key={overlay.id}
                        className={`absolute cursor-pointer ${
                          selectedOverlay === overlay.id ? 'ring-2 ring-blue-500' : ''
                        }`}
                        style={{
                          left: `${overlay.position.x}%`,
                          top: `${overlay.position.y}%`,
                          transform: 'translate(-50%, -50%)',
                          color: overlay.style.color,
                          backgroundColor: overlay.style.backgroundColor,
                          fontSize: `${overlay.style.fontSize}px`,
                          fontFamily: overlay.style.fontFamily,
                          fontWeight: overlay.style.fontWeight,
                          padding: '4px 8px',
                          borderRadius: '4px',
                          maxWidth: '80%',
                          textAlign: 'center',
                          pointerEvents: readonly ? 'none' : 'auto',
                        }}
                        onClick={() => setSelectedOverlay(overlay.id)}
                        draggable={!readonly}
                        onDragEnd={(e) => {
                          if (readonly || !previewRef.current) return;
                          
                          const rect = previewRef.current.getBoundingClientRect();
                          const x = ((e.clientX - rect.left) / rect.width) * 100;
                          const y = ((e.clientY - rect.top) / rect.height) * 100;
                          
                          handlePositionChange(overlay.id, {
                            x: Math.max(0, Math.min(100, x)),
                            y: Math.max(0, Math.min(100, y)),
                          });
                        }}
                      >
                        {overlay.text}
                      </Box>
                    ))}
                    
                    {overlays.length === 0 && (
                      <Box className="absolute inset-0 flex items-center justify-center">
                        <Typography variant="body2" className="text-gray-400">
                          No overlays to display
                        </Typography>
                      </Box>
                    )}
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
                    <Box className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>0:00</span>
                      <span>{formatTime(videoDuration)}</span>
                    </Box>
                  </Box>
                </Box>
              </Paper>
            </Box>
          )}

          {/* Overlays List */}
          <Box className="space-y-3">
            {overlays.length === 0 ? (
              <Box className="text-center py-8">
                <FormatColorText className="text-gray-400 mb-4" style={{ fontSize: 48 }} />
                <Typography variant="h6" className="text-gray-600 mb-2">
                  No Overlays Added
                </Typography>
                <Typography variant="body2" className="text-gray-500">
                  Add text overlays to enhance your video with titles, captions, and more
                </Typography>
              </Box>
            ) : (
              overlays.map((overlay) => (
                <Card
                  key={overlay.id}
                  className={`border-2 ${
                    selectedOverlay === overlay.id
                      ? 'border-blue-300 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  } transition-colors cursor-pointer`}
                  onClick={() => setSelectedOverlay(overlay.id)}
                >
                  <CardContent className="p-4">
                    <Box className="flex items-center justify-between mb-3">
                      <Box className="flex items-center space-x-3">
                        <Typography
                          variant="h6"
                          className="font-medium"
                          style={{
                            color: overlay.style.color,
                            fontFamily: overlay.style.fontFamily,
                            fontWeight: overlay.style.fontWeight,
                          }}
                        >
                          {overlay.text}
                        </Typography>
                        <Chip
                          label={overlay.animation || 'none'}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                      {!readonly && overlay.isEditable && (
                        <Box className="flex space-x-1">
                          <IconButton
                            onClick={(e) => {
                              e.stopPropagation();
                              handleEditOverlay(overlay);
                            }}
                            size="small"
                            className="text-blue-600"
                          >
                            <Edit />
                          </IconButton>
                          <IconButton
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteOverlay(overlay.id);
                            }}
                            size="small"
                            className="text-red-600"
                          >
                            <Delete />
                          </IconButton>
                        </Box>
                      )}
                    </Box>

                    <Box className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                      <Box className="flex items-center space-x-1">
                        <Timeline fontSize="small" />
                        <span>{formatTime(overlay.startTime)} - {formatTime(overlay.endTime)}</span>
                      </Box>
                      <Box className="flex items-center space-x-1">
                        <AspectRatio fontSize="small" />
                        <span>{overlay.position.x.toFixed(0)}%, {overlay.position.y.toFixed(0)}%</span>
                      </Box>
                      <Box className="flex items-center space-x-1">
                        <FormatSize fontSize="small" />
                        <span>{overlay.style.fontSize}px</span>
                      </Box>
                      <Box className="flex items-center space-x-1">
                        <span style={{ 
                          display: 'inline-block',
                          width: '12px',
                          height: '12px',
                          backgroundColor: overlay.style.color,
                          borderRadius: '2px',
                          border: '1px solid #ccc'
                        }}></span>
                        <span>{overlay.style.fontFamily}</span>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              ))
            )}
          </Box>
        </CardContent>
      </Card>

      {/* Add Overlay Dialog */}
      <Dialog open={addDialog} onClose={() => setAddDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Text Overlay</DialogTitle>
        <DialogContent>
          <Box className="space-y-4 pt-2">
            <TextField
              fullWidth
              label="Overlay Text"
              value={newOverlay.text}
              onChange={(e) => setNewOverlay({ ...newOverlay, text: e.target.value })}
              placeholder="Enter overlay text..."
            />

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Start Time (seconds)"
                  type="number"
                  value={newOverlay.startTime}
                  onChange={(e) => setNewOverlay({ ...newOverlay, startTime: Number(e.target.value) })}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="End Time (seconds)"
                  type="number"
                  value={newOverlay.endTime}
                  onChange={(e) => setNewOverlay({ ...newOverlay, endTime: Number(e.target.value) })}
                />
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography gutterBottom>Horizontal Position: {newOverlay.position?.x}%</Typography>
                <Slider
                  value={newOverlay.position?.x || 50}
                  onChange={(_, value) => setNewOverlay({
                    ...newOverlay,
                    position: { ...newOverlay.position!, x: value as number }
                  })}
                  min={0}
                  max={100}
                />
              </Grid>
              <Grid item xs={6}>
                <Typography gutterBottom>Vertical Position: {newOverlay.position?.y}%</Typography>
                <Slider
                  value={newOverlay.position?.y || 50}
                  onChange={(_, value) => setNewOverlay({
                    ...newOverlay,
                    position: { ...newOverlay.position!, y: value as number }
                  })}
                  min={0}
                  max={100}
                />
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Font Family</InputLabel>
                  <Select
                    value={newOverlay.style?.fontFamily || 'Arial'}
                    onChange={(e) => setNewOverlay({
                      ...newOverlay,
                      style: { ...newOverlay.style!, fontFamily: e.target.value }
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
              <Grid item xs={6}>
                <FormControl fullWidth>
                  <InputLabel>Animation</InputLabel>
                  <Select
                    value={newOverlay.animation || 'fade'}
                    onChange={(e) => setNewOverlay({ ...newOverlay, animation: e.target.value as any })}
                  >
                    {animations.map(anim => (
                      <MenuItem key={anim.value} value={anim.value}>
                        {anim.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            <Grid container spacing={2}>
              <Grid item xs={4}>
                <Typography gutterBottom>Font Size: {newOverlay.style?.fontSize}px</Typography>
                <Slider
                  value={newOverlay.style?.fontSize || 24}
                  onChange={(_, value) => setNewOverlay({
                    ...newOverlay,
                    style: { ...newOverlay.style!, fontSize: value as number }
                  })}
                  min={12}
                  max={72}
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  label="Text Color"
                  type="color"
                  value={newOverlay.style?.color || '#ffffff'}
                  onChange={(e) => setNewOverlay({
                    ...newOverlay,
                    style: { ...newOverlay.style!, color: e.target.value }
                  })}
                />
              </Grid>
              <Grid item xs={4}>
                <FormControl fullWidth>
                  <InputLabel>Font Weight</InputLabel>
                  <Select
                    value={newOverlay.style?.fontWeight || 'bold'}
                    onChange={(e) => setNewOverlay({
                      ...newOverlay,
                      style: { ...newOverlay.style!, fontWeight: e.target.value as 'normal' | 'bold' }
                    })}
                  >
                    <MenuItem value="normal">Normal</MenuItem>
                    <MenuItem value="bold">Bold</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAddDialog(false)}>Cancel</Button>
          <Button
            onClick={handleAddOverlay}
            variant="contained"
            disabled={!newOverlay.text?.trim() || (newOverlay.startTime! >= newOverlay.endTime!)}
          >
            Add Overlay
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Overlay Dialog */}
      <Dialog
        open={!!editingOverlay}
        onClose={() => setEditingOverlay(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Edit Overlay</DialogTitle>
        <DialogContent>
          {editingOverlay && (
            <Box className="space-y-4 pt-2">
              <TextField
                fullWidth
                label="Overlay Text"
                value={editingOverlay.text}
                onChange={(e) => setEditingOverlay({ ...editingOverlay, text: e.target.value })}
              />

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Start Time (seconds)"
                    type="number"
                    value={editingOverlay.startTime}
                    onChange={(e) => setEditingOverlay({ ...editingOverlay, startTime: Number(e.target.value) })}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="End Time (seconds)"
                    type="number"
                    value={editingOverlay.endTime}
                    onChange={(e) => setEditingOverlay({ ...editingOverlay, endTime: Number(e.target.value) })}
                  />
                </Grid>
              </Grid>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography gutterBottom>Horizontal Position: {editingOverlay.position.x}%</Typography>
                  <Slider
                    value={editingOverlay.position.x}
                    onChange={(_, value) => setEditingOverlay({
                      ...editingOverlay,
                      position: { ...editingOverlay.position, x: value as number }
                    })}
                    min={0}
                    max={100}
                  />
                </Grid>
                <Grid item xs={6}>
                  <Typography gutterBottom>Vertical Position: {editingOverlay.position.y}%</Typography>
                  <Slider
                    value={editingOverlay.position.y}
                    onChange={(_, value) => setEditingOverlay({
                      ...editingOverlay,
                      position: { ...editingOverlay.position, y: value as number }
                    })}
                    min={0}
                    max={100}
                  />
                </Grid>
              </Grid>

              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Font Family</InputLabel>
                    <Select
                      value={editingOverlay.style.fontFamily}
                      onChange={(e) => setEditingOverlay({
                        ...editingOverlay,
                        style: { ...editingOverlay.style, fontFamily: e.target.value }
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
                <Grid item xs={6}>
                  <FormControl fullWidth>
                    <InputLabel>Animation</InputLabel>
                    <Select
                      value={editingOverlay.animation || 'fade'}
                      onChange={(e) => setEditingOverlay({ ...editingOverlay, animation: e.target.value as any })}
                    >
                      {animations.map(anim => (
                        <MenuItem key={anim.value} value={anim.value}>
                          {anim.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>

              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <Typography gutterBottom>Font Size: {editingOverlay.style.fontSize}px</Typography>
                  <Slider
                    value={editingOverlay.style.fontSize}
                    onChange={(_, value) => setEditingOverlay({
                      ...editingOverlay,
                      style: { ...editingOverlay.style, fontSize: value as number }
                    })}
                    min={12}
                    max={72}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Text Color"
                    type="color"
                    value={editingOverlay.style.color}
                    onChange={(e) => setEditingOverlay({
                      ...editingOverlay,
                      style: { ...editingOverlay.style, color: e.target.value }
                    })}
                  />
                </Grid>
                <Grid item xs={4}>
                  <FormControl fullWidth>
                    <InputLabel>Font Weight</InputLabel>
                    <Select
                      value={editingOverlay.style.fontWeight}
                      onChange={(e) => setEditingOverlay({
                        ...editingOverlay,
                        style: { ...editingOverlay.style, fontWeight: e.target.value as 'normal' | 'bold' }
                      })}
                    >
                      <MenuItem value="normal">Normal</MenuItem>
                      <MenuItem value="bold">Bold</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingOverlay(null)}>Cancel</Button>
          <Button onClick={handleSaveEdit} variant="contained">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default OverlayEditor;