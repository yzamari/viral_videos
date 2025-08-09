import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  Avatar,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Chip,
  LinearProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  useTheme,
  Skeleton,
  Alert,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Campaign,
  Visibility,
  MouseIcon,
  MonetizationOn,
  Analytics,
  Refresh,
  Launch,
  PlayArrow,
  Pause,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from 'recharts';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/store';
import { dashboardActions, campaignsActions } from '../store/store';
import { apiClient } from '../services/api';
import { DashboardMetrics, Campaign as CampaignType } from '../types';

interface MetricCardProps {
  title: string;
  value: string | number;
  change: number;
  icon: React.ReactElement;
  color: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  format?: 'currency' | 'percentage' | 'number';
}

const MetricCard: React.FC<MetricCardProps> = ({ 
  title, 
  value, 
  change, 
  icon, 
  color,
  format = 'number' 
}) => {
  const theme = useTheme();
  const isPositive = change >= 0;

  const formatValue = (val: string | number) => {
    if (typeof val === 'string') return val;
    
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD',
          minimumFractionDigits: 0,
        }).format(val);
      case 'percentage':
        return `${val.toFixed(1)}%`;
      default:
        return new Intl.NumberFormat('en-US').format(val);
    }
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Avatar sx={{ bgcolor: `${color}.main`, width: 56, height: 56 }}>
            {icon}
          </Avatar>
          <Box textAlign="right">
            <Box display="flex" alignItems="center">
              {isPositive ? (
                <TrendingUp color="success" sx={{ mr: 0.5 }} />
              ) : (
                <TrendingDown color="error" sx={{ mr: 0.5 }} />
              )}
              <Typography
                variant="body2"
                color={isPositive ? 'success.main' : 'error.main'}
                fontWeight="bold"
              >
                {Math.abs(change).toFixed(1)}%
              </Typography>
            </Box>
          </Box>
        </Box>
        <Typography variant="h4" component="div" fontWeight="bold" gutterBottom>
          {formatValue(value)}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );
};

const Dashboard: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  
  const { metrics, loading, error, lastUpdated } = useAppSelector(state => state.dashboard);
  const { campaigns } = useAppSelector(state => state.campaigns);

  const [timeframe, setTimeframe] = useState('7d');
  const [chartData, setChartData] = useState<any[]>([]);
  const [platformData, setPlatformData] = useState<any[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, [timeframe]);

  const loadDashboardData = async () => {
    try {
      dispatch(dashboardActions.setLoading({ isLoading: true, message: 'Loading dashboard...' }));
      
      const [metricsResponse, campaignsResponse] = await Promise.all([
        apiClient.getDashboardMetrics(timeframe),
        apiClient.getCampaigns(1, 10)
      ]);

      dispatch(dashboardActions.setMetrics(metricsResponse.data));
      dispatch(campaignsActions.setCampaigns({
        campaigns: campaignsResponse.data,
        totalCount: campaignsResponse.pagination.total
      }));

      // Generate sample chart data (replace with real data from API)
      generateChartData();
      generatePlatformData();

    } catch (error: any) {
      console.error('Failed to load dashboard:', error);
      dispatch(dashboardActions.setError({
        hasError: true,
        message: error.message || 'Failed to load dashboard data'
      }));
    }
  };

  const generateChartData = () => {
    // Sample data - replace with real API data
    const data = [];
    const now = new Date();
    const days = timeframe === '7d' ? 7 : timeframe === '30d' ? 30 : 90;
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      
      data.push({
        date: date.toISOString().split('T')[0],
        impressions: Math.floor(Math.random() * 10000) + 5000,
        clicks: Math.floor(Math.random() * 1000) + 200,
        conversions: Math.floor(Math.random() * 100) + 20,
        revenue: Math.floor(Math.random() * 5000) + 1000,
      });
    }
    
    setChartData(data);
  };

  const generatePlatformData = () => {
    const platforms = [
      { name: 'YouTube', value: 45, color: '#FF0000' },
      { name: 'TikTok', value: 30, color: '#000000' },
      { name: 'Instagram', value: 20, color: '#E4405F' },
      { name: 'Facebook', value: 5, color: '#4267B2' },
    ];
    setPlatformData(platforms);
  };

  const handleRefresh = () => {
    loadDashboardData();
  };

  const handleTimeframeChange = (newTimeframe: string) => {
    setTimeframe(newTimeframe);
  };

  const getStatusColor = (status: CampaignType['status']) => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'completed': return 'info';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const toggleCampaignStatus = async (campaign: CampaignType) => {
    try {
      if (campaign.status === 'active') {
        await apiClient.pauseCampaign(campaign.id);
      } else if (campaign.status === 'paused') {
        await apiClient.resumeCampaign(campaign.id);
      }
      loadDashboardData(); // Refresh data
    } catch (error: any) {
      console.error('Failed to toggle campaign status:', error);
    }
  };

  if (loading.isLoading && !metrics) {
    return (
      <Box>
        <Grid container spacing={3} mb={3}>
          {Array.from({ length: 4 }).map((_, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Card>
                <CardContent>
                  <Skeleton variant="circular" width={56} height={56} />
                  <Skeleton variant="text" width="60%" sx={{ mt: 2 }} />
                  <Skeleton variant="text" width="100%" />
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
        <Skeleton variant="rectangular" height={400} />
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" component="h1" fontWeight="bold" gutterBottom>
            Dashboard Overview
          </Typography>
          {lastUpdated && (
            <Typography variant="body2" color="text.secondary">
              Last updated: {new Date(lastUpdated).toLocaleString()}
            </Typography>
          )}
        </Box>
        <Box display="flex" gap={2}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Timeframe</InputLabel>
            <Select
              value={timeframe}
              onChange={(e) => handleTimeframeChange(e.target.value)}
              label="Timeframe"
            >
              <MenuItem value="7d">7 Days</MenuItem>
              <MenuItem value="30d">30 Days</MenuItem>
              <MenuItem value="90d">90 Days</MenuItem>
            </Select>
          </FormControl>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={handleRefresh}
            disabled={loading.isLoading}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Campaign />}
            onClick={() => navigate('/create-campaign')}
          >
            Create Campaign
          </Button>
        </Box>
      </Box>

      {error.hasError && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => dispatch(dashboardActions.clearError())}>
          {error.message}
        </Alert>
      )}

      {/* Metrics Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Campaigns"
            value={metrics?.totalCampaigns || 0}
            change={12.5}
            icon={<Campaign />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Impressions"
            value={metrics?.totalImpressions || 0}
            change={8.3}
            icon={<Visibility />}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Click-Through Rate"
            value={metrics?.averageCTR || 0}
            change={-2.1}
            icon={<MouseIcon />}
            color="warning"
            format="percentage"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Spent"
            value={metrics?.totalSpent || 0}
            change={15.7}
            icon={<MonetizationOn />}
            color="success"
            format="currency"
          />
        </Grid>
      </Grid>

      {/* Charts Row */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Trends
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area
                    type="monotone"
                    dataKey="impressions"
                    stackId="1"
                    stroke={theme.palette.primary.main}
                    fill={theme.palette.primary.main}
                    fillOpacity={0.6}
                  />
                  <Area
                    type="monotone"
                    dataKey="clicks"
                    stackId="1"
                    stroke={theme.palette.secondary.main}
                    fill={theme.palette.secondary.main}
                    fillOpacity={0.6}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Platform Distribution
              </Typography>
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={platformData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {platformData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Active Campaigns and Recent Activity */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Active Campaigns
                </Typography>
                <Button
                  size="small"
                  endIcon={<Launch />}
                  onClick={() => navigate('/campaigns')}
                >
                  View All
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Campaign</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell align="right">Budget</TableCell>
                      <TableCell align="right">Spent</TableCell>
                      <TableCell align="right">CTR</TableCell>
                      <TableCell align="center">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {campaigns.slice(0, 5).map((campaign) => (
                      <TableRow key={campaign.id}>
                        <TableCell>
                          <Box>
                            <Typography variant="subtitle2" fontWeight="bold">
                              {campaign.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {campaign.platforms.join(', ')}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={campaign.status}
                            color={getStatusColor(campaign.status)}
                            size="small"
                            variant="outlined"
                          />
                        </TableCell>
                        <TableCell align="right">
                          ${campaign.budget.toLocaleString()}
                        </TableCell>
                        <TableCell align="right">
                          <Box>
                            ${campaign.spent.toLocaleString()}
                            <LinearProgress
                              variant="determinate"
                              value={(campaign.spent / campaign.budget) * 100}
                              sx={{ mt: 1, width: 80 }}
                            />
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          {campaign.performance.ctr.toFixed(2)}%
                        </TableCell>
                        <TableCell align="center">
                          <IconButton
                            size="small"
                            onClick={() => toggleCampaignStatus(campaign)}
                            color={campaign.status === 'active' ? 'warning' : 'success'}
                          >
                            {campaign.status === 'active' ? <Pause /> : <PlayArrow />}
                          </IconButton>
                          <IconButton
                            size="small"
                            onClick={() => navigate(`/campaigns/${campaign.id}`)}
                          >
                            <Analytics />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Recent Activity
              </Typography>
              <List dense>
                {metrics?.recentActivity?.slice(0, 6).map((activity, index) => (
                  <ListItem key={activity.id} divider={index < 5}>
                    <ListItemAvatar>
                      <Avatar sx={{ bgcolor: 'primary.main', width: 32, height: 32 }}>
                        <Campaign fontSize="small" />
                      </Avatar>
                    </ListItemAvatar>
                    <ListItemText
                      primary={activity.title}
                      secondary={
                        <>
                          <Typography component="span" variant="body2">
                            {activity.description}
                          </Typography>
                          <br />
                          <Typography component="span" variant="caption" color="text.secondary">
                            {new Date(activity.timestamp).toRelative?.() || 
                             new Date(activity.timestamp).toLocaleString()}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                )) || (
                  <ListItem>
                    <ListItemText
                      primary="No recent activity"
                      secondary="Activities will appear here as they happen"
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;