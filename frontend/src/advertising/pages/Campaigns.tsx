import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  Avatar,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  OutlinedInput,
  Checkbox,
  ListItemText,
  Paper,
  Toolbar,
  LinearProgress,
  Menu,
  Alert,
  Grid,
  Fab,
  Tooltip,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  PlayArrow,
  Pause,
  ContentCopy,
  Analytics,
  FilterList,
  Search,
  MoreVert,
  Visibility,
  Download,
  Campaign,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store/store';
import { campaignsActions } from '../store/store';
import { apiClient } from '../services/api';
import { Campaign as CampaignType, CampaignFilters } from '../types';

const PLATFORMS = ['youtube', 'tiktok', 'instagram', 'facebook', 'twitter'];
const STATUSES = ['draft', 'active', 'paused', 'completed', 'cancelled'];

interface CampaignRowProps {
  campaign: CampaignType;
  onEdit: (campaign: CampaignType) => void;
  onDelete: (campaignId: string) => void;
  onToggleStatus: (campaign: CampaignType) => void;
  onDuplicate: (campaign: CampaignType) => void;
  onViewAnalytics: (campaignId: string) => void;
}

const CampaignRow: React.FC<CampaignRowProps> = ({
  campaign,
  onEdit,
  onDelete,
  onToggleStatus,
  onDuplicate,
  onViewAnalytics,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const getStatusColor = (status: CampaignType['status']) => {
    switch (status) {
      case 'active': return 'success';
      case 'paused': return 'warning';
      case 'completed': return 'info';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <>
      <TableRow hover>
        <TableCell>
          <Box display="flex" alignItems="center">
            <Avatar sx={{ mr: 2, bgcolor: 'primary.main' }}>
              <Campaign />
            </Avatar>
            <Box>
              <Typography variant="subtitle2" fontWeight="bold">
                {campaign.name}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Created {new Date(campaign.createdAt).toLocaleDateString()}
              </Typography>
            </Box>
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
        <TableCell>
          <Box display="flex" flexWrap="wrap" gap={0.5}>
            {campaign.platforms.slice(0, 3).map((platform) => (
              <Chip key={platform} label={platform} size="small" variant="outlined" />
            ))}
            {campaign.platforms.length > 3 && (
              <Chip label={`+${campaign.platforms.length - 3}`} size="small" variant="outlined" />
            )}
          </Box>
        </TableCell>
        <TableCell align="right">
          {formatCurrency(campaign.budget)}
        </TableCell>
        <TableCell align="right">
          <Box>
            {formatCurrency(campaign.spent)}
            <LinearProgress
              variant="determinate"
              value={(campaign.spent / campaign.budget) * 100}
              sx={{ mt: 1, width: 80 }}
            />
          </Box>
        </TableCell>
        <TableCell align="right">
          {campaign.performance.impressions.toLocaleString()}
        </TableCell>
        <TableCell align="right">
          {campaign.performance.ctr.toFixed(2)}%
        </TableCell>
        <TableCell align="right">
          <Box display="flex" alignItems="center" justifyContent="flex-end">
            <IconButton
              size="small"
              onClick={() => onToggleStatus(campaign)}
              color={campaign.status === 'active' ? 'warning' : 'success'}
              disabled={campaign.status === 'completed' || campaign.status === 'cancelled'}
            >
              {campaign.status === 'active' ? <Pause /> : <PlayArrow />}
            </IconButton>
            <IconButton
              size="small"
              onClick={handleMenuOpen}
            >
              <MoreVert />
            </IconButton>
          </Box>
        </TableCell>
      </TableRow>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={() => { onViewAnalytics(campaign.id); handleMenuClose(); }}>
          <Analytics sx={{ mr: 1 }} /> Analytics
        </MenuItem>
        <MenuItem onClick={() => { onEdit(campaign); handleMenuClose(); }}>
          <Edit sx={{ mr: 1 }} /> Edit
        </MenuItem>
        <MenuItem onClick={() => { onDuplicate(campaign); handleMenuClose(); }}>
          <ContentCopy sx={{ mr: 1 }} /> Duplicate
        </MenuItem>
        <MenuItem 
          onClick={() => { onDelete(campaign.id); handleMenuClose(); }}
          sx={{ color: 'error.main' }}
        >
          <Delete sx={{ mr: 1 }} /> Delete
        </MenuItem>
      </Menu>
    </>
  );
};

const Campaigns: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  
  const {
    campaigns,
    totalCount,
    currentPage,
    pageSize,
    loading,
    error,
    filters
  } = useAppSelector(state => state.campaigns);

  const [searchQuery, setSearchQuery] = useState('');
  const [filterDialogOpen, setFilterDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedCampaignId, setSelectedCampaignId] = useState<string | null>(null);
  
  // Filter states
  const [statusFilter, setStatusFilter] = useState<string[]>(filters.status || []);
  const [platformFilter, setPlatformFilter] = useState<string[]>(filters.platforms || []);
  const [dateRangeFilter, setDateRangeFilter] = useState({
    start: filters.dateRange?.start || '',
    end: filters.dateRange?.end || ''
  });

  useEffect(() => {
    loadCampaigns();
  }, [currentPage, pageSize, filters]);

  const loadCampaigns = async () => {
    try {
      dispatch(campaignsActions.setLoading({ isLoading: true, message: 'Loading campaigns...' }));
      
      const response = await apiClient.getCampaigns(
        currentPage,
        pageSize,
        {
          status: filters.status,
          platforms: filters.platforms,
          dateRange: filters.dateRange,
        }
      );

      dispatch(campaignsActions.setCampaigns({
        campaigns: response.data,
        totalCount: response.pagination.total
      }));

    } catch (error: any) {
      console.error('Failed to load campaigns:', error);
      dispatch(campaignsActions.setError({
        hasError: true,
        message: error.message || 'Failed to load campaigns'
      }));
    }
  };

  const handlePageChange = (event: unknown, newPage: number) => {
    dispatch(campaignsActions.setPage(newPage + 1));
  };

  const handleRowsPerPageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(campaignsActions.setPageSize(parseInt(event.target.value, 10)));
    dispatch(campaignsActions.setPage(1));
  };

  const handleSearch = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(event.target.value);
    // Implement search functionality
  };

  const handleApplyFilters = () => {
    const newFilters: CampaignFilters = {
      status: statusFilter.length > 0 ? statusFilter as CampaignType['status'][] : undefined,
      platforms: platformFilter.length > 0 ? platformFilter as CampaignType['platforms'] : undefined,
      dateRange: dateRangeFilter.start && dateRangeFilter.end ? dateRangeFilter : undefined,
    };

    dispatch(campaignsActions.setFilters(newFilters));
    setFilterDialogOpen(false);
  };

  const handleClearFilters = () => {
    setStatusFilter([]);
    setPlatformFilter([]);
    setDateRangeFilter({ start: '', end: '' });
    dispatch(campaignsActions.setFilters({}));
    setFilterDialogOpen(false);
  };

  const handleToggleStatus = async (campaign: CampaignType) => {
    try {
      if (campaign.status === 'active') {
        const response = await apiClient.pauseCampaign(campaign.id);
        dispatch(campaignsActions.updateCampaign(response.data));
      } else if (campaign.status === 'paused') {
        const response = await apiClient.resumeCampaign(campaign.id);
        dispatch(campaignsActions.updateCampaign(response.data));
      }
    } catch (error: any) {
      console.error('Failed to toggle campaign status:', error);
    }
  };

  const handleDuplicate = async (campaign: CampaignType) => {
    try {
      const response = await apiClient.duplicateCampaign(campaign.id);
      dispatch(campaignsActions.addCampaign(response.data));
    } catch (error: any) {
      console.error('Failed to duplicate campaign:', error);
    }
  };

  const handleDelete = async () => {
    if (!selectedCampaignId) return;

    try {
      await apiClient.deleteCampaign(selectedCampaignId);
      dispatch(campaignsActions.removeCampaign(selectedCampaignId));
      setDeleteDialogOpen(false);
      setSelectedCampaignId(null);
    } catch (error: any) {
      console.error('Failed to delete campaign:', error);
    }
  };

  const openDeleteDialog = (campaignId: string) => {
    setSelectedCampaignId(campaignId);
    setDeleteDialogOpen(true);
  };

  const filteredCampaigns = campaigns.filter(campaign =>
    campaign.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    campaign.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getActiveFiltersCount = () => {
    let count = 0;
    if (statusFilter.length > 0) count++;
    if (platformFilter.length > 0) count++;
    if (dateRangeFilter.start && dateRangeFilter.end) count++;
    return count;
  };

  return (
    <Box>
      {/* Header */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Campaigns
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => navigate('/create-campaign')}
          size="large"
        >
          Create Campaign
        </Button>
      </Box>

      {error.hasError && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }} 
          onClose={() => dispatch(campaignsActions.clearError())}
        >
          {error.message}
        </Alert>
      )}

      {/* Toolbar */}
      <Card sx={{ mb: 2 }}>
        <Toolbar>
          <TextField
            placeholder="Search campaigns..."
            variant="outlined"
            size="small"
            value={searchQuery}
            onChange={handleSearch}
            InputProps={{
              startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
            sx={{ mr: 2, minWidth: 300 }}
          />
          
          <Button
            variant="outlined"
            startIcon={<FilterList />}
            onClick={() => setFilterDialogOpen(true)}
            sx={{ mr: 2 }}
          >
            Filters {getActiveFiltersCount() > 0 && `(${getActiveFiltersCount()})`}
          </Button>

          <Box flexGrow={1} />

          <Button
            variant="outlined"
            startIcon={<Download />}
            sx={{ mr: 1 }}
          >
            Export
          </Button>

          <Button
            variant="outlined"
            startIcon={<Analytics />}
            onClick={() => navigate('/analytics')}
          >
            View Analytics
          </Button>
        </Toolbar>
      </Card>

      {/* Campaigns Table */}
      <Card>
        {loading.isLoading && <LinearProgress />}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Campaign</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Platforms</TableCell>
                <TableCell align="right">Budget</TableCell>
                <TableCell align="right">Spent</TableCell>
                <TableCell align="right">Impressions</TableCell>
                <TableCell align="right">CTR</TableCell>
                <TableCell align="right">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredCampaigns.map((campaign) => (
                <CampaignRow
                  key={campaign.id}
                  campaign={campaign}
                  onEdit={(campaign) => navigate(`/campaigns/${campaign.id}/edit`)}
                  onDelete={openDeleteDialog}
                  onToggleStatus={handleToggleStatus}
                  onDuplicate={handleDuplicate}
                  onViewAnalytics={(id) => navigate(`/campaigns/${id}/analytics`)}
                />
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={totalCount}
          rowsPerPage={pageSize}
          page={currentPage - 1}
          onPageChange={handlePageChange}
          onRowsPerPageChange={handleRowsPerPageChange}
        />
      </Card>

      {/* Filter Dialog */}
      <Dialog
        open={filterDialogOpen}
        onClose={() => setFilterDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Filter Campaigns</DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  multiple
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value as string[])}
                  input={<OutlinedInput label="Status" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                >
                  {STATUSES.map((status) => (
                    <MenuItem key={status} value={status}>
                      <Checkbox checked={statusFilter.indexOf(status) > -1} />
                      <ListItemText primary={status} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Platforms</InputLabel>
                <Select
                  multiple
                  value={platformFilter}
                  onChange={(e) => setPlatformFilter(e.target.value as string[])}
                  input={<OutlinedInput label="Platforms" />}
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {selected.map((value) => (
                        <Chip key={value} label={value} size="small" />
                      ))}
                    </Box>
                  )}
                >
                  {PLATFORMS.map((platform) => (
                    <MenuItem key={platform} value={platform}>
                      <Checkbox checked={platformFilter.indexOf(platform) > -1} />
                      <ListItemText primary={platform} />
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Start Date"
                type="date"
                value={dateRangeFilter.start}
                onChange={(e) => setDateRangeFilter(prev => ({ ...prev, start: e.target.value }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="End Date"
                type="date"
                value={dateRangeFilter.end}
                onChange={(e) => setDateRangeFilter(prev => ({ ...prev, end: e.target.value }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClearFilters}>Clear All</Button>
          <Button onClick={() => setFilterDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleApplyFilters} variant="contained">
            Apply Filters
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
      >
        <DialogTitle>Delete Campaign</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to delete this campaign? This action cannot be undone.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleDelete} color="error" variant="contained">
            Delete
          </Button>
        </DialogActions>
      </Dialog>

      {/* Floating Action Button */}
      <Fab
        color="primary"
        aria-label="create campaign"
        sx={{
          position: 'fixed',
          bottom: 16,
          right: 16,
        }}
        onClick={() => navigate('/create-campaign')}
      >
        <Add />
      </Fab>
    </Box>
  );
};

export default Campaigns;