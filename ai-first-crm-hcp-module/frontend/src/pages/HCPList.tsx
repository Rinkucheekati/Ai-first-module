import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Fade,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
} from '@mui/icons-material';
import { useNotification } from '../components/common/NotificationProvider';
import { hcpApi, HCP } from '../services/hcpApi';
import LoadingSpinner from '../components/common/LoadingSpinner';

const HCPList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedHCP, setSelectedHCP] = useState<HCP | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [hcpList, setHcpList] = useState<HCP[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const notification = useNotification();

  // Fetch HCPs on component mount
  useEffect(() => {
    fetchHCPs();
  }, []);

  const fetchHCPs = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await hcpApi.getHCPs(0, 100, searchTerm || undefined);
      setHcpList(data.hcps || []);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load HCPs';
      setError(errorMessage);
      notification.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Refetch when search term changes
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchTerm.length === 0 || searchTerm.length >= 2) {
        fetchHCPs();
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  const handleView = (hcp: HCP) => {
    setSelectedHCP(hcp);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedHCP(null);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
            HCP List
          </Typography>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            sx={{ borderRadius: 2 }}
          >
            Add HCP
          </Button>
        </Box>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              fullWidth
              placeholder="Search HCPs by name, specialization, hospital, or city..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
              sx={{ maxWidth: 600 }}
            />
          </Box>
        </Paper>

        {error && (
          <Fade in={true} timeout={400}>
            <Alert severity="error" sx={{ mb: 3 }}>
              {error}
            </Alert>
          </Fade>
        )}

        {loading ? (
          <LoadingSpinner message="Loading HCPs..." />
        ) : (
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Specialization</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Hospital</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>City</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Email</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Phone</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {hcpList.length > 0 ? (
                  hcpList.map((hcp) => (
                    <Fade in={true} timeout={400} key={hcp.id}>
                      <TableRow hover sx={{ '&:hover': { backgroundColor: '#f5f5f5' } }}>
                        <TableCell sx={{ fontWeight: 500 }}>{hcp.doctor_name}</TableCell>
                        <TableCell>{hcp.specialization}</TableCell>
                        <TableCell>{hcp.hospital}</TableCell>
                        <TableCell>{hcp.city}</TableCell>
                        <TableCell>{hcp.email}</TableCell>
                        <TableCell>{hcp.phone}</TableCell>
                        <TableCell>
                          <IconButton size="small" onClick={() => handleView(hcp)}>
                            <VisibilityIcon />
                          </IconButton>
                          <IconButton size="small">
                            <EditIcon />
                          </IconButton>
                        </TableCell>
                      </TableRow>
                    </Fade>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">No HCPs found</Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>HCP Details</DialogTitle>
          <DialogContent>
            {selectedHCP && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {selectedHCP.doctor_name}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Specialization
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedHCP.specialization}
                  </Typography>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Hospital
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedHCP.hospital}
                  </Typography>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Email
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedHCP.email}
                  </Typography>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Phone
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedHCP.phone}
                  </Typography>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    City
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedHCP.city}
                  </Typography>
                </Box>
              </Box>
            )}
          </DialogContent>
          <DialogActions>
            <Button onClick={handleCloseDialog}>Close</Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
};

export default HCPList;
