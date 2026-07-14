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
  Backdrop,
  Fade,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as SmartToyIcon,
  Person as PersonIcon,
  AttachFile as AttachFileIcon,
  Save as SaveIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { RootState, AppDispatch } from '../store/store';
import { sendMessage, clearResponse, clearError, updateFormData, resetFormData } from '../store/slices/agentSlice';
import { interactionApi } from '../services/interactionApi';
import TypingAnimation from '../components/common/TypingAnimation';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { useNotification } from '../components/common/NotificationProvider';

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
  const [isFormSubmitting, setIsFormSubmitting] = useState(false);

  const dispatch = useDispatch<AppDispatch>();
  const agent = useSelector((state: RootState) => state.agent);
  const notification = useNotification();

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
    if (!formData.hcpId || !formData.date || !formData.notes) {
      notification.warning('Please fill in required fields (HCP, Date, Notes)');
      return;
    }

    setIsFormSubmitting(true);
    try {
      const hcpId = parseInt(formData.hcpId) || 1;
      
      const interactionData = {
        hcp_id: hcpId,
        interaction_date: formData.date,
        discussion: formData.notes,
        summary: formData.outcome,
        follow_up_date: formData.followUpRequired ? formData.followUpDate : undefined,
      };
      
      await interactionApi.createInteraction(interactionData);
      
      notification.success('Interaction logged successfully!', 5000);
      dispatch(resetFormData());
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to log interaction';
      notification.error(errorMessage, 6000);
    } finally {
      setIsFormSubmitting(false);
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
      notification.success('Interaction saved successfully!', 5000);
    } else {
      notification.warning('No data to save yet');
    }
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

            <Box sx={{ display: 'flex', gap: 2, mt: 3, position: 'relative' }}>
              <Button
                variant="contained"
                size="large"
                onClick={handleFormSubmit}
                disabled={isFormSubmitting}
                sx={{
                  borderRadius: 2,
                  transition: 'all 0.3s ease-in-out',
                  opacity: isFormSubmitting ? 0.7 : 1,
                  minWidth: 150,
                }}
              >
                {isFormSubmitting ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CircularProgress size={20} sx={{ color: 'inherit' }} />
                    Saving...
                  </Box>
                ) : (
                  'Log Interaction'
                )}
              </Button>
              {agent.hasExtractedData && (
                <Button
                  variant="outlined"
                  size="large"
                  onClick={handleResetForm}
                  disabled={isFormSubmitting}
                  sx={{
                    borderRadius: 2,
                    transition: 'all 0.3s ease-in-out',
                  }}
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
                transition: 'all 0.3s ease-in-out',
                '&::-webkit-scrollbar': {
                  width: '8px',
                },
                '&::-webkit-scrollbar-track': {
                  background: '#f1f1f1',
                  borderRadius: '4px',
                },
                '&::-webkit-scrollbar-thumb': {
                  background: '#888',
                  borderRadius: '4px',
                  '&:hover': {
                    background: '#555',
                  },
                },
              }}
            >
              {messages.map((message) => (
                <Fade in={true} timeout={400} key={message.id}>
                  <Box
                    sx={{
                      display: 'flex',
                      justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                      mb: 2,
                      animation: 'slideInMessage 0.3s ease-out',
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
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                          transition: 'all 0.3s ease-in-out',
                          '&:hover': {
                            boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
                          },
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
                </Fade>
              ))}
              {agent.isLoading && (
                <Fade in={true} timeout={400}>
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
                          boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                          minWidth: 100,
                          display: 'flex',
                          alignItems: 'center',
                        }}
                      >
                        <TypingAnimation variant="dots" size="small" />
                      </Box>
                    </Box>
                  </Box>
                </Fade>
              )}
            </Box>

            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center', mb: 2 }}>
              <IconButton disabled={agent.isLoading}>
                <AttachFileIcon />
              </IconButton>
              <TextField
                fullWidth
                placeholder="Type your message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !agent.isLoading && inputMessage.trim()) {
                    handleSendMessage();
                  }
                }}
                disabled={agent.isLoading}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: 2,
                    transition: 'all 0.2s ease-in-out',
                    '&.Mui-disabled': {
                      opacity: 0.6,
                    },
                  },
                }}
              />
              <Button
                variant="contained"
                onClick={handleSendMessage}
                disabled={agent.isLoading || !inputMessage.trim()}
                sx={{
                  borderRadius: 2,
                  minWidth: 'auto',
                  transition: 'all 0.3s ease-in-out',
                  '&:disabled': {
                    opacity: 0.5,
                  },
                }}
              >
                {agent.isLoading ? (
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <CircularProgress size={20} sx={{ color: 'inherit' }} />
                  </Box>
                ) : (
                  <SendIcon />
                )}
              </Button>
            </Box>

            {agent.error && (
              <Fade in={true} timeout={400}>
                <Alert
                  severity="error"
                  sx={{
                    mb: 2,
                    animation: 'slideInMessage 0.3s ease-out',
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                  }}
                  onClose={() => dispatch(clearError())}
                  icon={<ErrorIcon />}
                >
                  {agent.error}
                </Alert>
              </Fade>
            )}

            {agent.structuredData && (
              <Fade in={true} timeout={500}>
                <Paper
                  sx={{
                    p: 3,
                    mt: 3,
                    backgroundColor: '#f5f5f5',
                    transition: 'all 0.3s ease-in-out',
                    animation: 'slideInMessage 0.4s ease-out',
                  }}
                >
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
                    <Typography
                      variant="body2"
                      color="success.main"
                      sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5,
                        animation: 'slideIn 0.3s ease-out',
                      }}
                    >
                      <CheckCircleIcon fontSize="small" />
                      Interaction ID: {agent.currentResponse.interaction_id}
                    </Typography>
                  </Box>
                )}
              </Paper>
            </Fade>
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

      <Backdrop
        sx={{
          color: '#fff',
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: 'rgba(0, 0, 0, 0.1)',
        }}
        open={agent.isLoading && tabValue === 0}
      >
        <LoadingSpinner message="Processing your interaction..." size="large" />
      </Backdrop>

      <style>{`
        @keyframes slideInMessage {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        @keyframes slideIn {
          from {
            opacity: 0;
            transform: translateX(-10px);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </Box>
  );
};

export default LogInteraction;
