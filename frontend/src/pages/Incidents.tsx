import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import {
  getIncidents,
  type Incident,
} from "../api/incidents";
import AIStatusBadge from "../components/status/AIStatusBadge";
import PriorityBadge from "../components/status/PriorityBadge";
import SeverityBadge from "../components/status/SeverityBadge";
import EmptyState from "../components/ui/EmptyState";
import ErrorState from "../components/ui/ErrorState";
import LoadingState from "../components/ui/LoadingState";

const PAGE_SIZE = 10;

function formatDate(date: string) {
  return new Date(date).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function Incidents() {
  const navigate = useNavigate();

  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [searchInput, setSearchInput] = useState("");
  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");
  const [incidentType, setIncidentType] = useState("");
  const [page, setPage] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [hasNextPage, setHasNextPage] = useState(false);

  useEffect(() => {
    async function loadIncidents() {
      try {
        setLoading(true);
        setError("");

        const data = await getIncidents({
          skip: page * PAGE_SIZE,
          limit: PAGE_SIZE,
          search: search || undefined,
          severity: severity || undefined,
          status: status || undefined,
          incident_type: incidentType || undefined,
        });

        setIncidents(data);
        setHasNextPage(data.length === PAGE_SIZE);
      } catch {
        setError("Unable to load incidents. Please try again.");
      } finally {
        setLoading(false);
      }
    }

    loadIncidents();
  }, [page, search, severity, status, incidentType]);

  function handleSearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPage(0);
    setSearch(searchInput.trim());
  }

  function clearFilters() {
    setSearchInput("");
    setSearch("");
    setSeverity("");
    setStatus("");
    setIncidentType("");
    setPage(0);
  }

  return (
    <div className="incidents-page">
      <header className="incidents-page-heading">
        <div>
          <p className="eyebrow">INCIDENT MANAGEMENT</p>

          <h1>Incidents</h1>

          <p>
            Monitor reported emergencies and AI-generated intelligence.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => navigate("/incidents/new")}
        >
          Report Incident
        </button>
      </header>

      <section className="incident-filters">
        <form className="search-form" onSubmit={handleSearch}>
          <input
            type="search"
            placeholder="Search incidents..."
            value={searchInput}
            maxLength={200}
            onChange={(event) => setSearchInput(event.target.value)}
          />

          <button type="submit" className="primary-button">
            Search
          </button>
        </form>

        <div className="filter-row">
          <select
            value={severity}
            onChange={(event) => {
              setSeverity(event.target.value);
              setPage(0);
            }}
          >
            <option value="">All Severities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>

          <select
            value={status}
            onChange={(event) => {
              setStatus(event.target.value);
              setPage(0);
            }}
          >
            <option value="">All Statuses</option>
            <option value="reported">Reported</option>
            <option value="processing">Processing</option>
            <option value="resolved">Resolved</option>
          </select>

          <select
            value={incidentType}
            onChange={(event) => {
              setIncidentType(event.target.value);
              setPage(0);
            }}
          >
            <option value="">All Types</option>
            <option value="Traffic Accident">Traffic Accident</option>
            <option value="Medical Emergency">Medical Emergency</option>
            <option value="Structure Fire">Structure Fire</option>
            <option value="Flood">Flood</option>
            <option value="Landslide">Landslide</option>
            <option value="Chemical Hazard">Chemical Hazard</option>
            <option value="Explosion">Explosion</option>
            <option value="Building Collapse">Building Collapse</option>
          </select>

          <button
            type="button"
            className="clear-filter-button"
            onClick={clearFilters}
          >
            Clear
          </button>
        </div>
      </section>

      {loading && <LoadingState message="Loading incidents..." />}

      {!loading && error && (
        <ErrorState
          title="Unable to load incidents"
          message={error}
          onRetry={() => setPage(0)}
        />
      )}

      {!loading && !error && incidents.length === 0 && (
        <EmptyState
          title="No incidents found"
          message="No incidents match the current filters."
          actionLabel="Clear Filters"
          onAction={clearFilters}
        />
      )}

      {!loading && !error && incidents.length > 0 && (
        <>
          <section className="incident-list">
            {incidents.map((incident) => (
              <article
                className="incident-row"
                key={incident.id}
                onClick={() => navigate(`/incidents/${incident.id}`)}
              >
                <div className="incident-main">
                  <div className="incident-title-row">
                    <h2>{incident.title}</h2>
                    <PriorityBadge priority={incident.priority} />
                  </div>

                  <p className="incident-description">{incident.description}</p>

                  <div className="incident-meta">
                    <span>#{incident.id}</span>
                    <span>{incident.incident_type}</span>
                    <span>{incident.status}</span>
                    <span>{formatDate(incident.created_at)}</span>
                  </div>
                </div>

                <div className="incident-ai">
                  <div className="ai-label">AI STATUS</div>
                  <AIStatusBadge status={incident.ai_status} />

                  <div className="ai-severity">
                    <span>Severity</span>
                    <SeverityBadge
                      severity={incident.predicted_severity}
                    />
                  </div>

                  <div className="incident-arrow">→</div>
                </div>
              </article>
            ))}
          </section>

          <div className="pagination">
            <button
              className="secondary-button"
              disabled={page === 0}
              onClick={() => setPage((current) => Math.max(0, current - 1))}
            >
              ← Previous
            </button>

            <span>Page {page + 1}</span>

            <button
              className="secondary-button"
              disabled={!hasNextPage}
              onClick={() => setPage((current) => current + 1)}
            >
              Next →
            </button>
          </div>
        </>
      )}
    </div>
  );
}