import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  getDashboardAnalytics,
  getIncidentHeatmap,
  getIncidentTrends,
  type DashboardAnalytics,
  type HeatmapPoint,
  type TrendPoint,
} from "../api/analytics";

import PriorityBadge from "../components/status/PriorityBadge";
import ErrorState from "../components/ui/ErrorState";
import LoadingState from "../components/ui/LoadingState";

function formatDate(date: string) {
  return new Date(`${date}T00:00:00`).toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
  });
}

function distributionToData(distribution: Record<string, number>) {
  return Object.entries(distribution)
    .map(([name, value]) => ({
      name,
      value,
    }))
    .sort((a, b) => b.value - a.value);
}

export default function Analytics() {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [heatmap, setHeatmap] = useState<HeatmapPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadAnalytics() {
      try {
        setLoading(true);
        setError("");

        const [dashboardData, trendData, heatmapData] = await Promise.all([
          getDashboardAnalytics(),
          getIncidentTrends(),
          getIncidentHeatmap(),
        ]);

        setAnalytics(dashboardData);
        setTrends(trendData.trends);
        setHeatmap(heatmapData.incidents);
      } catch {
        setError("Unable to load analytics data.");
      } finally {
        setLoading(false);
      }
    }

    loadAnalytics();
  }, []);

  const priorityData = useMemo(() => {
    if (!analytics) return [];
    return distributionToData(analytics.priority_distribution);
  }, [analytics]);

  const severityData = useMemo(() => {
    if (!analytics) return [];
    return distributionToData(analytics.severity_distribution);
  }, [analytics]);

  const categoryData = useMemo(() => {
    if (!analytics) return [];
    return distributionToData(analytics.category_distribution);
  }, [analytics]);

  if (loading) {
    return <LoadingState message="Loading operational analytics..." />;
  }

  if (error || !analytics) {
    return (
      <ErrorState
        title="Analytics unavailable"
        message={error || "Unable to load analytics data."}
      />
    );
  }

  const confidenceCards = [
    {
      label: "Avg. Severity Confidence",
      value: analytics.average_severity_confidence,
    },
    {
      label: "Avg. Category Confidence",
      value: analytics.average_category_confidence,
    },
  ];

  return (
    <div className="analytics-page">
      <header className="analytics-header">
        <div>
          <p className="eyebrow">OPERATIONAL ANALYTICS</p>
          <h1>Analytics</h1>
          <p>
            Analyze incident volume, priority, AI classifications and response
            trends.
          </p>
        </div>
      </header>

      <section className="analytics-kpi-grid">
        <div className="analytics-kpi">
          <span>Total Incidents</span>
          <strong>{analytics.total_incidents}</strong>
          <small>All recorded incidents</small>
        </div>

        <div className="analytics-kpi">
          <span>Critical Priority</span>
          <strong>{analytics.priority_distribution.critical ?? 0}</strong>
          <small>Immediate response required</small>
        </div>

        <div className="analytics-kpi">
          <span>High Priority</span>
          <strong>{analytics.priority_distribution.high ?? 0}</strong>
          <small>Urgent response cases</small>
        </div>

        <div className="analytics-kpi">
          <span>AI Completed</span>
          <strong>{analytics.ai_status_distribution.completed ?? 0}</strong>
          <small>Successfully analyzed</small>
        </div>
      </section>

      <section className="analytics-chart-grid">
        <div className="analytics-panel analytics-panel-wide">
          <div className="analytics-panel-header">
            <div>
              <h2>Incident Volume</h2>
              <p>Daily incident count over time</p>
            </div>
          </div>

          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" tickFormatter={formatDate} />
                <YAxis allowDecimals={false} />
                <Tooltip
                  labelFormatter={(value) => formatDate(String(value))}
                />
                <Line
                  type="monotone"
                  dataKey="count"
                  name="Incidents"
                  stroke="#2563eb"
                  strokeWidth={3}
                  dot
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h2>Priority</h2>
              <p>Operational urgency</p>
            </div>
          </div>

          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={priorityData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" allowDecimals={false} />
                <YAxis type="category" dataKey="name" width={75} />
                <Tooltip />
                <Bar
                  dataKey="value"
                  name="Incidents"
                  fill="#2563eb"
                  radius={[0, 6, 6, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="analytics-chart-grid">
        <div className="analytics-panel">
          <div className="analytics-panel-header">
            <div>
              <h2>Severity</h2>
              <p>AI-predicted severity</p>
            </div>
          </div>

          <div className="analytics-list">
            {severityData.map((item) => (
              <div className="analytics-list-row" key={item.name}>
                <span>{item.name}</span>
                <strong>{item.value}</strong>
              </div>
            ))}
          </div>
        </div>

        <div className="analytics-panel analytics-panel-wide">
          <div className="analytics-panel-header">
            <div>
              <h2>Incident Categories</h2>
              <p>AI-classified categories</p>
            </div>
          </div>

          <div className="analytics-chart">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData.slice(0, 10)} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" allowDecimals={false} />
                <YAxis
                  type="category"
                  dataKey="name"
                  width={170}
                  tick={{ fontSize: 11 }}
                />
                <Tooltip />
                <Bar
                  dataKey="value"
                  name="Incidents"
                  fill="#7c3aed"
                  radius={[0, 6, 6, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

      <section className="analytics-panel">
        <div className="analytics-panel-header">
          <div>
            <h2>AI Confidence</h2>
            <p>Average model confidence across classified incidents</p>
          </div>
        </div>

        <div className="confidence-summary-grid">
          {confidenceCards.map((card) => {
            const percentage =
              card.value == null ? null : card.value * 100;

            return (
              <div className="confidence-summary-card" key={card.label}>
                <span>{card.label}</span>
                <strong>
                  {percentage == null ? "N/A" : `${percentage.toFixed(1)}%`}
                </strong>
                <div className="confidence-component-track">
                  <div
                    className="confidence-component-fill"
                    style={{
                      width:
                        percentage == null
                          ? "0%"
                          : `${Math.min(100, Math.max(0, percentage))}%`,
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="analytics-panel">
        <div className="analytics-panel-header">
          <div>
            <h2>Incident Heatmap Data</h2>
            <p>Geospatial incidents available for visualization</p>
          </div>
          <span className="analytics-count">
            {heatmap.length} locations
          </span>
        </div>

        <div className="heatmap-preview">
          {heatmap.length === 0 ? (
            <div className="heatmap-empty">
              No geolocated incidents available.
            </div>
          ) : (
            <div className="heatmap-grid">
              {heatmap.slice(0, 12).map((incident) => (
                <div className="heatmap-card" key={incident.id}>
                  <div>
                    <strong>#{incident.id}</strong>
                    <PriorityBadge priority={incident.priority} />
                  </div>
                  <span>{incident.category}</span>
                  <small>
                    {incident.latitude.toFixed(4)},{" "}
                    {incident.longitude.toFixed(4)}
                  </small>
                </div>
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
}