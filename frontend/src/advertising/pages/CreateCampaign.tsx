import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Checkbox,
  FormControlLabel,
  FormGroup,
  FormLabel,
  RadioGroup,
  Radio,
  Slider,
  Chip,
  OutlinedInput,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Grid,
  Paper,
  Alert,
  LinearProgress,
  Divider,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  ArrowBack,
  ArrowForward,
  Campaign,
  TrendingUp,
  People,
  VideoLibrary,
  Settings,
  Preview,
  Save,
  Launch,
  Add,
  Delete,
  Help,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useAppDispatch, useAppSelector } from '../store/store';
import { campaignsActions } from '../store/store';
import { apiClient } from '../services/api';
import { CreateCampaignRequest, Video, TrendingTopic } from '../types';

const PLATFORMS = [
  { value: 'youtube', label: 'YouTube', color: '#FF0000' },
  { value: 'tiktok', label: 'TikTok', color: '#000000' },
  { value: 'instagram', label: 'Instagram', color: '#E4405F' },
  { value: 'facebook', label: 'Facebook', color: '#4267B2' },
  { value: 'twitter', label: 'Twitter', color: '#1DA1F2' },
];

const OBJECTIVES = [
  { value: 'brand_awareness', label: 'Brand Awareness', description: 'Increase recognition of your brand' },
  { value: 'engagement', label: 'Engagement', description: 'Get more likes, shares, and comments' },
  { value: 'conversions', label: 'Conversions', description: 'Drive actions like purchases or signups' },
  { value: 'traffic', label: 'Website Traffic', description: 'Bring visitors to your website' },
  { value: 'reach', label: 'Reach', description: 'Show your ads to the most people' },
];

const LANGUAGES = [
  'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Russian', 'Chinese', 'Japanese', 'Arabic'
];

const STEPS = [
  'Campaign Details',
  'Target Audience', 
  'Platform & Budget',
  'Content & Creative',
  'Review & Launch'
];

const validationSchema = Yup.object({
  name: Yup.string().required('Campaign name is required').min(3, 'Name must be at least 3 characters'),
  description: Yup.string().required('Description is required').min(10, 'Description must be at least 10 characters'),
  budget: Yup.number().required('Budget is required').min(100, 'Minimum budget is $100'),
  startDate: Yup.string().required('Start date is required'),
  platforms: Yup.array().min(1, 'Select at least one platform'),
  objectives: Yup.array().min(1, 'Select at least one objective'),
  callToAction: Yup.string().required('Call to action is required'),
});

const CreateCampaign: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const [activeStep, setActiveStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [videos, setVideos] = useState<Video[]>([]);
  const [trendingTopics, setTrendingTopics] = useState<TrendingTopic[]>([]);
  const [selectedVideos, setSelectedVideos] = useState<string[]>([]);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);

  const formik = useFormik<CreateCampaignRequest>({
    initialValues: {
      name: '',
      description: '',
      budget: 1000,
      startDate: new Date().toISOString().split('T')[0],
      endDate: '',
      targetAudience: {
        demographics: {
          ageMin: 18,
          ageMax: 65,
          gender: 'all',
        },
        interests: [],
        locations: ['United States'],
        languages: ['English'],
      },
      platforms: [],
      objectives: [],
      content: {
        videoIds: [],
        callToAction: '',
      },
    },
    validationSchema,
    onSubmit: async (values) => {
      handleCreateCampaign(values);
    },
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      const [videosResponse, trendingResponse] = await Promise.all([
        apiClient.getVideos(1, 20, 'ready'),
        apiClient.getTrendingTopics(1, 10)
      ]);
      
      setVideos(videosResponse.data);
      setTrendingTopics(trendingResponse.data);
    } catch (error: any) {
      console.error('Failed to load initial data:', error);
    }
  };

  const handleCreateCampaign = async (values: CreateCampaignRequest) => {
    try {
      setLoading(true);
      setError(null);

      const campaignData = {
        ...values,
        content: {
          ...values.content,
          videoIds: selectedVideos,
        },
      };

      const response = await apiClient.createCampaign(campaignData);
      dispatch(campaignsActions.addCampaign(response.data));

      // Navigate to campaigns list
      navigate('/campaigns');
    } catch (error: any) {
      setError(error.message || 'Failed to create campaign');
    } finally {
      setLoading(false);
    }
  };

  const handleNext = () => {
    if (activeStep === STEPS.length - 1) {
      formik.handleSubmit();
    } else {
      setActiveStep(prev => prev + 1);
    }
  };

  const handleBack = () => {
    setActiveStep(prev => prev - 1);
  };

  const handleVideoSelection = (videoId: string) => {
    setSelectedVideos(prev => 
      prev.includes(videoId) 
        ? prev.filter(id => id !== videoId)
        : [...prev, videoId]
    );
  };

  const getStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Campaign Basic Information
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Campaign Name"
                name="name"
                value={formik.values.name}
                onChange={formik.handleChange}
                error={formik.touched.name && Boolean(formik.errors.name)}
                helperText={formik.touched.name && formik.errors.name}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Budget (USD)"
                name="budget"
                type="number"
                value={formik.values.budget}
                onChange={formik.handleChange}
                error={formik.touched.budget && Boolean(formik.errors.budget)}
                helperText={formik.touched.budget && formik.errors.budget}
                required
                InputProps={{ inputProps: { min: 100 } }}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                name="description"
                multiline
                rows={4}
                value={formik.values.description}
                onChange={formik.handleChange}
                error={formik.touched.description && Boolean(formik.errors.description)}
                helperText={formik.touched.description && formik.errors.description}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Start Date"
                name="startDate"
                type="date"
                value={formik.values.startDate}
                onChange={formik.handleChange}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="End Date (Optional)"
                name="endDate"
                type="date"
                value={formik.values.endDate}
                onChange={formik.handleChange}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        );

      case 1:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Define Your Target Audience
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography gutterBottom>Age Range</Typography>
              <Box px={2}>
                <Slider
                  value={[formik.values.targetAudience.demographics.ageMin, formik.values.targetAudience.demographics.ageMax]}
                  onChange={(_, newValue) => {
                    const [min, max] = newValue as number[];
                    formik.setFieldValue('targetAudience.demographics.ageMin', min);
                    formik.setFieldValue('targetAudience.demographics.ageMax', max);
                  }}
                  valueLabelDisplay="auto"
                  min={13}
                  max={80}
                  marks={[
                    { value: 18, label: '18' },
                    { value: 25, label: '25' },
                    { value: 35, label: '35' },
                    { value: 45, label: '45' },
                    { value: 55, label: '55' },
                    { value: 65, label: '65+' },
                  ]}
                />
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <FormLabel>Gender</FormLabel>
                <RadioGroup
                  value={formik.values.targetAudience.demographics.gender}
                  onChange={(e) => formik.setFieldValue('targetAudience.demographics.gender', e.target.value)}
                >
                  <FormControlLabel value="all" control={<Radio />} label="All" />
                  <FormControlLabel value="male" control={<Radio />} label="Male" />
                  <FormControlLabel value="female" control={<Radio />} label="Female" />
                </RadioGroup>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Languages</InputLabel>
                <Select
                  multiple
                  value={formik.values.targetAudience.languages}
                  onChange={(e) => formik.setFieldValue('targetAudience.languages', e.target.value)}
                  input={<OutlinedInput label="Languages" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                >
                  {LANGUAGES.map((language) => (
                    <MenuItem key={language} value={language}>
                      {language}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Locations"
                value={formik.values.targetAudience.locations.join(', ')}
                onChange={(e) => formik.setFieldValue('targetAudience.locations', e.target.value.split(', '))}
                placeholder="United States, Canada, United Kingdom"
                helperText="Separate locations with commas"
              />
            </Grid>
          </Grid>
        );

      case 2:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Platforms & Objectives
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <FormLabel>Select Platforms</FormLabel>
                <FormGroup>
                  {PLATFORMS.map((platform) => (
                    <FormControlLabel
                      key={platform.value}
                      control={
                        <Checkbox
                          checked={formik.values.platforms.includes(platform.value as any)}
                          onChange={(e) => {
                            const platforms = formik.values.platforms;
                            if (e.target.checked) {
                              formik.setFieldValue('platforms', [...platforms, platform.value]);
                            } else {
                              formik.setFieldValue('platforms', platforms.filter(p => p !== platform.value));
                            }
                          }}
                        />
                      }
                      label={
                        <Box display="flex" alignItems="center">
                          <Avatar sx={{ bgcolor: platform.color, width: 24, height: 24, mr: 1 }}>
                            {platform.label[0]}
                          </Avatar>
                          {platform.label}
                        </Box>
                      }
                    />
                  ))}
                </FormGroup>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormLabel>Campaign Objectives</FormLabel>
              <List>
                {OBJECTIVES.map((objective) => (
                  <ListItemButton
                    key={objective.value}
                    selected={formik.values.objectives.includes(objective.value as any)}
                    onClick={() => {
                      const objectives = formik.values.objectives;
                      if (objectives.includes(objective.value as any)) {
                        formik.setFieldValue('objectives', objectives.filter(o => o !== objective.value));
                      } else {
                        formik.setFieldValue('objectives', [...objectives, objective.value]);
                      }
                    }}
                  >
                    <ListItemText
                      primary={objective.label}
                      secondary={objective.description}
                    />
                  </ListItemButton>
                ))}
              </List>
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info">
                <Typography variant="body2">
                  <strong>Trending Topics:</strong> Consider these trending topics for your campaign
                </Typography>
                <Box mt={1}>
                  {trendingTopics.slice(0, 5).map((topic) => (
                    <Chip
                      key={topic.id}
                      label={`${topic.keyword} (${topic.trending_score})`}
                      size="small"
                      sx={{ mr: 1, mb: 1 }}
                      onClick={() => {
                        // Add trending topic to interests
                        const interests = formik.values.targetAudience.interests;
                        if (!interests.includes(topic.keyword)) {
                          formik.setFieldValue('targetAudience.interests', [...interests, topic.keyword]);
                        }
                      }}
                    />
                  ))}
                </Box>
              </Alert>
            </Grid>
          </Grid>
        );

      case 3:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Select Content & Creative Assets
              </Typography>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Call to Action"
                name="content.callToAction"
                value={formik.values.content.callToAction}
                onChange={(e) => formik.setFieldValue('content.callToAction', e.target.value)}
                placeholder="Learn More, Shop Now, Sign Up, etc."
                required
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle1" gutterBottom>
                Select Videos for Your Campaign
              </Typography>
              <Grid container spacing={2}>
                {videos.map((video) => (
                  <Grid item xs={12} sm={6} md={4} key={video.id}>
                    <Card
                      sx={{
                        cursor: 'pointer',
                        border: selectedVideos.includes(video.id) ? 2 : 0,
                        borderColor: 'primary.main',
                      }}
                      onClick={() => handleVideoSelection(video.id)}
                    >
                      <Box
                        sx={{
                          height: 200,
                          backgroundImage: `url(${video.thumbnailUrl})`,
                          backgroundSize: 'cover',
                          backgroundPosition: 'center',
                          position: 'relative',
                        }}
                      >
                        {selectedVideos.includes(video.id) && (
                          <Box
                            sx={{
                              position: 'absolute',
                              top: 8,
                              right: 8,
                              bgcolor: 'primary.main',
                              color: 'white',
                              borderRadius: '50%',
                              p: 1,
                            }}
                          >
                            ✓
                          </Box>
                        )}
                      </Box>
                      <CardContent>
                        <Typography variant="subtitle2" noWrap>
                          {video.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {Math.floor(video.duration / 60)}:{(video.duration % 60).toString().padStart(2, '0')}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
              {selectedVideos.length === 0 && (
                <Alert severity="warning" sx={{ mt: 2 }}>
                  Please select at least one video for your campaign.
                </Alert>
              )}
            </Grid>
          </Grid>
        );

      case 4:
        return (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Review Your Campaign
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>Campaign Details</Typography>
                <Typography><strong>Name:</strong> {formik.values.name}</Typography>
                <Typography><strong>Budget:</strong> ${formik.values.budget.toLocaleString()}</Typography>
                <Typography><strong>Start Date:</strong> {formik.values.startDate}</Typography>
                {formik.values.endDate && (
                  <Typography><strong>End Date:</strong> {formik.values.endDate}</Typography>
                )}
              </Paper>

              <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>Target Audience</Typography>
                <Typography>
                  <strong>Age:</strong> {formik.values.targetAudience.demographics.ageMin}-{formik.values.targetAudience.demographics.ageMax}
                </Typography>
                <Typography><strong>Gender:</strong> {formik.values.targetAudience.demographics.gender}</Typography>
                <Typography><strong>Languages:</strong> {formik.values.targetAudience.languages.join(', ')}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={6}>
              <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>Platforms</Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {formik.values.platforms.map((platform) => (
                    <Chip key={platform} label={platform} size="small" />
                  ))}
                </Box>
              </Paper>

              <Paper sx={{ p: 2, mb: 2 }}>
                <Typography variant="subtitle2" gutterBottom>Objectives</Typography>
                <Box display="flex" flexWrap="wrap" gap={1}>
                  {formik.values.objectives.map((objective) => (
                    <Chip key={objective} label={objective} size="small" />
                  ))}
                </Box>
              </Paper>

              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" gutterBottom>Content</Typography>
                <Typography><strong>Call to Action:</strong> {formik.values.content.callToAction}</Typography>
                <Typography><strong>Videos Selected:</strong> {selectedVideos.length}</Typography>
              </Paper>
            </Grid>
          </Grid>
        );

      default:
        return 'Unknown step';
    }
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <IconButton onClick={() => navigate('/campaigns')} sx={{ mr: 2 }}>
          <ArrowBack />
        </IconButton>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Create New Campaign
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* Progress Stepper */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Stepper activeStep={activeStep} alternativeLabel>
            {STEPS.map((label) => (
              <Step key={label}>
                <StepLabel>{label}</StepLabel>
              </Step>
            ))}
          </Stepper>
        </CardContent>
      </Card>

      {/* Form Content */}
      <Card>
        <CardContent sx={{ p: 4 }}>
          {loading && <LinearProgress sx={{ mb: 2 }} />}
          
          <form onSubmit={formik.handleSubmit}>
            {getStepContent(activeStep)}

            {/* Navigation Buttons */}
            <Box display="flex" justifyContent="space-between" mt={4}>
              <Button
                onClick={handleBack}
                disabled={activeStep === 0}
                startIcon={<ArrowBack />}
              >
                Back
              </Button>

              <Box display="flex" gap={2}>
                {activeStep === STEPS.length - 1 && (
                  <Button
                    variant="outlined"
                    startIcon={<Preview />}
                    onClick={() => setPreviewDialogOpen(true)}
                  >
                    Preview
                  </Button>
                )}
                
                <Button
                  variant="contained"
                  onClick={handleNext}
                  disabled={loading}
                  endIcon={activeStep === STEPS.length - 1 ? <Launch /> : <ArrowForward />}
                >
                  {activeStep === STEPS.length - 1 ? 'Launch Campaign' : 'Next'}
                </Button>
              </Box>
            </Box>
          </form>
        </CardContent>
      </Card>

      {/* Preview Dialog */}
      <Dialog
        open={previewDialogOpen}
        onClose={() => setPreviewDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Campaign Preview</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            This is how your campaign will appear to your target audience.
          </Typography>
          {/* Add campaign preview component here */}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setPreviewDialogOpen(false)}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CreateCampaign;