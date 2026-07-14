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
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility as VisibilityIcon,
  FilterList as FilterListIcon,
  SmartToy as SmartToyIcon,
} from '@mui/icons-material';

interface Interaction {
  id: string;
  hcpName: string;
  hcpSpecialty: string;
  type: 'call' | 'email' | 'meeting' | 'visit';
  date: string;
  duration: number;
  notes: string;
  outcome: string;
  followUpRequired: boolean;
  followUpDate: string | null;
  aiSummary: string;
  aiInsights: string[];
}

const InteractionHistory: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedInteraction, setSelectedInteraction] = useState<Interaction | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const mockInteractions: Interaction[] = [
    {
      id: '1',
      hcpName: 'Dr. Sarah Johnson',
      hcpSpecialty: 'Cardiology',
      type: 'call',
      date: '2024-01-15',
      duration: 15,
      notes: 'Discussed new product features and upcoming conference presentation.',
      outcome: 'Interested in demo',
      followUpRequired: true,
      followUpDate: '2024-01-22',
      aiSummary: 'Productive call with Dr. Johnson. She expressed strong interest in the new features and requested a demo. Follow-up scheduled for next week.',
      aiInsights: [
        'High engagement level detected',
        'Key decision maker identified',
        'Timing favorable for next steps',
      ],
    },
    {
      id: '2',
      hcpName: 'Dr. Michael Chen',
      hcpSpecialty: 'Neurology',
      type: 'meeting',
      date: '2024-01-12',
      duration: 45,
      notes: 'In-person meeting at Medical Center. Presented clinical data and case studies.',
      outcome: 'Positive response',
      followUpRequired: false,
      followUpDate: null,
      aiSummary: 'Successful in-person meeting with Dr. Chen. Clinical presentation was well-received. No immediate follow-up required.',
      aiInsights: [
        'Clinical data resonated well',
        'Peer influence opportunity identified',
        'Consider for case study program',
      ],
    },
    {
      id: '3',
      hcpName: 'Dr. Emily Davis',
      hcpSpecialty: 'Oncology',
      type: 'email',
      date: '2024-01-10',
      duration: 0,
      notes: 'Sent product information and research papers.',
      outcome: 'Awaiting response',
      followUpRequired: true,
      followUpDate: '2024-01-17',
      aiSummary: 'Initial outreach via email with supporting materials. Awaiting response from Dr. Davis.',
      aiInsights: [
        'Research materials appropriate for specialty',
        'Follow-up timing optimal',
        'Consider phone follow-up if no response',
      ],
    },
    {
      id: '4',
      hcpName: 'Dr. James Wilson',
      hcpSpecialty: 'Pediatrics',
      type: 'visit',
      date: '2024-01-08',
      duration: 60,
      notes: 'Site visit to Children Hospital. Met with department head and team.',
      outcome: 'Partnership discussion',
      followUpRequired: true,
      followUpDate: '2024-01-15',
      aiSummary: 'Comprehensive site visit with Dr. Wilson and team. Partnership opportunities identified. Follow-up meeting scheduled.',
      aiInsights: [
        'Strong team alignment',
        'Partnership potential high',
        'Multiple stakeholders engaged',
      ],
    },
    {
      id: '5',
      hcpName: 'Dr. Lisa Anderson',
      hcpSpecialty: 'Dermatology',
      type: 'call',
      date: '2024-01-05',
      duration: 20,
      notes: 'Follow-up call regarding previous meeting.',
      outcome: 'Confirmed interest',
      followUpRequired: false,
      followUpDate: null,
      aiSummary: 'Follow-up call confirmed Dr. Anderson\'s continued interest. No additional follow-up needed at this time.',
      aiInsights: [
        'Interest maintained over time',
        'Relationship strengthening',
        'Ready for next phase engagement',
      ],
    },
  ];

  const filteredInteractions = mockInteractions.filter(
    (interaction) =>
      interaction.hcpName.toLowerCase().includes(searchTerm.toLowerCase()) ||
      interaction.hcpSpecialty.toLowerCase().includes(searchTerm.toLowerCase()) ||
      interaction.type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      interaction.outcome.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'call':
        return 'primary';
      case 'email':
        return 'info';
      case 'meeting':
        return 'success';
      case 'visit':
        return 'warning';
      default:
        return 'default';
    }
  };

  const handleView = (interaction: Interaction) => {
    setSelectedInteraction(interaction);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedInteraction(null);
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
          <Typography variant="h4" sx={{ fontWeight: 600 }}>
            Interaction History
          </Typography>
          <Button
            variant="outlined"
            startIcon={<FilterListIcon />}
            sx={{ borderRadius: 2 }}
          >
            Filter
          </Button>
        </Box>

        <Paper sx={{ p: 3, mb: 3 }}>
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <TextField
              fullWidth
              placeholder="Search interactions by HCP name, specialty, type, or outcome..."
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
                <TableCell sx={{ fontWeight: 600 }}>HCP Name</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Specialty</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Date</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Duration</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Outcome</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Follow-up</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredInteractions.map((interaction) => (
                <TableRow key={interaction.id} hover>
                  <TableCell sx={{ fontWeight: 500 }}>{interaction.hcpName}</TableCell>
                  <TableCell>{interaction.hcpSpecialty}</TableCell>
                  <TableCell>
                    <Chip
                      label={interaction.type.charAt(0).toUpperCase() + interaction.type.slice(1)}
                      color={getTypeColor(interaction.type) as any}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>{interaction.date}</TableCell>
                  <TableCell>{interaction.duration > 0 ? `${interaction.duration} min` : '-'}</TableCell>
                  <TableCell>{interaction.outcome}</TableCell>
                  <TableCell>
                    {interaction.followUpRequired ? (
                      <Chip
                        label={interaction.followUpDate}
                        color="warning"
                        size="small"
                      />
                    ) : (
                      <Chip label="None" size="small" />
                    )}
                  </TableCell>
                  <TableCell>
                    <IconButton size="small" onClick={() => handleView(interaction)}>
                      <VisibilityIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
          <DialogTitle>Interaction Details</DialogTitle>
          <DialogContent>
            {selectedInteraction && (
              <Box sx={{ mt: 2 }}>
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      HCP Name
                    </Typography>
                    <Typography variant="body1" gutterBottom sx={{ fontWeight: 500 }}>
                      {selectedInteraction.hcpName}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Specialty
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {selectedInteraction.hcpSpecialty}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Type
                    </Typography>
                    <Chip
                      label={selectedInteraction.type.charAt(0).toUpperCase() + selectedInteraction.type.slice(1)}
                      color={getTypeColor(selectedInteraction.type) as any}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="body2" color="text.secondary">
                      Date
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {selectedInteraction.date}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Notes
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {selectedInteraction.notes}
                    </Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Outcome
                    </Typography>
                    <Typography variant="body1" gutterBottom>
                      {selectedInteraction.outcome}
                    </Typography>
                  </Grid>
                </Grid>

                <Card sx={{ mt: 3, backgroundColor: '#e3f2fd' }}>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                      <SmartToyIcon sx={{ color: '#1976d2' }} />
                      <Typography variant="h6" sx={{ fontWeight: 600 }}>
                        AI Summary
                      </Typography>
                    </Box>
                    <Typography variant="body1" gutterBottom>
                      {selectedInteraction.aiSummary}
                    </Typography>
                  </CardContent>
                </Card>

                <Card sx={{ mt: 2, backgroundColor: '#f5f5f5' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                      AI Insights
                    </Typography>
                    {selectedInteraction.aiInsights.map((insight, index) => (
                      <Box key={index} sx={{ display: 'flex', alignItems: 'flex-start', gap: 1, mb: 1 }}>
                        <Typography variant="body2" sx={{ color: '#1976d2' }}>
                          •
                        </Typography>
                        <Typography variant="body2">{insight}</Typography>
                      </Box>
                    ))}
                  </CardContent>
                </Card>
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

export default InteractionHistory;
