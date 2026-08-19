import api from "./client";

export interface DashboardAnalytics {
  total_incidents: number;
  status_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  priority_distribution: Record<string, number>;
  ai_status_distribution: Record<string, number>;
  average_severity_confidence?: number | null;
  average_category_confidence?: number | null;
}

export interface TrendPoint {
  date: string;
  count: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
}

export interface TrendResponse {
  trends: TrendPoint[];
}

export interface HeatmapPoint {
  id: number;
  latitude: number;
  longitude: number;
  severity: string;
  category: string;
  priority: string;
  status: string;
  created_at: string;
}

export interface HeatmapResponse {
  incidents: HeatmapPoint[];
}

export async function getDashboardAnalytics(): Promise<DashboardAnalytics> {
  const response = await api.get<DashboardAnalytics>(
    "/analytics/dashboard"
  );

  return response.data;
}

export async function getIncidentTrends(): Promise<TrendResponse> {
  const response = await api.get<TrendResponse>(
    "/analytics/trends"
  );

  return response.data;
}

export async function getIncidentHeatmap(): Promise<HeatmapResponse> {
  const response = await api.get<HeatmapResponse>(
    "/analytics/heatmap"
  );

  return response.data;
}