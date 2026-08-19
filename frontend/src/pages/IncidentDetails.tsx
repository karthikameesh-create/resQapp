import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { useNavigate, useParams } from "react-router-dom";

import api from "../api/client";
import {
  getIncident,
  type Incident,
} from "../api/incidents";
import AIIntelligencePanel from "../components/ai/AIIntelligencePanel";
import IncidentHistoryTimeline from "../components/history/IncidentHistoryTimeline";
import AIStatusBadge from "../components/status/AIStatusBadge";
import PriorityBadge from "../components/status/PriorityBadge";
import SeverityBadge from "../components/status/SeverityBadge";
import ErrorState from "../components/ui/ErrorState";
import LoadingState from "../components/ui/LoadingState";

function formatDate(date: string) {
  return new Date(date).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function DetailRow({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="detail-row">
      <span>{label}</span>
      <strong>{children}</strong>
    </div>
  );
}

export default function IncidentDetails() {
  const { incidentId } = useParams();
  const navigate = useNavigate();

  const [incident, setIncident] =
    useState<Incident | null>(null);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [retrying, setRetrying] =
    useState(false);

  async function loadIncident() {
    if (!incidentId) {
      setError("Invalid incident ID.");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await getIncident(
        Number(incidentId)
      );

      setIncident(data);
      setError("");
    } catch {
      setError(
        "Unable to load this incident."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadIncident();
  }, [incidentId]);

  /*
   * Poll the backend while AI analysis is still
   * pending or processing.
   *
   * We stop polling automatically when the backend
   * reaches completed or failed.
   */
  useEffect(() => {
    if (!incident) {
      return;
    }

    if (
      incident.ai_status !== "pending" &&
      incident.ai_status !== "processing"
    ) {
      return;
    }

    const interval = window.setInterval(
      async () => {
        try {
          const updated = await getIncident(
            incident.id
          );

          setIncident(updated);

          if (
            updated.ai_status !== "pending" &&
            updated.ai_status !== "processing"
          ) {
            window.clearInterval(interval);
          }
        } catch {
          // Keep the existing incident state.
          // The next poll can retry.
        }
      },
      3000
    );

    return () => {
      window.clearInterval(interval);
    };
  }, [
    incident?.id,
    incident?.ai_status,
  ]);

  async function retryAiAnalysis() {
    if (!incident) {
      return;
    }

    setRetrying(true);
    setError("");

    try {
      const response =
        await api.post<Incident>(
          `/incidents/${incident.id}/retry-ai`
        );

      setIncident(response.data);
    } catch (requestError: any) {
      const responseStatus =
        requestError?.response?.status;

      if (responseStatus === 409) {
        setError(
          "This incident is not currently eligible for AI retry."
        );
      } else if (responseStatus === 403) {
        setError(
          "You are not authorized to retry this AI analysis."
        );
      } else {
        setError(
          "Unable to retry AI analysis."
        );
      }
    } finally {
      setRetrying(false);
    }
  }

  if (loading) {
    return (
      <LoadingState
        message="Loading incident intelligence..."
      />
    );
  }

  if (error && !incident) {
    return (
      <ErrorState
        title="Incident unavailable"
        message={error}
        onRetry={loadIncident}
      />
    );
  }

  if (!incident) {
    return (
      <div className="incident-state">
        <h2>Incident not found</h2>

        <button
          className="primary-button"
          onClick={() =>
            navigate("/incidents")
          }
        >
          Back to Incidents
        </button>
      </div>
    );
  }

  const latitude =
    typeof incident.latitude === "number" ? incident.latitude : null;

  const longitude =
    typeof incident.longitude === "number" ? incident.longitude : null;

  return (
    <div className="incident-details-page">
      <div className="incident-context-bar">
        <button
          className="back-button"
          onClick={() => navigate("/incidents")}
        >
          ← Back to Incidents
        </button>
      </div>

      <main className="incident-details-content">
        <section className="incident-hero">
          <div className="incident-hero-main">
            <p className="eyebrow">
              INCIDENT #{incident.id}
            </p>

            <h1>{incident.title}</h1>

            <p className="incident-hero-description">
              {incident.description}
            </p>

            <div className="hero-meta">
              <span>
                {incident.incident_type}
              </span>

              <span>
                {incident.status}
              </span>

              <span>
                {formatDate(
                  incident.created_at
                )}
              </span>
            </div>
          </div>

          <div className="incident-hero-priority">
            <span className="hero-label">
              PRIORITY
            </span>

            <PriorityBadge
              priority={incident.priority}
              large
            />
          </div>
        </section>

        {error && (
          <div className="form-error-box">
            {error}
          </div>
        )}

        <section className="details-grid">
          <div className="details-main-column">
            <AIIntelligencePanel
              incident={incident}
              onRetryAnalysis={retryAiAnalysis}
              retrying={retrying}
            />

            <section className="details-panel">
              <div className="details-panel-header">
                <div>
                  <p className="panel-eyebrow">
                    INCIDENT INFORMATION
                  </p>

                  <h2>
                    Incident Details
                  </h2>
                </div>
              </div>

              <div className="details-list">
                <DetailRow label="Incident ID">
                  #{incident.id}
                </DetailRow>

                <DetailRow label="Type">
                  {incident.incident_type}
                </DetailRow>

                <DetailRow label="Status">
                  {incident.status}
                </DetailRow>

                <DetailRow label="Priority">
                  {incident.priority}
                </DetailRow>

                <DetailRow label="AI Status">
                  <AIStatusBadge
                    status={incident.ai_status}
                  />
                </DetailRow>

                {incident.reporter_id && (
                  <DetailRow label="Reporter">
                    #{incident.reporter_id}
                  </DetailRow>
                )}

                <DetailRow label="Created">
                  {formatDate(
                    incident.created_at
                  )}
                </DetailRow>
              </div>
            </section>

            <IncidentHistoryTimeline
              incidentId={incident.id}
            />
          </div>

          <aside className="details-side-column">
            <section className="details-panel">
              <div className="details-panel-header">
                <div>
                  <p className="panel-eyebrow">
                    LOCATION
                  </p>

                  <h2>
                    Incident Coordinates
                  </h2>
                </div>
              </div>

              <div className="coordinates-card">
                <div>
                  <span>Latitude</span>
                  <strong>
                    {typeof latitude === "number"
                      ? latitude.toFixed(6)
                      : "N/A"}
                  </strong>
                </div>

                <div>
                  <span>Longitude</span>
                  <strong>
                    {typeof longitude === "number"
                      ? longitude.toFixed(6)
                      : "N/A"}
                  </strong>
                </div>
              </div>

              <div className="location-placeholder">
                <div className="location-pin">
                  +
                </div>

                <span>
                  Map visualization will be added
                  with the geospatial dashboard.
                </span>
              </div>
            </section>

            <section className="details-panel">
              <p className="panel-eyebrow">
                OPERATIONAL STATUS
              </p>

              <h2>Response Snapshot</h2>

              <div className="operational-status-list">
                <div className="operational-status-row">
                  <span>Priority</span>
                  <PriorityBadge
                    priority={incident.priority}
                  />
                </div>

                <div className="operational-status-row">
                  <span>AI Status</span>
                  <AIStatusBadge
                    status={incident.ai_status}
                  />
                </div>

                <div className="operational-status-row">
                  <span>Severity</span>
                  <SeverityBadge
                    severity={incident.predicted_severity}
                  />
                </div>

                <div className="operational-status-row">
                  <span>Category</span>
                  <strong className="operational-category">
                    {incident.predicted_category ??
                      "Pending"}
                  </strong>
                </div>
              </div>
            </section>
          </aside>
        </section>
      </main>
    </div>
  );
}