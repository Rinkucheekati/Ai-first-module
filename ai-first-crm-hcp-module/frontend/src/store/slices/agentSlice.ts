import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { agentApi, AgentChatResponse, StructuredInteractionData } from '../../services/agentApi';

interface FormData {
  hcpId: string;
  hcpName: string;
  interactionType: string;
  date: string;
  duration: string;
  notes: string;
  outcome: string;
  followUpRequired: boolean;
  followUpDate: string;
}

interface AgentState {
  isLoading: boolean;
  error: string | null;
  currentResponse: AgentChatResponse | null;
  structuredData: StructuredInteractionData | null;
  conversationHistory: Array<{ role: string; content: string }>;
  isSaved: boolean;
  saveError: string | null;
  formData: FormData;
  hasExtractedData: boolean;
}

const initialFormData: FormData = {
  hcpId: '',
  hcpName: '',
  interactionType: '',
  date: new Date().toISOString().split('T')[0],
  duration: '',
  notes: '',
  outcome: '',
  followUpRequired: false,
  followUpDate: '',
};

const initialState: AgentState = {
  isLoading: false,
  error: null,
  currentResponse: null,
  structuredData: null,
  conversationHistory: [],
  isSaved: false,
  saveError: null,
  formData: initialFormData,
  hasExtractedData: false,
};

export const sendMessage = createAsyncThunk(
  'agent/sendMessage',
  async (message: string, { rejectWithValue }) => {
    try {
      const response = await agentApi.chat({ message });
      return response;
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to send message';
      return rejectWithValue(errorMessage);
    }
  }
);

const agentSlice = createSlice({
  name: 'agent',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    clearResponse: (state) => {
      state.currentResponse = null;
      state.structuredData = null;
      state.isSaved = false;
      state.saveError = null;
      state.hasExtractedData = false;
    },
    setConversationHistory: (state, action: PayloadAction<Array<{ role: string; content: string }>>) => {
      state.conversationHistory = action.payload;
    },
    addToConversationHistory: (state, action: PayloadAction<{ role: string; content: string }>) => {
      state.conversationHistory.push(action.payload);
    },
    markAsSaved: (state) => {
      state.isSaved = true;
    },
    clearSaveError: (state) => {
      state.saveError = null;
    },
    updateFormData: (state, action: PayloadAction<Partial<FormData>>) => {
      state.formData = { ...state.formData, ...action.payload };
    },
    resetFormData: (state) => {
      state.formData = initialFormData;
      state.hasExtractedData = false;
    },
    populateFormFromExtraction: (state, action: PayloadAction<StructuredInteractionData>) => {
      const extracted = action.payload;
      
      // Only populate fields that are not already manually edited
      if (!state.hasExtractedData) {
        if (extracted.doctor_name) {
          state.formData.hcpName = extracted.doctor_name;
        }
        if (extracted.interaction_date) {
          state.formData.date = extracted.interaction_date;
        }
        if (extracted.follow_up_date) {
          state.formData.followUpDate = extracted.follow_up_date;
          state.formData.followUpRequired = true;
        }
        if (extracted.summary) {
          state.formData.outcome = extracted.summary;
        }
        state.formData.notes = state.formData.notes || ''; // Keep existing notes
        state.hasExtractedData = true;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
        state.isSaved = false;
        state.saveError = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentResponse = action.payload;
        state.structuredData = action.payload.structured_data || null;
        
        // Add to conversation history
        if (action.payload.conversation_history) {
          state.conversationHistory = action.payload.conversation_history;
        }
        
        // Auto-mark as saved if interaction was stored
        if (action.payload.interaction_id) {
          state.isSaved = true;
        }
        
        // Auto-populate form if structured data is available
        if (action.payload.structured_data) {
          agentSlice.caseReducers.populateFormFromExtraction(state, {
            payload: action.payload.structured_data,
            type: 'agent/populateFormFromExtraction',
          });
        }
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  clearError,
  clearResponse,
  setConversationHistory,
  addToConversationHistory,
  markAsSaved,
  clearSaveError,
  updateFormData,
  resetFormData,
  populateFormFromExtraction,
} = agentSlice.actions;

export default agentSlice.reducer;
