import type { Incident } from "../../api/incidents";
import AIStatusBadge from "../status/AIStatusBadge";
import ConfidenceBar from "../status/ConfidenceBar";
import PriorityBadge from "../status/PriorityBadge";
import SeverityBadge from "../status/SeverityBadge";

interface AIIntelligencePanelProps {
  incident: Incident;
  onRetryAnalysis?: () => Promise<void> | void;
  retrying?: boolean;
}

export default function AIIntelligencePanel({
  incident,
  onRetryAnalysis,
  retrying = false,
}: AIIntelligencePanelProps) {
  const processing =
    incident.ai_status === "pending" ||
    incident.ai_status === "processing";

  const failed = incident.ai_status === "failed";

  if (processing) {
    return (
      <section className="ai-intelligence-panel">
        <div className="ai-panel-heading">
          <div>
            <p className="panel-eyebrow">
              AI INTELLIGENCE
            </p>

            <h2>Automated Incident Analysis</h2>
          </div>

          <AIStatusBadge status={incident.ai_status} />
        </div>

        <div className="ai-analysis-processing">
          <div className="ai-orb">AI</div>

          <div>
            <h3>Analyzing incident...</h3>

            <p>
              ResQAI is evaluating severity, category and emergency response
              requirements.
            </p>

            <div className="ai-processing-bar">
              <span />
            </div>

            <small>Results will update automatically.</small>
          </div>
        </div>
      </section>
    );
  }

  if (failed) {
    return (
      <section className="ai-intelligence-panel">
        <div className="ai-panel-heading">
          <div>
            <p className="panel-eyebrow">
              AI INTELLIGENCE
            </p>

            <h2>Automated Incident Analysis</h2>
          </div>

          <AIStatusBadge status={incident.ai_status} />
        </div>

        <div className="ai-analysis-failed">
          <div className="ai-failure-icon">!</div>

          <div>
            <h3>AI analysis unavailable</h3>

            <p>
              The incident has been saved, but automated analysis did not
              complete.
            </p>

            {onRetryAnalysis && (
              <button
                className="secondary-button retry-button"
                onClick={onRetryAnalysis}
                disabled={retrying}
              >
                {retrying ? "Retrying..." : "Retry AI Analysis"}
              </button>
            )}
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="ai-intelligence-panel">
      <div className="ai-panel-heading">
        <div>
          <p className="panel-eyebrow">
            AI INTELLIGENCE
          </p>

          <h2>Automated Incident Analysis</h2>
        </div>

        <AIStatusBadge status={incident.ai_status} />
      </div>

      <div className="ai-primary-grid">
        <div className="ai-classification">
          <span className="ai-card-label">
            PREDICTED SEVERITY
          </span>

          <div className="ai-severity-value">
            <SeverityBadge
              severity={incident.predicted_severity}
              large
            />
          </div>

          <ConfidenceBar
            label="Model confidence"
            value={incident.severity_confidence}
          />
        </div>

        <div className="ai-classification">
          <span className="ai-card-label">
            PREDICTED CATEGORY
          </span>

          <h3 className="ai-category-value">
            {incident.predicted_category ?? "Unknown"}
          </h3>

          <ConfidenceBar
            label="Model confidence"
            value={incident.category_confidence}
          />
        </div>

        <div className="ai-priority-card">
          <span className="ai-card-label">
            FINAL OPERATIONAL PRIORITY
          </span>

          <PriorityBadge
            priority={incident.priority}
            large
          />

          <p>
            The final operational priority is determined by ResQAI's incident
            prioritization logic.
          </p>
        </div>
      </div>

      {incident.ai_summary && (
        <div className="ai-section">
          <div className="ai-section-heading">
            <h3>AI Summary</h3>
            <span>Generated analysis</span>
          </div>

          <p className="ai-summary">
            {incident.ai_summary}
          </p>
        </div>
      )}

      <div className="ai-section">
        <div className="ai-section-heading">
          <h3>Recommended Response</h3>
          <span>AI-generated operational guidance</span>
        </div>

        {incident.recommended_response &&
        incident.recommended_response.length > 0 ? (
          <ol className="ai-response-list">
            {incident.recommended_response.map((response, index) => (
              <li key={`${incident.id}-response-${index}`}>
                <span className="ai-response-number">
                  {index + 1}
                </span>

                <span>{response}</span>
              </li>
            ))}
          </ol>
        ) : (
          <p className="muted-text">
            No recommended response available.
          </p>
        )}
      </div>

      <div className="ai-completed-banner">
        <span className="ai-completed-check">✓</span>

        <div>
          <strong>AI analysis completed</strong>

          <span>
            Classification and response guidance are available for this incident.
          </span>
        </div>
      </div>
    </section>
  );
}