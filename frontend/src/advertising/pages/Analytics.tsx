import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  ButtonGroup,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Avatar,
  Alert,
  Skeleton,
  Tab,
  Tabs,
  LinearProgress,
  IconButton,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Visibility,
  MouseIcon,
  MonetizationOn,
  People,
  Timer,
  Share,
  ThumbUp,
  Download,
  Refresh,
  DateRange,
  Campaign,
  Analytics as AnalyticsIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  ComposedChart,
  Legend,
} from 'recharts';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { useAppSelector } from '../store/store';
import { apiClient } from '../services/api';
import { Campaign as CampaignType } from '../types';

interface AnalyticsMetric {
  title: string;
  value: string | number;
  change: number;
  icon: React.ReactElement;
  color: string;
  format?: 'currency' | 'percentage' | 'number';
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div hidden={value !== index} style={{ paddingTop: 24 }}>
    {value === index && children}
  </div>
);

const MetricCard: React.FC<AnalyticsMetric> = ({ 
  title, 
  value, 
  change, 
  icon, 
  color,
  format = 'number' 
}) => {
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
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
          <Avatar sx={{ bgcolor: color, width: 48, height: 48 }}>
            {icon}
          </Avatar>
          <Box textAlign="right">
            <Box display="flex" alignItems="center">
              {isPositive ? (
                <TrendingUp color="success" fontSize="small" />
              ) : (
                <TrendingDown color="error" fontSize="small" />
              )}
              <Typography
                variant="body2"
                color={isPositive ? 'success.main' : 'error.main'}
                fontWeight="bold"
                ml={0.5}
              >
                {Math.abs(change).toFixed(1)}%
              </Typography>
            </Box>
          </Box>
        </Box>
        <Typography variant="h5" component="div" fontWeight="bold" gutterBottom>
          {formatValue(value)}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {title}
        </Typography>
      </CardContent>
    </Card>
  );
};

const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [timeframe, setTimeframe] = useState('7d');
  const [selectedCampaigns, setSelectedCampaigns] = useState<string[]>([]);
  const [startDate, setStartDate] = useState<Date | null>(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000));
  const [endDate, setEndDate] = useState<Date | null>(new Date());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [analyticsData, setAnalyticsData] = useState<any>(null);
  const [performanceData, setPerformanceData] = useState<any[]>([]);
  const [platformData, setPlatformData] = useState<any[]>([]);
  const [campaignComparison, setCampaignComparison] = useState<any[]>([]);
  const [demographicsData, setDemographicsData] = useState<any[]>([]);

  const { campaigns } = useAppSelector(state => state.campaigns);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeframe, selectedCampaigns, startDate, endDate]);

  const loadAnalyticsData = async () => {
    if (!startDate || !endDate) return;

    try {
      setLoading(true);
      setError(null);

      const startDateStr = startDate.toISOString().split('T')[0];
      const endDateStr = endDate.toISOString().split('T')[0];

      const [overviewResponse, comparisonResponse] = await Promise.all([
        apiClient.getAnalyticsOverview(startDateStr, endDateStr, [
          'impressions', 'clicks', 'conversions', 'revenue', 'ctr', 'cpm', 'roas'
        ]),
        selectedCampaigns.length > 0 
          ? apiClient.getPerformanceComparison(selectedCampaigns, startDateStr, endDateStr)
          : Promise.resolve({ data: [] })
      ]);

      setAnalyticsData(overviewResponse.data);
      setCampaignComparison(comparisonResponse.data);

      // Generate sample chart data (replace with real API data)
      generatePerformanceData();
      generatePlatformData();
      generateDemographicsData();

    } catch (error: any) {
      console.error('Failed to load analytics:', error);
      setError(error.message || 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const generatePerformanceData = () => {
    const data = [];
    const days = timeframe === '7d' ? 7 : timeframe === '30d' ? 30 : 90;
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      
      data.push({
        date: date.toISOString().split('T')[0],
        impressions: Math.floor(Math.random() * 10000) + 5000,
        clicks: Math.floor(Math.random() * 1000) + 200,
        conversions: Math.floor(Math.random() * 100) + 20,
        revenue: Math.floor(Math.random() * 5000) + 1000,
        ctr: (Math.random() * 5) + 1,
        cpm: (Math.random() * 10) + 5,
      });
    }
    
    setPerformanceData(data);
  };

  const generatePlatformData = () => {
    const platforms = [
      { name: 'YouTube', value: 45, color: '#FF0000', revenue: 12500 },
      { name: 'TikTok', value: 30, color: '#000000', revenue: 8200 },
      { name: 'Instagram', value: 20, color: '#E4405F', revenue: 5800 },
      { name: 'Facebook', value: 5, color: '#4267B2', revenue: 1500 },
    ];
    setPlatformData(platforms);
  };

  const generateDemographicsData = () => {
    const demographics = [
      { ageGroup: '18-24', male: 35, female: 45 },
      { ageGroup: '25-34', male: 45, female: 55 },
      { ageGroup: '35-44', male: 30, female: 40 },
      { ageGroup: '45-54', male: 25, female: 35 },
      { ageGroup: '55+', male: 15, female: 25 },
    ];
    setDemographicsData(demographics);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleTimeframeChange = (newTimeframe: string) => {
    setTimeframe(newTimeframe);
    
    // Update date range based on timeframe
    const end = new Date();
    let start = new Date();
    
    switch (newTimeframe) {
      case '7d':
        start.setDate(end.getDate() - 7);
        break;
      case '30d':
        start.setDate(end.getDate() - 30);
        break;
      case '90d':
        start.setDate(end.getDate() - 90);
        break;
    }
    
    setStartDate(start);
    setEndDate(end);
  };

  const handleCampaignSelection = (event: any) => {
    setSelectedCampaigns(event.target.value);
  };

  const exportData = () => {
    // Implement data export functionality
    console.log('Exporting analytics data...');
  };

  const metrics: AnalyticsMetric[] = analyticsData ? [
    {
      title: 'Total Impressions',
      value: analyticsData.totalImpressions || 0,
      change: 12.5,
      icon: <Visibility />,
      color: '#2196F3',
    },
    {
      title: 'Total Clicks',
      value: analyticsData.totalClicks || 0,
      change: 8.3,
      icon: <MouseIcon />,
      color: '#FF9800',
    },
    {
      title: 'Click-Through Rate',
      value: analyticsData.averageCTR || 0,
      change: -2.1,
      icon: <TrendingUp />,
      color: '#9C27B0',
      format: 'percentage',
    },
    {
      title: 'Total Revenue',
      value: analyticsData.totalRevenue || 0,
      change: 15.7,
      icon: <MonetizationOn />,
      color: '#4CAF50',
      format: 'currency',
    },
  ] : [];

  if (loading && !analyticsData) {
    return (
      <Box>
        <Grid container spacing={3} mb={3}>
          {Array.from({ length: 4 }).map((_, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <Skeleton variant="rectangular" height={140} />
            </Grid>
          ))}
        </Grid>
        <Skeleton variant="rectangular" height={400} />
      </Box>
    );
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns}>
      <Box>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Typography variant="h4" component="h1" fontWeight="bold">
            Analytics Dashboard
          </Typography>
          <Box display="flex" gap={2} alignItems="center">
            <ButtonGroup variant="outlined" size="small">
              <Button
                variant={timeframe === '7d' ? 'contained' : 'outlined'}
                onClick={() => handleTimeframeChange('7d')}
              >
                7D
              </Button>
              <Button
                variant={timeframe === '30d' ? 'contained' : 'outlined'}
                onClick={() => handleTimeframeChange('30d')}
              >
                30D
              </Button>
              <Button
                variant={timeframe === '90d' ? 'contained' : 'outlined'}
                onClick={() => handleTimeframeChange('90d')}
              >
                90D
              </Button>
            </ButtonGroup>
            
            <DatePicker
              label="Start Date"
              value={startDate}
              onChange={(newValue) => setStartDate(newValue)}
              slotProps={{ textField: { size: 'small' } }}
            />
            
            <DatePicker
              label="End Date"
              value={endDate}
              onChange={(newValue) => setEndDate(newValue)}
              slotProps={{ textField: { size: 'small' } }}
            />

            <Tooltip title="Refresh Data">
              <IconButton onClick={() => loadAnalyticsData()}>
                <Refresh />
              </IconButton>
            </Tooltip>

            <Button
              variant="outlined"
              startIcon={<Download />}
              onClick={exportData}
            >
              Export
            </Button>
          </Box>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 3 }}>
            {error}
          </Alert>
        )}

        {/* Metrics Cards */}
        <Grid container spacing={3} mb={3}>
          {metrics.map((metric, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <MetricCard {...metric} />
            </Grid>
          ))}
        </Grid>

        {/* Campaign Selection */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" gap={2}>
              <FormControl sx={{ minWidth: 200 }}>
                <InputLabel>Compare Campaigns</InputLabel>
                <Select
                  multiple
                  value={selectedCampaigns}
                  onChange={handleCampaignSelection}
                  label="Compare Campaigns"
                >
                  {campaigns.map((campaign) => (
                    <MenuItem key={campaign.id} value={campaign.id}>
                      {campaign.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <Typography variant="body2" color="text.secondary">
                Select campaigns to compare their performance
              </Typography>
            </Box>
          </CardContent>
        </Card>

        {/* Tabs */}
        <Card>
          {loading && <LinearProgress />}
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={activeTab} onChange={handleTabChange}>
              <Tab label="Performance Overview" />
              <Tab label="Platform Analysis" />
              <Tab label="Campaign Comparison" />
              <Tab label="Audience Demographics" />
            </Tabs>
          </Box>

          {/* Performance Overview Tab */}
          <TabPanel value={activeTab} index={0}>
            <Grid container spacing={3}>
              <Grid item xs={12} lg={8}>
                <Paper sx={{ p: 2, height: 400 }}>
                  <Typography variant="h6" gutterBottom>
                    Performance Trends
                  </Typography>
                  <ResponsiveContainer width="100%" height="90%">
                    <ComposedChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis yAxisId="left" />
                      <YAxis yAxisId="right" orientation="right" />
                      <RechartsTooltip />
                      <Legend />
                      <Area
                        yAxisId="left"
                        type="monotone"
                        dataKey="impressions"
                        stackId="1"
                        stroke="#2196F3"
                        fill="#2196F3"
                        fillOpacity={0.6}
                      />
                      <Bar yAxisId="right" dataKey="clicks" fill="#FF9800" />
                      <Line
                        yAxisId="right"
                        type="monotone"
                        dataKey="conversions"
                        stroke="#4CAF50"
                        strokeWidth={3}
                      />
                    </ComposedChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              
              <Grid item xs={12} lg={4}>
                <Paper sx={{ p: 2, height: 400 }}>
                  <Typography variant="h6" gutterBottom>
                    Top Performing Content
                  </Typography>
                  <Box sx={{ overflowY: 'auto', height: '90%' }}>
                    {campaigns.slice(0, 5).map((campaign, index) => (
                      <Box key={campaign.id} display="flex" alignItems="center" p={1} mb={1}>
                        <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
                          {index + 1}
                        </Avatar>
                        <Box flex={1}>
                          <Typography variant="subtitle2" noWrap>
                            {campaign.name}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            CTR: {campaign.performance.ctr.toFixed(2)}%
                          </Typography>
                        </Box>
                        <Chip
                          size="small"
                          label={`${campaign.performance.impressions.toLocaleString()}`}
                          color="primary"
                          variant="outlined"
                        />
                      </Box>
                    ))}
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Platform Analysis Tab */}
          <TabPanel value={activeTab} index={1}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, height: 400 }}>
                  <Typography variant="h6" gutterBottom>
                    Platform Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height="90%">
                    <PieChart>
                      <Pie
                        data={platformData}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                        outerRadius={120}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {platformData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Paper sx={{ p: 2, height: 400 }}>
                  <Typography variant="h6" gutterBottom>
                    Platform Performance
                  </Typography>
                  <TableContainer sx={{ height: '90%' }}>
                    <Table size="small">
                      <TableHead>
                        <TableRow>
                          <TableCell>Platform</TableCell>
                          <TableCell align="right">Impressions</TableCell>
                          <TableCell align="right">Revenue</TableCell>
                          <TableCell align="right">ROAS</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {platformData.map((platform) => (
                          <TableRow key={platform.name}>
                            <TableCell>
                              <Box display="flex" alignItems="center">
                                <Avatar
                                  sx={{ 
                                    bgcolor: platform.color, 
                                    width: 24, 
                                    height: 24, 
                                    mr: 1 
                                  }}
                                >
                                  {platform.name[0]}
                                </Avatar>
                                {platform.name}
                              </Box>
                            </TableCell>
                            <TableCell align="right">
                              {(platform.value * 1000).toLocaleString()}
                            </TableCell>
                            <TableCell align="right">
                              ${platform.revenue.toLocaleString()}
                            </TableCell>
                            <TableCell align="right">
                              {((platform.revenue / (platform.value * 100)) * 100).toFixed(1)}%
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>

          {/* Campaign Comparison Tab */}
          <TabPanel value={activeTab} index={2}>
            <Paper sx={{ p: 2, height: 500 }}>
              <Typography variant="h6" gutterBottom>
                Campaign Performance Comparison
              </Typography>
              {selectedCampaigns.length === 0 ? (
                <Alert severity="info">
                  Select campaigns from the dropdown above to compare their performance.
                </Alert>
              ) : (
                <ResponsiveContainer width="100%" height="90%">
                  <BarChart data={campaignComparison}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="impressions" fill="#2196F3" name="Impressions" />
                    <Bar dataKey="clicks" fill="#FF9800" name="Clicks" />
                    <Bar dataKey="conversions" fill="#4CAF50" name="Conversions" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </Paper>
          </TabPanel>

          {/* Audience Demographics Tab */}
          <TabPanel value={activeTab} index={3}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={8}>
                <Paper sx={{ p: 2, height: 400 }}>
                  <Typography variant="h6" gutterBottom>
                    Age & Gender Distribution
                  </Typography>
                  <ResponsiveContainer width="100%" height="90%">
                    <BarChart data={demographicsData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="ageGroup" />
                      <YAxis />
                      <RechartsTooltip />
                      <Legend />
                      <Bar dataKey="male" stackId="a" fill="#2196F3" name="Male" />
                      <Bar dataKey="female" stackId="a" fill="#E91E63" name="Female" />
                    </BarChart>
                  </ResponsiveContainer>
                </Paper>
              </Grid>
              
              <Grid item xs={12} md={4}>
                <Paper sx={{ p: 2, height: 400 }}>
                  <Typography variant="h6" gutterBottom>
                    Top Locations
                  </Typography>
                  <Box sx={{ overflowY: 'auto', height: '90%' }}>
                    {[
                      { country: 'United States', percentage: 45, flag: '🇺🇸' },
                      { country: 'Canada', percentage: 20, flag: '🇨🇦' },
                      { country: 'United Kingdom', percentage: 15, flag: '🇬🇧' },
                      { country: 'Australia', percentage: 10, flag: '🇦🇺' },
                      { country: 'Germany', percentage: 10, flag: '🇩🇪' },
                    ].map((location) => (
                      <Box
                        key={location.country}
                        display="flex"
                        alignItems="center"
                        justifyContent="space-between"
                        p={1}
                        mb={1}
                      >
                        <Box display="flex" alignItems="center">
                          <Typography sx={{ mr: 1, fontSize: '1.2em' }}>
                            {location.flag}
                          </Typography>
                          <Typography variant="body2">
                            {location.country}
                          </Typography>
                        </Box>
                        <Box display="flex" alignItems="center" gap={1}>
                          <LinearProgress
                            variant="determinate"
                            value={location.percentage}
                            sx={{ width: 60, mr: 1 }}
                          />
                          <Typography variant="caption">
                            {location.percentage}%
                          </Typography>
                        </Box>
                      </Box>
                    ))}
                  </Box>
                </Paper>
              </Grid>
            </Grid>
          </TabPanel>
        </Card>
      </Box>
    </LocalizationProvider>
  );
};

export default Analytics;