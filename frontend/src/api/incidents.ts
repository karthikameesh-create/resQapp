import api from "./client";

export interface Incident {
  id: number;
  title: string;
  description: string;
  incident_type: string;
  status: string;
  severity: string;
  priority: string;

  predicted_severity: string | null;
  severity_confidence: number | null;

  predicted_category: string | null;
  category_confidence: number | null;

  ai_summary: string | null;
  recommended_response: string[] | null;
  ai_status: string;

  latitude: number;
  longitude: number;
  reporter_id: number;
  created_at: string;
}

export interface CreateIncidentData {
  title: string;
  description: string;
  incident_type: string;
  latitude: number;
  longitude: number;
}

export async function createIncident(
  data: CreateIncidentData
): Promise<Incident> {
  const response = await api.post<Incident>(
    "/incidents",
    data
  );

  return response.data;
}

export async function getIncidents(
  params?: {
    skip?: number;
    limit?: number;
    status?: string;
    severity?: string;
    incident_type?: string;
    search?: string;
  }
): Promise<Incident[]> {
  const response = await api.get<Incident[]>(
    "/incidents",
    {
      params,
    }
  );

  return response.data;
}

export async function getIncident(
  incidentId: number
): Promise<Incident> {
  const response = await api.get<Incident>(
    `/incidents/${incidentId}`
  );

  return response.data;
}