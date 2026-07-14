import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface HCP {
  id: string;
  name: string;
  specialty: string;
  organization: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  country: string;
  status: 'active' | 'inactive';
  lastInteraction: string;
  totalInteractions: number;
}

interface HCPState {
  hcps: HCP[];
  selectedHCP: HCP | null;
  loading: boolean;
  error: string | null;
}

const initialState: HCPState = {
  hcps: [],
  selectedHCP: null,
  loading: false,
  error: null,
};

const hcpSlice = createSlice({
  name: 'hcp',
  initialState,
  reducers: {
    setHCPs: (state, action: PayloadAction<HCP[]>) => {
      state.hcps = action.payload;
    },
    setSelectedHCP: (state, action: PayloadAction<HCP>) => {
      state.selectedHCP = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const { setHCPs, setSelectedHCP, setLoading, setError } = hcpSlice.actions;
export default hcpSlice.reducer;
