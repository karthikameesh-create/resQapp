import api from "./client";

export interface IncidentHistory {
  id: number;
  incident_id: number | null;
  action: string;
  field: string | null;
  old_value: string | null;
  new_value: string | null;
  changed_by: number | null;
  created_at: string;
}

export async function getIncidentHistory(
  incidentId: number
): Promise<IncidentHistory[]> {
  const response = await api.get<IncidentHistory[]>(
    `/incidents/${incidentId}/history`
  );

  return response.data;
}