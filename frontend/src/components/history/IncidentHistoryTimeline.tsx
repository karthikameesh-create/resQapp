import { useEffect, useState } from "react";

import {
  getIncidentHistory,
  type IncidentHistory,
} from "../../api/incidentHistory";

function formatHistoryDate(date: string) {
  return new Date(date).toLocaleString("en-IN", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getActionLabel(action: string) {
  return action
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) =>
      character.toUpperCase()
    );
}

function getActionClass(action: string) {
  const normalized = action.toLowerCase();

  if (normalized.includes("create")) {
    return "history-create";
  }

  if (
    normalized.includes("update") ||
    normalized.includes("change")
  ) {
    return "history-update";
  }

  if (
    normalized.includes("ai") ||
    normalized.includes("analysis")
  ) {
    return "history-ai";
  }

  if (normalized.includes("delete")) {
    return "history-delete";
  }

  return "history-default";
}

function formatField(field: string | null) {
  if (!field) {
    return "";
  }

  return field
    .replace(/_/g, " ")
    .replace(/\b\w/g, (character) =>
      character.toUpperCase()
    );
}

export default function IncidentHistoryTimeline({
  incidentId,
}: {
  incidentId: number;
}) {
  const [history, setHistory] =
    useState<IncidentHistory[]>([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    async function loadHistory() {
      try {
        setLoading(true);
        setError("");

        const data =
          await getIncidentHistory(incidentId);

        setHistory(data);
      } catch {
        setError(
          "Unable to load incident history."
        );
      } finally {
        setLoading(false);
      }
    }

    loadHistory();
  }, [incidentId]);

  if (loading) {
    return (
      <section className="details-panel">
        <div className="details-panel-header">
          <div>
            <p className="panel-eyebrow">
              AUDIT HISTORY
            </p>

            <h2>Incident Timeline</h2>
          </div>
        </div>

        <div className="history-state">
          Loading incident history...
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="details-panel">
        <div className="details-panel-header">
          <div>
            <p className="panel-eyebrow">
              AUDIT HISTORY
            </p>

            <h2>Incident Timeline</h2>
          </div>
        </div>

        <div className="history-error">
          {error}
        </div>
      </section>
    );
  }

  return (
    <section className="details-panel">
      <div className="details-panel-header">
        <div>
          <p className="panel-eyebrow">
            AUDIT HISTORY
          </p>

          <h2>Incident Timeline</h2>
        </div>

        <span className="history-count">
          {history.length} events
        </span>
      </div>

      {history.length === 0 ? (
        <div className="history-empty">
          <div className="history-empty-icon">
            —
          </div>

          <strong>No history recorded</strong>

          <span>
            Changes to this incident will appear
            here.
          </span>
        </div>
      ) : (
        <div className="history-timeline">
          {history.map((event) => (
            <div
              className="history-event"
              key={event.id}
            >
              <div className="history-line">
                <div
                  className={[
                    "history-dot",
                    getActionClass(event.action),
                  ].join(" ")}
                />
              </div>

              <div className="history-content">
                <div className="history-event-header">
                  <div>
                    <strong>
                      {getActionLabel(
                        event.action
                      )}
                    </strong>

                    {event.field && (
                      <span className="history-field">
                        {formatField(event.field)}
                      </span>
                    )}
                  </div>

                  <time>
                    {formatHistoryDate(
                      event.created_at
                    )}
                  </time>
                </div>

                {(event.old_value !== null ||
                  event.new_value !== null) && (
                  <div className="history-change">
                    {event.old_value !== null && (
                      <div>
                        <span>Previous</span>

                        <code>
                          {event.old_value}
                        </code>
                      </div>
                    )}

                    {event.new_value !== null && (
                      <div>
                        <span>New</span>

                        <code>
                          {event.new_value}
                        </code>
                      </div>
                    )}
                  </div>
                )}

                {event.changed_by !== null && (
                  <span className="history-actor">
                    Changed by user #
                    {event.changed_by}
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}