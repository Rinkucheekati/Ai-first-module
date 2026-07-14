import React from 'react';
import { Box } from '@mui/material';

interface TypingAnimationProps {
  variant?: 'dots' | 'pulse' | 'wave';
  size?: 'small' | 'medium' | 'large';
}

const TypingAnimation: React.FC<TypingAnimationProps> = ({ 
  variant = 'dots', 
  size = 'medium' 
}) => {
  const dotSize = size === 'small' ? 4 : size === 'large' ? 10 : 6;
  const animationDuration = size === 'small' ? 1.2 : size === 'large' ? 1.6 : 1.4;
  
  const dotStyle = {
    width: dotSize,
    height: dotSize,
    borderRadius: '50%',
    backgroundColor: '#1976d2',
    display: 'inline-block',
    margin: '0 2px',
  };

  if (variant === 'dots') {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
        <Box
          sx={{
            ...dotStyle,
            animation: `typing ${animationDuration}s infinite`,
          }}
        />
        <Box
          sx={{
            ...dotStyle,
            animation: `typing ${animationDuration}s infinite 0.2s`,
          }}
        />
        <Box
          sx={{
            ...dotStyle,
            animation: `typing ${animationDuration}s infinite 0.4s`,
          }}
        />
        <style>{`
          @keyframes typing {
            0%, 60%, 100% {
              opacity: 0.3;
              transform: translateY(0);
            }
            30% {
              opacity: 1;
              transform: translateY(-${dotSize + 2}px);
            }
          }
        `}</style>
      </Box>
    );
  }

  if (variant === 'pulse') {
    return (
      <Box
        sx={{
          width: dotSize * 3,
          height: dotSize * 3,
          borderRadius: '50%',
          backgroundColor: '#1976d2',
          animation: `pulse-animation ${animationDuration}s ease-in-out infinite`,
        }}
      >
        <style>{`
          @keyframes pulse-animation {
            0%, 100% {
              opacity: 1;
              transform: scale(1);
            }
            50% {
              opacity: 0.3;
              transform: scale(0.8);
            }
          }
        `}</style>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
      {[0, 0.15, 0.3].map((delay, idx) => (
        <Box
          key={idx}
          sx={{
            ...dotStyle,
            animation: `wave-animation ${animationDuration}s ease-in-out infinite`,
            animationDelay: `${delay}s`,
          }}
        />
      ))}
      <style>{`
        @keyframes wave-animation {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-${dotSize + 4}px);
          }
        }
      `}</style>
    </Box>
  );
};

export default TypingAnimation;
