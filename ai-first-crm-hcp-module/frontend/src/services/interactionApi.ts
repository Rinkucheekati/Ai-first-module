import axios from 'axios';

const API_BASE_URL = (process.env.REACT_APP_API_URL as string) || 'http://localhost:8000';

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
      const response = await axios.post<Interaction>(
        `${API_BASE_URL}/interactions/`,
        data
      );
      return response.data;
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to create interaction');
      }
      throw new Error('An unexpected error occurred');
    }
  },

  async getInteractions(skip: number = 0, limit: number = 100): Promise<Interaction[]> {
    try {
      const response = await axios.get<Interaction[]>(
        `${API_BASE_URL}/interactions/?skip=${skip}&limit=${limit}`
      );
      return response.data;
    } catch (error: unknown) {
      throw new Error('Failed to fetch interactions');
    }
  },

  async getInteractionById(id: number): Promise<Interaction> {
    try {
      const response = await axios.get<Interaction>(`${API_BASE_URL}/interactions/${id}`);
      return response.data;
    } catch (error: unknown) {
      throw new Error('Failed to fetch interaction');
    }
  },

  async updateInteraction(id: number, data: Partial<InteractionCreate>): Promise<Interaction> {
    try {
      const response = await axios.put<Interaction>(
        `${API_BASE_URL}/interactions/${id}`,
        data
      );
      return response.data;
    } catch (error: unknown) {
      if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || 'Failed to update interaction');
      }
      throw new Error('An unexpected error occurred');
    }
  },

  async deleteInteraction(id: number): Promise<void> {
    try {
      await axios.delete(`${API_BASE_URL}/interactions/${id}`);
    } catch (error: unknown) {
      throw new Error('Failed to delete interaction');
    }
  }
};
