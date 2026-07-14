import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import { dashboardApi, DashboardSummary } from '../../services/dashboardApi';

interface DashboardState {
  data: DashboardSummary | null;
  loading: boolean;
  error: string | null;
}

const initialState: DashboardState = {
  data: null,
  loading: false,
  error: null,
};

export const fetchDashboardSummary = createAsyncThunk(
  'dashboard/fetchSummary',
  async (_, { rejectWithValue }) => {
    try {
      return await dashboardApi.getSummary();
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Failed to load dashboard data');
    }
  }
);

const dashboardSlice = createSlice({
  name: 'dashboard',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardSummary.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchDashboardSummary.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchDashboardSummary.rejected, (state, action) => {
        state.loading = false;
        state.error = (action.payload as string) || 'Failed to load dashboard data';
      });
  },
});

export default dashboardSlice.reducer;
