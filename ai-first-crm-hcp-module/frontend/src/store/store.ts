import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import hcpReducer from './slices/hcpSlice';
import interactionReducer from './slices/interactionSlice';
import agentReducer from './slices/agentSlice';
import dashboardReducer from './slices/dashboardSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    hcp: hcpReducer,
    interaction: interactionReducer,
    agent: agentReducer,
    dashboard: dashboardReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
