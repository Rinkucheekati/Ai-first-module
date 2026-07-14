import apiClient from './apiClient';

export interface DashboardMeeting {
  id: number;
  hcp_name: string;
  interaction_date: string;
  follow_up_date?: string | null;
  summary?: string | null;
}

export interface DashboardSummary {
  total_hcps: number;
  total_interactions: number;
  todays_meetings: number;
  pending_follow_ups: number;
  upcoming_meetings: DashboardMeeting[];
  recent_ai_summaries: DashboardMeeting[];
}

export const dashboardApi = {
  async getSummary(): Promise<DashboardSummary> {
    try {
      const response = await apiClient.get<DashboardSummary>('/dashboard/summary');
      return response.data;
    } catch (error: unknown) {
      if (error instanceof Error && 'response' in error) {
        const axiosError = error as any;
        throw new Error(axiosError.response?.data?.detail || 'Failed to load dashboard data');
      }
      throw new Error('Failed to load dashboard data');
    }
  },
};
