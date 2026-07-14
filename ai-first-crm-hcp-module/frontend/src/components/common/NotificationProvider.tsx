import React from 'react';
import { Alert, AlertColor, Box, Snackbar, SnackbarCloseReason } from '@mui/material';

interface NotificationConfig {
  message: string;
  severity: AlertColor;
  duration?: number;
  onClose?: () => void;
}

interface NotificationProviderProps {
  children: React.ReactNode;
}

interface NotificationContextType {
  showNotification: (config: NotificationConfig) => void;
  success: (message: string, duration?: number) => void;
  error: (message: string, duration?: number) => void;
  warning: (message: string, duration?: number) => void;
  info: (message: string, duration?: number) => void;
}

const NotificationContext = React.createContext<NotificationContextType | undefined>(undefined);

export const useNotification = () => {
  const context = React.useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within NotificationProvider');
  }
  return context;
};

export const NotificationProvider: React.FC<NotificationProviderProps> = ({ children }) => {
  const [notification, setNotification] = React.useState<NotificationConfig | null>(null);
  const [open, setOpen] = React.useState(false);

  const showNotification = (config: NotificationConfig) => {
    setNotification(config);
    setOpen(true);
  };

  const success = (message: string, duration?: number) => {
    showNotification({
      message,
      severity: 'success',
      duration,
    });
  };

  const error = (message: string, duration?: number) => {
    showNotification({
      message,
      severity: 'error',
      duration,
    });
  };

  const warning = (message: string, duration?: number) => {
    showNotification({
      message,
      severity: 'warning',
      duration,
    });
  };

  const info = (message: string, duration?: number) => {
    showNotification({
      message,
      severity: 'info',
      duration,
    });
  };

  const handleClose = (
    event?: React.SyntheticEvent | Event,
    reason?: SnackbarCloseReason
  ) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);
    notification?.onClose?.();
  };

  return (
    <NotificationContext.Provider value={{ showNotification, success, error, warning, info }}>
      {children}
      <Snackbar
        open={open}
        autoHideDuration={notification?.duration || 4000}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        sx={{
          animation: 'slideIn 0.3s ease-out',
        }}
      >
        <Alert
          onClose={handleClose}
          severity={notification?.severity || 'info'}
          variant="filled"
          sx={{
            width: '100%',
            minWidth: 300,
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            borderRadius: 1,
            animation: 'slideIn 0.3s ease-out',
          }}
        >
          {notification?.message}
        </Alert>
      </Snackbar>
      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(400px);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </NotificationContext.Provider>
  );
};

export default NotificationProvider;
