import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Button,
  IconButton,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  ListItemButton,
  Avatar,
  Badge,
  Alert,
  Skeleton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tabs,
  Tab,
  LinearProgress,
  Tooltip,
  Divider,
  Fade,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Whatshot,
  Search,
  FilterList,
  Refresh,
  Bookmark,
  BookmarkBorder,
  Campaign,
  Psychology,
  Speed,
  Public,
  Schedule,
  VideoLibrary,
  Share,
  ContentCopy,
  Lightbulb,
  Star,
} from '@mui/icons-material';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as RechartsTooltip, 
  ResponsiveContainer,
  AreaChart,
  Area,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/store';
import { trendingActions } from '../store/store';
import { apiClient } from '../services/api';
import { TrendingTopic } from '../types';

interface TrendingCardProps {
  topic: TrendingTopic;
  onBookmark: (topic: TrendingTopic) => void;
  onCreateCampaign: (topic: TrendingTopic) => void;
  isBookmarked?: boolean;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index}>
    {value === index && <Box sx={{ pt: 3 }}>{children}</Box>}
  </div>
);

const TrendingCard: React.FC<TrendingCardProps> = ({ 
  topic, 
  onBookmark, 
  onCreateCampaign,
  isBookmarked = false 
}) => {
  const [expanded, setExpanded] = useState(false);

  const getScoreColor = (score: number) => {
    if (score >= 80) return '#FF5722'; // Hot
    if (score >= 60) return '#FF9800'; // Trending
    if (score >= 40) return '#FFC107'; // Warm
    return '#4CAF50'; // Emerging
  };

  const getScoreLabel = (score: number) => {
    if (score >= 80) return 'HOT';
    if (score >= 60) return 'TRENDING';
    if (score >= 40) return 'WARM';
    return 'EMERGING';
  };

  const getCompetitionColor = (level: string) => {
    switch (level) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'info';
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return '😊';
      case 'negative': return '😞';
      default: return '😐';
    }
  };

  return (
    <Card sx={{ height: '100%', transition: 'transform 0.2s', '&:hover': { transform: 'translateY(-2px)' } }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box flex={1}>
            <Box display="flex" alignItems="center" mb={1}>
              <Chip
                label={getScoreLabel(topic.trending_score)}
                size="small"
                sx={{
                  bgcolor: getScoreColor(topic.trending_score),
                  color: 'white',
                  fontWeight: 'bold',
                  mr: 1
                }}
              />
              <Typography variant="h6" component="div" fontWeight="bold">
                {topic.keyword}
              </Typography>
            </Box>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {topic.category}
            </Typography>
          </Box>
          <Box display="flex" alignItems="center">
            <Typography variant="h4" fontWeight="bold" color={getScoreColor(topic.trending_score)}>
              {topic.trending_score}
            </Typography>
            <IconButton onClick={() => onBookmark(topic)}>
              {isBookmarked ? <Bookmark color="primary" /> : <BookmarkBorder />}
            </IconButton>
          </Box>
        </Box>

        <Grid container spacing={2} mb={2}>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center">
              <Speed fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">
                Search Volume: {topic.search_volume.toLocaleString()}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center">
              <Typography variant="caption" color="text.secondary" sx={{ mr: 0.5 }}>
                {getSentimentIcon(topic.sentiment)}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {topic.sentiment}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6}>
            <Chip
              label={`${topic.competition_level} competition`}
              size="small"
              color={getCompetitionColor(topic.competition_level)}
              variant="outlined"
            />
          </Grid>
          <Grid item xs={6}>
            <Box display="flex" alignItems="center">
              <Public fontSize="small" sx={{ mr: 0.5, color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">
                {topic.platforms.length} platforms
              </Typography>
            </Box>
          </Grid>
        </Grid>

        <Box mb={2}>
          <Typography variant="caption" color="text.secondary" gutterBottom display="block">
            Platforms:
          </Typography>
          <Box display="flex" flexWrap="wrap" gap={0.5}>
            {topic.platforms.map((platform) => (
              <Chip key={platform} label={platform} size="small" variant="outlined" />
            ))}
          </Box>
        </Box>

        {expanded && (
          <Fade in={expanded}>
            <Box>
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle2" gutterBottom>
                Related Keywords
              </Typography>
              <Box display="flex" flexWrap="wrap" gap={0.5} mb={2}>
                {topic.related_keywords.slice(0, 5).map((keyword) => (
                  <Chip key={keyword} label={keyword} size="small" />
                ))}
              </Box>

              <Typography variant="subtitle2" gutterBottom>
                Content Suggestions
              </Typography>
              <List dense>
                {topic.content_suggestions.slice(0, 3).map((suggestion, index) => (
                  <ListItem key={index} sx={{ py: 0.5 }}>
                    <ListItemAvatar>
                      <Avatar sx={{ width: 24, height: 24, bgcolor: 'primary.main' }}>
                        <Lightbulb sx={{ fontSize: 14 }} />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={suggestion}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                ))}
              </List>

              <Typography variant="subtitle2" gutterBottom>
                Optimal Timing
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Best days: {topic.optimal_timing.best_days.join(', ')}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Best hours: {topic.optimal_timing.best_hours.join(', ')}
              </Typography>
            </Box>
          </Fade>
        )}

        <Box display="flex" justifyContent="space-between" alignItems="center" mt={2}>
          <Button
            size="small"
            onClick={() => setExpanded(!expanded)}
          >
            {expanded ? 'Show Less' : 'Show More'}
          </Button>
          <Box display="flex" gap={1}>
            <Button
              size="small"
              variant="outlined"
              startIcon={<Campaign />}
              onClick={() => onCreateCampaign(topic)}
            >
              Create Campaign
            </Button>
            <IconButton size="small">
              <ContentCopy fontSize="small" />
            </IconButton>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
};

const Trending: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  
  const {
    topics,
    viralOpportunities,
    totalCount,
    currentPage,
    pageSize,
    loading,
    error,
    lastUpdated
  } = useAppSelector(state => state.trending);

  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [platformFilter, setPlatformFilter] = useState('');
  const [bookmarkedTopics, setBookmarkedTopics] = useState<Set<string>>(new Set());
  const [selectedTopic, setSelectedTopic] = useState<TrendingTopic | null>(null);
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);

  const categories = ['Technology', 'Entertainment', 'Sports', 'Politics', 'Health', 'Business', 'Lifestyle'];
  const platforms = ['YouTube', 'TikTok', 'Instagram', 'Facebook', 'Twitter'];

  useEffect(() => {
    loadTrendingData();
  }, [categoryFilter, platformFilter]);

  const loadTrendingData = async () => {
    try {
      dispatch(trendingActions.setLoading({ isLoading: true, message: 'Loading trending topics...' }));
      
      const [topicsResponse, viralResponse] = await Promise.all([
        apiClient.getTrendingTopics(currentPage, pageSize, categoryFilter, platformFilter),
        apiClient.getViralOpportunities()
      ]);

      dispatch(trendingActions.setTopics({
        topics: topicsResponse.data,
        totalCount: topicsResponse.pagination.total
      }));
      dispatch(trendingActions.setViralOpportunities(viralResponse.data));

    } catch (error: any) {
      console.error('Failed to load trending topics:', error);
      dispatch(trendingActions.setError({
        hasError: true,
        message: error.message || 'Failed to load trending topics'
      }));
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      const response = await apiClient.searchTrendingTopics(searchQuery);
      dispatch(trendingActions.setTopics({
        topics: response.data,
        totalCount: response.data.length
      }));
    } catch (error: any) {
      console.error('Search failed:', error);
    }
  };

  const handleBookmark = (topic: TrendingTopic) => {
    const newBookmarked = new Set(bookmarkedTopics);
    if (newBookmarked.has(topic.id)) {
      newBookmarked.delete(topic.id);
    } else {
      newBookmarked.add(topic.id);
    }
    setBookmarkedTopics(newBookmarked);
  };

  const handleCreateCampaign = (topic: TrendingTopic) => {
    // Navigate to create campaign with pre-filled data
    navigate('/create-campaign', {
      state: {
        trendingTopic: topic,
        prefilledData: {
          targetAudience: {
            interests: [topic.keyword, ...topic.related_keywords.slice(0, 2)],
            demographics: topic.demographics,
          },
          platforms: topic.platforms,
        }
      }
    });
  };

  const handleTopicDetail = (topic: TrendingTopic) => {
    setSelectedTopic(topic);
    setDetailDialogOpen(true);
  };

  const filteredTopics = topics.filter(topic =>
    topic.keyword.toLowerCase().includes(searchQuery.toLowerCase()) ||
    topic.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getViralOpportunityChart = () => {
    return viralOpportunities.map(topic => ({
      keyword: topic.keyword,
      score: topic.trending_score,
      volume: topic.search_volume / 1000, // Scale down for chart
      competition: topic.competition_level === 'low' ? 3 : topic.competition_level === 'medium' ? 2 : 1
    }));
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Trending & Viral Opportunities
          </Typography>
          {lastUpdated && (
            <Typography variant="body2" color="text.secondary">
              Last updated: {new Date(lastUpdated).toLocaleString()}
            </Typography>
          )}
        </Box>
        <Box display="flex" gap={2}>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={loadTrendingData}
            disabled={loading.isLoading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<VideoLibrary />}
            onClick={() => navigate('/videos')}
          >
            Generate Content
          </Button>
        </Box>
      </Box>

      {error.hasError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => dispatch(trendingActions.clearError())}>
          {error.message}
        </Alert>
      )}

      {/* Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                size="small"
                placeholder="Search trending topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                InputProps={{
                  endAdornment: (
                    <IconButton size="small" onClick={handleSearch}>
                      <Search />
                    </IconButton>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Category</InputLabel>
                <Select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  label="Category"
                >
                  <MenuItem value="">All Categories</MenuItem>
                  {categories.map((category) => (
                    <MenuItem key={category} value={category}>
                      {category}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Platform</InputLabel>
                <Select
                  value={platformFilter}
                  onChange={(e) => setPlatformFilter(e.target.value)}
                  label="Platform"
                >
                  <MenuItem value="">All Platforms</MenuItem>
                  {platforms.map((platform) => (
                    <MenuItem key={platform} value={platform}>
                      {platform}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={2}>
              <Button
                fullWidth
                variant="outlined"
                startIcon={<FilterList />}
                onClick={() => {
                  setCategoryFilter('');
                  setPlatformFilter('');
                  setSearchQuery('');
                }}
              >
                Clear
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Card>
        {loading.isLoading && <LinearProgress />}
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={(_, newValue) => setActiveTab(newValue)}>
            <Tab label={`All Trending (${filteredTopics.length})`} />
            <Tab 
              label={
                <Badge badgeContent={viralOpportunities.length} color="error">
                  Viral Opportunities
                </Badge>
              }
            />
            <Tab 
              label={
                <Badge badgeContent={bookmarkedTopics.size} color="primary">
                  Bookmarked
                </Badge>
              }
            />
          </Tabs>
        </Box>

        {/* All Trending Tab */}
        <TabPanel value={activeTab} index={0}>
          <Box p={3}>
            {loading.isLoading && filteredTopics.length === 0 ? (
              <Grid container spacing={3}>
                {Array.from({ length: 6 }).map((_, index) => (
                  <Grid item xs={12} md={6} lg={4} key={index}>
                    <Skeleton variant="rectangular" height={300} />
                  </Grid>
                ))}
              </Grid>
            ) : (
              <Grid container spacing={3}>
                {filteredTopics.map((topic) => (
                  <Grid item xs={12} md={6} lg={4} key={topic.id}>
                    <TrendingCard
                      topic={topic}
                      onBookmark={handleBookmark}
                      onCreateCampaign={handleCreateCampaign}
                      isBookmarked={bookmarkedTopics.has(topic.id)}
                    />
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        </TabPanel>

        {/* Viral Opportunities Tab */}
        <TabPanel value={activeTab} index={1}>
          <Box p={3}>
            <Grid container spacing={3}>
              <Grid item xs={12} lg={8}>
                <Paper sx={{ p: 2, height: 400 }}>
                  <Typography variant="h6" gutterBottom>
                    Viral Opportunity Score vs Search Volume
                  </Typography>
                  <ResponsiveContainer width="100%" height="90%">
                    <AreaChart data={getViralOpportunityChart()}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="keyword" />
                      <YAxis />
                      <RechartsTooltip />
                      <Area
                        type="monotone"
                        dataKey="score"
                        stroke="#FF5722"
                        fill="#FF5722"
                        fillOpacity={0.6}
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              <Grid item xs={12} lg={4}>
                <Paper sx={{ p: 2, height: 400 }}>
                  <Typography variant="h6" gutterBottom>
                    Top Viral Opportunities
                  </Typography>
                  <List sx={{ overflowY: 'auto', height: '90%' }}>
                    {viralOpportunities.slice(0, 10).map((topic, index) => (
                      <ListItemButton
                        key={topic.id}
                        onClick={() => handleTopicDetail(topic)}
                        sx={{ mb: 1, borderRadius: 1 }}
                      >
                        <ListItemAvatar>
                          <Avatar sx={{ bgcolor: '#FF5722' }}>
                            <Star />
                          </Avatar>
                        </ListItemAvatar>
                        <ListItemText
                          primary={topic.keyword}
                          secondary={`Score: ${topic.trending_score} • ${topic.search_volume.toLocaleString()} searches`}
                        />
                        <Chip
                          label={`#${index + 1}`}
                          size="small"
                          color="error"
                          variant="outlined"
                        />
                      </ListItemButton>
                    ))}
                  </List>
                </Paper>
              </Grid>
            </Grid>

            <Box mt={3}>
              <Typography variant="h6" gutterBottom>
                Viral Opportunity Details
              </Typography>
              <Grid container spacing={3}>
                {viralOpportunities.map((topic) => (
                  <Grid item xs={12} md={6} lg={4} key={topic.id}>
                    <TrendingCard
                      topic={topic}
                      onBookmark={handleBookmark}
                      onCreateCampaign={handleCreateCampaign}
                      isBookmarked={bookmarkedTopics.has(topic.id)}
                    />
                  </Grid>
                ))}
              </Grid>
            </Box>
          </Box>
        </TabPanel>

        {/* Bookmarked Tab */}
        <TabPanel value={activeTab} index={2}>
          <Box p={3}>
            {bookmarkedTopics.size === 0 ? (
              <Alert severity="info">
                No bookmarked topics yet. Click the bookmark icon on any trending topic to save it here.
              </Alert>
            ) : (
              <Grid container spacing={3}>
                {filteredTopics
                  .filter(topic => bookmarkedTopics.has(topic.id))
                  .map((topic) => (
                    <Grid item xs={12} md={6} lg={4} key={topic.id}>
                      <TrendingCard
                        topic={topic}
                        onBookmark={handleBookmark}
                        onCreateCampaign={handleCreateCampaign}
                        isBookmarked={true}
                      />
                    </Grid>
                  ))}
              </Grid>
            )}
          </Box>
        </TabPanel>
      </Card>

      {/* Topic Detail Dialog */}
      <Dialog
        open={detailDialogOpen}
        onClose={() => setDetailDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedTopic?.keyword} - Detailed Analysis
        </DialogTitle>
        <DialogContent>
          {selectedTopic && (
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, height: 300 }}>
                  <Typography variant="h6" gutterBottom>
                    Trending History
                  </Typography>
                  <ResponsiveContainer width="100%" height="85%">
                    <LineChart data={selectedTopic.historical_data}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <RechartsTooltip />
                      <Line
                        type="monotone"
                        dataKey="score"
                        stroke="#2196F3"
                        strokeWidth={2}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, height: 300 }}>
                  <Typography variant="h6" gutterBottom>
                    Audience Profile
                  </Typography>
                  <ResponsiveContainer width="100%" height="85%">
                    <RadarChart data={[
                      { metric: 'Engagement', value: selectedTopic.trending_score },
                      { metric: 'Reach', value: Math.min(selectedTopic.search_volume / 1000, 100) },
                      { metric: 'Virality', value: selectedTopic.trending_score * 0.8 },
                      { metric: 'Competition', value: selectedTopic.competition_level === 'low' ? 20 : selectedTopic.competition_level === 'medium' ? 50 : 80 },
                      { metric: 'Sustainability', value: 60 },
                    ]}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="metric" />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} />
                      <Radar
                        name="Topic Analysis"
                        dataKey="value"
                        stroke="#8884d8"
                        fill="#8884d8"
                        fillOpacity={0.6}
                      />
                    </RadarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
            </Grid>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailDialogOpen(false)}>
            Close
          </Button>
          {selectedTopic && (
            <Button
              variant="contained"
              startIcon={<Campaign />}
              onClick={() => {
                setDetailDialogOpen(false);
                handleCreateCampaign(selectedTopic);
              }}
            >
              Create Campaign
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Trending;