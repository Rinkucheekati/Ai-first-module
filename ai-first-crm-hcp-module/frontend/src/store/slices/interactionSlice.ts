import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Interaction {
  id: string;
  hcpId: string;
  hcpName: string;
  type: 'call' | 'email' | 'meeting' | 'visit';
  date: string;
  duration: number;
  notes: string;
  outcome: string;
  followUpRequired: boolean;
  followUpDate: string | null;
  aiSummary: string;
  aiInsights: string[];
}

interface InteractionState {
  interactions: Interaction[];
  selectedInteraction: Interaction | null;
  loading: boolean;
  error: string | null;
}

const initialState: InteractionState = {
  interactions: [],
  selectedInteraction: null,
  loading: false,
  error: null,
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    setInteractions: (state, action: PayloadAction<Interaction[]>) => {
      state.interactions = action.payload;
    },
    addInteraction: (state, action: PayloadAction<Interaction>) => {
      state.interactions.unshift(action.payload);
    },
    setSelectedInteraction: (state, action: PayloadAction<Interaction>) => {
      state.selectedInteraction = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const { setInteractions, addInteraction, setSelectedInteraction, setLoading, setError } = interactionSlice.actions;
export default interactionSlice.reducer;
