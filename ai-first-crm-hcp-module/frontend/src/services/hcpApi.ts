import apiClient from './apiClient';

export interface HCP {
  id: number;
  doctor_name: string;
  specialization: string;
  hospital: string;
  email: string;
  phone: string;
  city: string;
}

export interface HCPCreateRequest {
  doctor_name: string;
  hospital: string;
  specialization: string;
  city: string;
  phone: string;
  email: string;
}

export interface HCPUpdateRequest {
  doctor_name?: string;
  hospital?: string;
  specialization?: string;
  city?: string;
  phone?: string;
  email?: string;
}

export interface HCPListResponse {
  hcps: HCP[];
  total: number;
}

export const hcpApi = {
  /**
   * Get all HCPs with optional search and pagination
   */
  async getHCPs(skip: number = 0, limit: number = 100, search?: string): Promise<HCPListResponse> {
    try {
      const response = await apiClient.get<HCPListResponse>('/hcp', {
        params: {
          skip,
          limit,
          search: search || undefined,
        },
      });
      return response.data;
    } catch (error: unknown) {
      if (error instanceof Error && 'response' in error) {
        const axiosError = error as any;
        throw new Error(axiosError.response?.data?.detail || 'Failed to fetch HCPs');
      }
      throw new Error('An unexpected error occurred');
    }
  },

  /**
   * Get a single HCP by ID
   */
  async getHCPById(id: number): Promise<HCP> {
    try {
      const response = await apiClient.get<HCP>(`/hcp/${id}`);
      return response.data;
    } catch (error: unknown) {
      if (error instanceof Error && 'response' in error) {
        const axiosError = error as any;
        throw new Error(axiosError.response?.data?.detail || 'Failed to fetch HCP');
      }
      throw new Error('An unexpected error occurred');
    }
  },

  /**
   * Create a new HCP
   */
  async createHCP(data: HCPCreateRequest): Promise<HCP> {
    try {
      const response = await apiClient.post<HCP>('/hcp', data);
      return response.data;
    } catch (error: unknown) {
      if (error instanceof Error && 'response' in error) {
        const axiosError = error as any;
        throw new Error(axiosError.response?.data?.detail || 'Failed to create HCP');
      }
      throw new Error('An unexpected error occurred');
    }
  },

  /**
   * Update an HCP
   */
  async updateHCP(id: number, data: HCPUpdateRequest): Promise<HCP> {
    try {
      const response = await apiClient.put<HCP>(`/hcp/${id}`, data);
      return response.data;
    } catch (error: unknown) {
      if (error instanceof Error && 'response' in error) {
        const axiosError = error as any;
        throw new Error(axiosError.response?.data?.detail || 'Failed to update HCP');
      }
      throw new Error('An unexpected error occurred');
    }
  },

  /**
   * Delete an HCP
   */
  async deleteHCP(id: number): Promise<void> {
    try {
      await apiClient.delete(`/hcp/${id}`);
    } catch (error: unknown) {
      if (error instanceof Error && 'response' in error) {
        const axiosError = error as any;
        throw new Error(axiosError.response?.data?.detail || 'Failed to delete HCP');
      }
      throw new Error('An unexpected error occurred');
    }
  },
};
