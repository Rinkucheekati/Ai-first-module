import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Alert,
  Box,
  Card,
  CardContent,
  CircularProgress,
  Container,
  Grid,
  Paper,
  Typography,
  Fade,
} from '@mui/material';
import {
  AssignmentLate as FollowUpIcon,
  Event as EventIcon,
  People as PeopleIcon,
  SmartToy as SmartToyIcon,
} from '@mui/icons-material';
import { AppDispatch, RootState } from '../store/store';
import { fetchDashboardSummary } from '../store/slices/dashboardSlice';
import LoadingSpinner from '../components/common/LoadingSpinner';

const formatDate = (date: string) => new Intl.DateTimeFormat(undefined, {
  dateStyle: 'medium',
  timeStyle: 'short',
}).format(new Date(date));

const Dashboard: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { data, loading, error } = useSelector((state: RootState) => state.dashboard);

  useEffect(() => {
    dispatch(fetchDashboardSummary());
  }, [dispatch]);

  const stats = [
    { title: 'Total HCP', value: data?.total_hcps ?? 0, icon: <PeopleIcon sx={{ fontSize: 40 }} />, color: '#1976d2' },
    { title: 'Total Interactions', value: data?.total_interactions ?? 0, icon: <EventIcon sx={{ fontSize: 40 }} />, color: '#9c27b0' },
    { title: "Today's Meetings", value: data?.todays_meetings ?? 0, icon: <EventIcon sx={{ fontSize: 40 }} />, color: '#2e7d32' },
    { title: 'Pending Follow-ups', value: data?.pending_follow_ups ?? 0, icon: <FollowUpIcon sx={{ fontSize: 40 }} />, color: '#ed6c02' },
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 4, animation: 'fadeIn 0.3s ease-out' }}>Dashboard</Typography>
        {error && (
          <Fade in={true} timeout={400}>
            <Alert severity="error" sx={{ mb: 3, animation: 'slideInMessage 0.3s ease-out' }}>{error}</Alert>
          </Fade>
        )}
        {loading && !data ? (
          <LoadingSpinner message="Loading dashboard..." />
        ) : (
          <Grid container spacing={3}>
            {stats.map((stat, index) => (
              <Grid item xs={12} sm={6} md={3} key={stat.title}>
                <Fade in={true} timeout={400 + index * 100}>
                  <Card
                    sx={{
                      height: '100%',
                      position: 'relative',
                      overflow: 'hidden',
                      transition: 'all 0.3s ease-in-out',
                      '&:hover': {
                        transform: 'translateY(-4px)',
                        boxShadow: '0 8px 16px rgba(0, 0, 0, 0.12)',
                      },
                      animation: 'slideInCard 0.4s ease-out',
                    }}
                  >
                    <Box sx={{ position: 'absolute', top: -20, right: -20, width: 100, height: 100, borderRadius: '50%', backgroundColor: `${stat.color}20` }} />
                    <CardContent sx={{ position: 'relative' }}>
                      <Box sx={{ p: 1.5, width: 'fit-content', borderRadius: 2, backgroundColor: `${stat.color}15`, color: stat.color, mb: 2 }}>{stat.icon}</Box>
                      <Typography variant="h3" sx={{ fontWeight: 600 }}>{stat.value}</Typography>
                      <Typography variant="body2" color="text.secondary">{stat.title}</Typography>
                    </CardContent>
                  </Card>
                </Fade>
              </Grid>
            ))}

            <Grid item xs={12} md={6}>
              <Fade in={true} timeout={600}>
                <Paper
                  sx={{
                    p: 3,
                    height: '100%',
                    transition: 'all 0.3s ease-in-out',
                    animation: 'slideInCard 0.5s ease-out',
                    '&:hover': {
                      boxShadow: '0 8px 16px rgba(0, 0, 0, 0.12)',
                    },
                  }}
                >
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>Upcoming Meetings</Typography>
                  {data?.upcoming_meetings.length ? data.upcoming_meetings.map((meeting) => (
                    <Box
                      key={meeting.id}
                      sx={{
                        py: 1.5,
                        borderBottom: '1px solid #e0e0e0',
                        '&:last-child': { borderBottom: 0 },
                        transition: 'all 0.2s ease-in-out',
                        '&:hover': {
                          backgroundColor: '#f5f5f5',
                          paddingLeft: 1,
                        },
                      }}
                    >
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>{meeting.hcp_name}</Typography>
                      <Typography variant="body2" color="text.secondary">{formatDate(meeting.interaction_date)}</Typography>
                    </Box>
                  )) : <Typography color="text.secondary">No upcoming meetings.</Typography>}
                </Paper>
              </Fade>
            </Grid>

            <Grid item xs={12} md={6}>
              <Fade in={true} timeout={700}>
                <Paper
                  sx={{
                    p: 3,
                    height: '100%',
                    transition: 'all 0.3s ease-in-out',
                    animation: 'slideInCard 0.6s ease-out',
                    '&:hover': {
                      boxShadow: '0 8px 16px rgba(0, 0, 0, 0.12)',
                    },
                  }}
                >
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>Recent AI Summaries</Typography>
                  {data?.recent_ai_summaries.length ? data.recent_ai_summaries.map((meeting) => (
                    <Box
                      key={meeting.id}
                      sx={{
                        py: 1.5,
                        borderBottom: '1px solid #e0e0e0',
                        '&:last-child': { borderBottom: 0 },
                        transition: 'all 0.2s ease-in-out',
                        '&:hover': {
                          backgroundColor: '#f5f5f5',
                          paddingLeft: 1,
                        },
                      }}
                    >
                      <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                        <SmartToyIcon color="success" fontSize="small" />
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>{meeting.hcp_name}</Typography>
                      </Box>
                      <Typography variant="body2" color="text.secondary">{meeting.summary}</Typography>
                    </Box>
                  )) : <Typography color="text.secondary">No AI summaries available.</Typography>}
                </Paper>
              </Fade>
            </Grid>
          </Grid>
        )}
      </Container>

      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        @keyframes slideInCard {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
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
      `}</style>
    </Box>
  );
};

export default Dashboard;
