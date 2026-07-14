import apiClient from './apiClient';

export interface AgentChatRequest {
  message: string;
  conversation_history?: Array<{ role: string; content: string }>;
}

export interface StructuredInteractionData {
  doctor_name?: string;
  hospital?: string;
  interaction_date?: string;
  products_discussed?: string[];
  doctor_feedback?: string;
  follow_up_date?: string;
  meeting_outcome?: string;
  summary?: string;
}

export interface AgentChatResponse {
  success: boolean;
  tool_used?: string;
  interaction_id?: number;
  structured_data?: StructuredInteractionData;
  reply: string;
  conversation_history?: Array<{ role: string; content: string }>;
  error?: string;
}

export const agentApi = {
  async chat(request: AgentChatRequest): Promise<AgentChatResponse> {
    try {
      const response = await apiClient.post<AgentChatResponse>(
        '/agent/chat',
        request
      );
      return response.data;
    } catch (error: unknown) {
      if (error instanceof Error && 'response' in error) {
        const axiosError = error as any;
        throw new Error(axiosError.response?.data?.detail || 'Failed to communicate with agent');
      }
      throw new Error('An unexpected error occurred');
    }
  },

  async healthCheck(): Promise<{ status: string; service: string; groq_available: boolean; model?: string }> {
    try {
      const response = await apiClient.get('/agent/health');
      return response.data;
    } catch (error) {
      throw new Error('Agent health check failed');
    }
  }
};
