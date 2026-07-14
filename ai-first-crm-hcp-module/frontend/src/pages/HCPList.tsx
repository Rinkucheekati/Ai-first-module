import React, { useState } from 'react';
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
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Search as SearchIcon,
  Add as AddIcon,
  Visibility as VisibilityIcon,
  Edit as EditIcon,
} from '@mui/icons-material';

interface HCP {
  id: string;
  name: string;
  specialty: string;
  organization: string;
  email: string;
  phone: string;
  city: string;
  status: 'active' | 'inactive';
  lastInteraction: string;
  totalInteractions: number;
}

const HCPList: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedHCP, setSelectedHCP] = useState<HCP | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const mockHCPs: HCP[] = [
    {
      id: '1',
      name: 'Dr. Sarah Johnson',
      specialty: 'Cardiology',
      organization: 'City Hospital',
      email: 'sarah.johnson@cityhospital.com',
      phone: '+1 555-0101',
      city: 'New York',
      status: 'active',
      lastInteraction: '2024-01-15',
      totalInteractions: 12,
    },
    {
      id: '2',
      name: 'Dr. Michael Chen',
      specialty: 'Neurology',
      organization: 'Medical Center',
      email: 'michael.chen@medicalcenter.com',
      phone: '+1 555-0102',
      city: 'Los Angeles',
      status: 'active',
      lastInteraction: '2024-01-10',
      totalInteractions: 8,
    },
    {
      id: '3',
      name: 'Dr. Emily Davis',
      specialty: 'Oncology',
      organization: 'Cancer Institute',
      email: 'emily.davis@cancerinstitute.com',
      phone: '+1 555-0103',
      city: 'Chicago',
      status: 'inactive',
      lastInteraction: '2023-12-20',
      totalInteractions: 5,
    },
    {
      id: '4',
      name: 'Dr. James Wilson',
      specialty: 'Pediatrics',
      organization: 'Children Hospital',
      email: 'james.wilson@childrenhospital.com',
      phone: '+1 555-0104',
      city: 'Houston',
      status: 'active',
      lastInteraction: '2024-01-12',
      totalInteractions: 15,
    },
    {
      id: '5',
      name: 'Dr. Lisa Anderson',
      specialty: 'Dermatology',
      organization: 'Skin Care Clinic',
      email: 'lisa.anderson@skincareclinic.com',
      phone: '+1 555-0105',
      city: 'Phoenix',
      status: 'active',
      lastInteraction: '2024-01-08',
      totalInteractions: 7,
    },
  ];

  const filteredHCPs = mockHCPs.filter(
    (hcp) =>
      hcp.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      hcp.specialty.toLowerCase().includes(searchTerm.toLowerCase()) ||
      hcp.organization.toLowerCase().includes(searchTerm.toLowerCase()) ||
      hcp.city.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
              placeholder="Search HCPs by name, specialty, organization, or city..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
              sx={{ maxWidth: 600 }}
            />
          </Box>
        </Paper>

        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Specialty</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Organization</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>City</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Last Interaction</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Total Interactions</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredHCPs.map((hcp) => (
                <TableRow key={hcp.id} hover>
                  <TableCell sx={{ fontWeight: 500 }}>{hcp.name}</TableCell>
                  <TableCell>{hcp.specialty}</TableCell>
                  <TableCell>{hcp.organization}</TableCell>
                  <TableCell>{hcp.city}</TableCell>
                  <TableCell>
                    <Chip
                      label={hcp.status}
                      color={hcp.status === 'active' ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{hcp.lastInteraction}</TableCell>
                  <TableCell>{hcp.totalInteractions}</TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleView(hcp)}>
                      <VisibilityIcon />
                    </IconButton>
                    <IconButton size="small">
                      <EditIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
          <DialogTitle>HCP Details</DialogTitle>
          <DialogContent>
            {selectedHCP && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="h6" gutterBottom>
                  {selectedHCP.name}
                </Typography>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Specialty
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedHCP.specialty}
                  </Typography>
                </Box>
                <Box sx={{ mt: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    Organization
                  </Typography>
                  <Typography variant="body1" gutterBottom>
                    {selectedHCP.organization}
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
                    Status
                  </Typography>
                  <Chip
                    label={selectedHCP.status}
                    color={selectedHCP.status === 'active' ? 'success' : 'default'}
                    size="small"
                  />
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
