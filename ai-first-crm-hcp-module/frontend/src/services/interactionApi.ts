import apiClient from './apiClient';

export interface InteractionCreate {
  hcp_id: number;
  interaction_date: string;
  discussion: string;
  summary?: string;
  follow_up_date?: string;
}

export interface Interaction {
  id: number;
  hcp_id: number;
  interaction_date: string;
  discussion: string;
  summary?: string;
  follow_up_date?: string;
  created_at: string;
  updated_at: string;
}

export const interactionApi = {
  async createInteraction(data: InteractionCreate): Promise<Interaction> {
    try {
      const response = await apiClient.post<Interaction>('/interactions/', data);
      return response.data;
    } catch (error: unknown) {
      if (error instanceof Error && 'response' in error) {
        const axiosError = error as any;
        throw new Error(axiosError.response?.data?.detail || 'Failed to create interaction');
      }
      throw new Error('An unexpected error occurred');
    }
  },

  async getInteractions(skip: number = 0, limit: number = 100): Promise<Interaction[]> {
    try {
      const response = await apiClient.get<Interaction[]>('/interactions/', {
        params: { skip, limit },
      });
      return response.data;
    } catch (error: unknown) {
      throw new Error('Failed to fetch interactions');
    }
  },

  async getInteractionById(id: number): Promise<Interaction> {
    try {
      const response = await apiClient.get<Interaction>(`/interactions/${id}`);
      return response.data;
    } catch (error: unknown) {
      throw new Error('Failed to fetch interaction');
    }
  },

  async updateInteraction(id: number, data: Partial<InteractionCreate>): Promise<Interaction> {
    try {
      const response = await apiClient.put<Interaction>(`/interactions/${id}`, data);
      return response.data;
    } catch (error: unknown) {
      if (error instanceof Error && 'response' in error) {
        const axiosError = error as any;
        throw new Error(axiosError.response?.data?.detail || 'Failed to update interaction');
      }
      throw new Error('An unexpected error occurred');
    }
  },

  async deleteInteraction(id: number): Promise<void> {
    try {
      await apiClient.delete(`/interactions/${id}`);
    } catch (error: unknown) {
      throw new Error('Failed to delete interaction');
    }
  }
};
