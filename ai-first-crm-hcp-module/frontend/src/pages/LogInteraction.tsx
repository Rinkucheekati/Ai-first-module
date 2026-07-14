import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Checkbox,
  FormControlLabel,
  Tabs,
  Tab,
  Card,
  CardContent,
  IconButton,
  Chip,
  Alert,
  Snackbar,
  CircularProgress,
  Divider,
  Grid,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as SmartToyIcon,
  Person as PersonIcon,
  AttachFile as AttachFileIcon,
  Save as SaveIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../store/store';
import { sendMessage, clearResponse, clearError, updateFormData, resetFormData } from '../store/slices/agentSlice';
import { interactionApi } from '../services/interactionApi';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

const LogInteraction: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      text: 'Hello! I\'m your AI assistant for logging interactions. Please provide details about the HCP you interacted with, and I\'ll help you log the interaction efficiently.',
      timestamp: new Date(),
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');

  const dispatch = useDispatch<AppDispatch>();
  const agent = useSelector((state: RootState) => state.agent);

  // Use Redux formData instead of local state
  const formData = agent.formData;

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleFormChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    dispatch(updateFormData({ [e.target.name]: e.target.value }));
  };

  const handleSelectChange = (e: any) => {
    dispatch(updateFormData({ [e.target.name]: e.target.value }));
  };

  const handleCheckboxChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(updateFormData({ followUpRequired: e.target.checked }));
  };

  const handleFormSubmit = async () => {
    try {
      // Find HCP ID from hcpName (simplified - in production, would use HCP API)
      const hcpId = parseInt(formData.hcpId) || 1; // Default to 1 if not selected
      
      const interactionData = {
        hcp_id: hcpId,
        interaction_date: formData.date,
        discussion: formData.notes,
        summary: formData.outcome,
        follow_up_date: formData.followUpRequired ? formData.followUpDate : undefined,
      };
      
      await interactionApi.createInteraction(interactionData);
      
      setSnackbarMessage('Interaction logged successfully!');
      setSnackbarOpen(true);
      
      // Reset form after successful save
      dispatch(resetFormData());
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to log interaction';
      setSnackbarMessage(errorMessage);
      setSnackbarOpen(true);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: inputMessage,
      timestamp: new Date(),
    };

    setMessages([...messages, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage('');
    setIsTyping(true);

    // Send to backend
    await dispatch(sendMessage(messageToSend));
    setIsTyping(false);
  };

  const handleSave = () => {
    if (agent.currentResponse?.interaction_id) {
      setSnackbarMessage('Interaction saved successfully!');
      setSnackbarOpen(true);
    }
  };

  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };

  const handleClearChat = () => {
    dispatch(clearResponse());
    setMessages([
      {
        id: '1',
        sender: 'ai',
        text: 'Hello! I\'m your AI assistant for logging interactions. Please provide details about the HCP you interacted with, and I\'ll help you log the interaction efficiently.',
        timestamp: new Date(),
      },
    ]);
  };

  const handleResetForm = () => {
    dispatch(resetFormData());
  };

  // Update messages when agent response changes
  useEffect(() => {
    if (agent.currentResponse && agent.currentResponse.reply) {
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: agent.currentResponse.reply,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    }
  }, [agent.currentResponse]);

  const hcpOptions = [
    { id: '1', name: 'Dr. Sarah Johnson' },
    { id: '2', name: 'Dr. Michael Chen' },
    { id: '3', name: 'Dr. Emily Davis' },
    { id: '4', name: 'Dr. James Wilson' },
    { id: '5', name: 'Dr. Lisa Anderson' },
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 4 }}>
          Log Interaction
        </Typography>

        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            indicatorColor="primary"
            textColor="primary"
            centered
          >
            <Tab label="Structured Form" />
            <Tab label="Conversational AI Chat" />
          </Tabs>
        </Paper>

        <TabPanel value={tabValue} index={0}>
          <Paper sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <FormControl fullWidth>
                <InputLabel>Select HCP</InputLabel>
                <Select
                  name="hcpId"
                  value={formData.hcpId}
                  onChange={handleSelectChange}
                  label="Select HCP"
                >
                  {hcpOptions.map((hcp) => (
                    <MenuItem key={hcp.id} value={hcp.id}>
                      {hcp.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Interaction Type</InputLabel>
                <Select
                  name="interactionType"
                  value={formData.interactionType}
                  onChange={handleSelectChange}
                  label="Interaction Type"
                >
                  <MenuItem value="call">Phone Call</MenuItem>
                  <MenuItem value="email">Email</MenuItem>
                  <MenuItem value="meeting">In-Person Meeting</MenuItem>
                  <MenuItem value="visit">Site Visit</MenuItem>
                </Select>
              </FormControl>
            </Box>

            <Box sx={{ display: 'flex', gap: 2, mb: 3 }}>
              <TextField
                fullWidth
                label="Date"
                type="date"
                name="date"
                value={formData.date}
                onChange={handleFormChange}
                InputLabelProps={{ shrink: true }}
              />
              <TextField
                fullWidth
                label="Duration (minutes)"
                type="number"
                name="duration"
                value={formData.duration}
                onChange={handleFormChange}
              />
            </Box>

            <TextField
              fullWidth
              label="Notes"
              multiline
              rows={4}
              name="notes"
              value={formData.notes}
              onChange={handleFormChange}
              sx={{ mb: 3 }}
            />

            <TextField
              fullWidth
              label="Outcome"
              multiline
              rows={2}
              name="outcome"
              value={formData.outcome}
              onChange={handleFormChange}
              sx={{ mb: 3 }}
            />

            <Box sx={{ mb: 3 }}>
              <FormControlLabel
                control={
                  <Checkbox
                    checked={formData.followUpRequired}
                    onChange={handleCheckboxChange}
                  />
                }
                label="Follow-up Required"
              />
            </Box>

            {formData.followUpRequired && (
              <TextField
                fullWidth
                label="Follow-up Date"
                type="date"
                name="followUpDate"
                value={formData.followUpDate}
                onChange={handleFormChange}
                InputLabelProps={{ shrink: true }}
                sx={{ mb: 3 }}
              />
            )}

            <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleFormSubmit}
                sx={{ borderRadius: 2 }}
              >
                Log Interaction
              </Button>
              {agent.hasExtractedData && (
                <Button
                  variant="outlined"
                  size="large"
                  onClick={handleResetForm}
                  sx={{ borderRadius: 2 }}
                >
                  Reset Form
                </Button>
              )}
            </Box>
          </Paper>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Paper sx={{ p: 4 }}>
            <Box sx={{ mb: 3 }}>
              <Alert severity="info" icon={<SmartToyIcon />}>
                Chat with AI to log your interaction naturally. The AI will guide you through the process.
              </Alert>
            </Box>

            <Box
              sx={{
                height: 400,
                overflowY: 'auto',
                mb: 2,
                p: 2,
                backgroundColor: '#f5f5f5',
                borderRadius: 2,
              }}
            >
              {messages.map((message) => (
                <Box
                  key={message.id}
                  sx={{
                    display: 'flex',
                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                    mb: 2,
                  }}
                >
                  <Box
                    sx={{
                      maxWidth: '70%',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: 1,
                    }}
                  >
                    {message.sender === 'ai' && (
                      <Box
                        sx={{
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          backgroundColor: '#e3f2fd',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                        }}
                      >
                        <SmartToyIcon sx={{ fontSize: 18, color: '#1976d2' }} />
                      </Box>
                    )}
                    <Box
                      sx={{
                        backgroundColor: message.sender === 'user' ? '#1976d2' : 'white',
                        color: message.sender === 'user' ? 'white' : 'text.primary',
                        p: 2,
                        borderRadius: 2,
                        boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                      }}
                    >
                      <Typography variant="body2">{message.text}</Typography>
                    </Box>
                    {message.sender === 'user' && (
                      <Box
                        sx={{
                          width: 32,
                          height: 32,
                          borderRadius: '50%',
                          backgroundColor: '#e8f5e9',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          flexShrink: 0,
                        }}
                      >
                        <PersonIcon sx={{ fontSize: 18, color: '#2e7d32' }} />
                      </Box>
                    )}
                  </Box>
                </Box>
              ))}
              {isTyping && (
                <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box
                      sx={{
                        width: 32,
                        height: 32,
                        borderRadius: '50%',
                        backgroundColor: '#e3f2fd',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                      }}
                    >
                      <SmartToyIcon sx={{ fontSize: 18, color: '#1976d2' }} />
                    </Box>
                    <Box
                      sx={{
                        backgroundColor: 'white',
                        p: 2,
                        borderRadius: 2,
                        boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                      }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        AI is typing...
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              )}
            </Box>

            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 2 }}>
              <IconButton>
                <AttachFileIcon />
              </IconButton>
              <TextField
                fullWidth
                placeholder="Type your message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    handleSendMessage();
                  }
                }}
                disabled={agent.isLoading}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                  },
                }}
              />
              <Button
                variant="contained"
                onClick={handleSendMessage}
                disabled={agent.isLoading || !inputMessage.trim()}
                sx={{ borderRadius: 2, minWidth: 'auto' }}
              >
                {agent.isLoading ? <CircularProgress size={24} /> : <SendIcon />}
              </Button>
            </Box>

            {agent.error && (
              <Alert severity="error" sx={{ mb: 2 }} onClose={() => dispatch(clearError())}>
                {agent.error}
              </Alert>
            )}

            {agent.structuredData && (
              <Paper sx={{ p: 3, mt: 3, backgroundColor: '#f5f5f5' }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Extracted Information
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Button
                      variant="outlined"
                      size="small"
                      onClick={handleClearChat}
                    >
                      Clear
                    </Button>
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<SaveIcon />}
                      onClick={handleSave}
                      disabled={agent.isSaved}
                      color={agent.isSaved ? 'success' : 'primary'}
                    >
                      {agent.isSaved ? 'Saved' : 'Save'}
                    </Button>
                  </Box>
                </Box>
                <Divider sx={{ mb: 2 }} />
                <Grid container spacing={2}>
                  {agent.structuredData.doctor_name && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Doctor Name
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {agent.structuredData.doctor_name}
                      </Typography>
                    </Grid>
                  )}
                  {agent.structuredData.hospital && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Hospital
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {agent.structuredData.hospital}
                      </Typography>
                    </Grid>
                  )}
                  {agent.structuredData.interaction_date && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Interaction Date
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {agent.structuredData.interaction_date}
                      </Typography>
                    </Grid>
                  )}
                  {agent.structuredData.follow_up_date && (
                    <Grid item xs={12} sm={6}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Follow-up Date
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {agent.structuredData.follow_up_date}
                      </Typography>
                    </Grid>
                  )}
                  {agent.structuredData.summary && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Summary
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {agent.structuredData.summary}
                      </Typography>
                    </Grid>
                  )}
                  {agent.structuredData.products_discussed && agent.structuredData.products_discussed.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Products Discussed
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                        {agent.structuredData.products_discussed.map((product, index) => (
                          <Chip key={index} label={product} size="small" />
                        ))}
                      </Box>
                    </Grid>
                  )}
                  {agent.structuredData.doctor_feedback && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Doctor Feedback
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {agent.structuredData.doctor_feedback}
                      </Typography>
                    </Grid>
                  )}
                  {agent.structuredData.meeting_outcome && (
                    <Grid item xs={12}>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        Meeting Outcome
                      </Typography>
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {agent.structuredData.meeting_outcome}
                      </Typography>
                    </Grid>
                  )}
                </Grid>
                {agent.currentResponse?.interaction_id && (
                  <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid #e0e0e0' }}>
                    <Typography variant="body2" color="success.main" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <CheckCircleIcon fontSize="small" />
                      Interaction ID: {agent.currentResponse.interaction_id}
                    </Typography>
                  </Box>
                )}
              </Paper>
            )}

            <Box sx={{ mt: 3, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              <Chip label="HCP: Dr. Sarah Johnson" clickable />
              <Chip label="Type: Phone Call" clickable />
              <Chip label="Duration: 15 minutes" clickable />
              <Chip label="+ Add Tag" variant="outlined" clickable />
            </Box>
          </Paper>
        </TabPanel>
      </Container>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={handleSnackbarClose} severity="success" sx={{ width: '100%' }}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default LogInteraction;
