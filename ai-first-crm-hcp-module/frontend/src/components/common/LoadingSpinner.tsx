import React from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

interface LoadingSpinnerProps {
  message?: string;
  fullScreen?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  fullScreen = false,
  size = 'medium',
}) => {
  const spinnerSize = size === 'small' ? 32 : size === 'large' ? 64 : 48;

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 2,
        ...(fullScreen && {
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          zIndex: 1300,
        }),
        ...(!fullScreen && {
          py: 4,
        }),
      }}
    >
      <CircularProgress
        size={spinnerSize}
        sx={{
          animation: 'fadeInScale 0.3s ease-in-out',
        }}
      />
      {message && (
        <Typography
          variant="body1"
          color="text.secondary"
          sx={{
            animation: 'fadeIn 0.5s ease-in-out 0.1s both',
            fontWeight: 500,
          }}
        >
          {message}
        </Typography>
      )}
      <style>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
        @keyframes fadeInScale {
          from {
            opacity: 0;
            transform: scale(0.8);
          }
          to {
            opacity: 1;
            transform: scale(1);
          }
        }
      `}</style>
    </Box>
  );
};

export default LoadingSpinner;
