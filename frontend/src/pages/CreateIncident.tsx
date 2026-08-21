import { useState } from "react";
import type { FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import {
  createIncident,
  type CreateIncidentData,
} from "../api/incidents";
import ButtonSpinner from "../components/ui/ButtonSpinner";

const incidentTypes = [
  "Traffic Accident",
  "Medical Emergency",
  "Structure Fire",
  "Flood",
  "Landslide",
  "Chemical Hazard",
  "Explosion",
  "Building Collapse",
  "Other",
];

export default function CreateIncident() {
  const navigate = useNavigate();

  const [form, setForm] =
    useState<CreateIncidentData>({
      title: "",
      description: "",
      incident_type: "Traffic Accident",
      latitude: 12.9141,
      longitude: 74.856,
    });

  const [submitting, setSubmitting] =
    useState(false);

  const [error, setError] =
    useState("");

  function updateField(
    field: keyof CreateIncidentData,
    value: string | number
  ) {
    setForm((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();

    setSubmitting(true);
    setError("");

    try {
      const incident = await createIncident(form);

      navigate(
        `/incidents/${incident.id}`
      );
    } catch {
      setError(
        "Unable to create the incident. Please check your information and try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="incident-page">
      <div className="incident-card">
        <div className="incident-heading">
          <p className="eyebrow">
            EMERGENCY REPORT
          </p>

          <h1>Report an Incident</h1>

          <p>
            Provide accurate information so ResQAI
            can classify the incident and determine
            response priority.
          </p>
        </div>

        <form
          className="incident-form"
          onSubmit={handleSubmit}
        >
          <div className="form-group">
            <label htmlFor="title">
              Incident Title
            </label>

            <input
              id="title"
              value={form.title}
              onChange={(event) =>
                updateField(
                  "title",
                  event.target.value
                )
              }
              minLength={3}
              maxLength={200}
              placeholder="e.g. Bus accident near Mangalore"
              required
            />

            <span className="field-hint">
              3–200 characters
            </span>
          </div>

          <div className="form-group">
            <label htmlFor="incident_type">
              Incident Type
            </label>

            <select
              id="incident_type"
              value={form.incident_type}
              onChange={(event) =>
                updateField(
                  "incident_type",
                  event.target.value
                )
              }
            >
              {incidentTypes.map((type) => (
                <option
                  key={type}
                  value={type}
                >
                  {type}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="description">
              Description
            </label>

            <textarea
              id="description"
              value={form.description}
              onChange={(event) =>
                updateField(
                  "description",
                  event.target.value
                )
              }
              minLength={5}
              maxLength={5000}
              rows={7}
              placeholder="Describe what happened, injuries, casualties, hazards, rescue needs, etc."
              required
            />

            <span className="field-hint">
              {form.description.length}/5000
            </span>
          </div>

          <div className="location-section">
            <div>
              <h3>Incident Location</h3>

              <p>
                Enter the approximate coordinates
                of the incident.
              </p>
            </div>

            <div className="location-grid">
              <div className="form-group">
                <label htmlFor="latitude">
                  Latitude
                </label>

                <input
                  id="latitude"
                  type="number"
                  step="any"
                  min="-90"
                  max="90"
                  value={form.latitude}
                  onChange={(event) =>
                    updateField(
                      "latitude",
                      Number(event.target.value)
                    )
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="longitude">
                  Longitude
                </label>

                <input
                  id="longitude"
                  type="number"
                  step="any"
                  min="-180"
                  max="180"
                  value={form.longitude}
                  onChange={(event) =>
                    updateField(
                      "longitude",
                      Number(event.target.value)
                    )
                  }
                  required
                />
              </div>
            </div>
          </div>

          {error && (
            <div
              className="form-error-box"
              aria-live="polite"
            >
              {error}
            </div>
          )}

          <div className="incident-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={() =>
                navigate("/dashboard")
              }
              disabled={submitting}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <ButtonSpinner />
                  Submitting...
                </>
              ) : (
                "Submit Incident"
              )}
            </button>
          </div>

          <div className="ai-note">
            <strong>AI analysis:</strong>{" "}
            After submission, ResQAI will analyze
            the incident in the background to
            determine severity, category, confidence
            and response priority.
          </div>
        </form>
      </div>
    </div>
  );
}