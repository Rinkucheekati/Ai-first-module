import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider, CssBaseline, Box } from '@mui/material';
import { store } from './store/store';
import theme from './utils/theme';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import HCPList from './pages/HCPList';
import LogInteraction from './pages/LogInteraction';
import InteractionHistory from './pages/InteractionHistory';
import Sidebar from './components/layout/Sidebar';
import Navbar from './components/layout/Navbar';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = localStorage.getItem('token') !== null;
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};

const App: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Box sx={{ display: 'flex' }}>
                    <Navbar onMenuClick={handleDrawerToggle} />
                    <Sidebar open={mobileOpen} onClose={handleDrawerToggle} />
                    <Box
                      component="main"
                      sx={{
                        flexGrow: 1,
                        p: 3,
                        width: { sm: `calc(100% - 260px)` },
                        mt: '64px',
                      }}
                    >
                      <Routes>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/hcp-list" element={<HCPList />} />
                        <Route path="/log-interaction" element={<LogInteraction />} />
                        <Route path="/interaction-history" element={<InteractionHistory />} />
                        <Route path="/" element={<Navigate to="/dashboard" />} />
                      </Routes>
                    </Box>
                  </Box>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </ThemeProvider>
    </Provider>
  );
};

export default App;
