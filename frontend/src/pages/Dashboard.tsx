import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  getDashboardAnalytics,
  getIncidentTrends,
  type DashboardAnalytics,
  type TrendPoint,
} from "../api/analytics";
import StatCard from "../components/dashboard/StatCard";
import ErrorState from "../components/ui/ErrorState";
import LoadingState from "../components/ui/LoadingState";

function distributionToData(distribution: Record<string, number>) {
  return Object.entries(distribution).map(([name, value]) => ({
    name,
    value,
  }));
}

function formatDate(date: string) {
  const parsed = new Date(`${date}T00:00:00`);
  return parsed.toLocaleDateString("en-IN", {
    day: "2-digit",
    month: "short",
  });
}

export default function Dashboard() {
  const [analytics, setAnalytics] = useState<DashboardAnalytics | null>(null);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      const [dashboardData, trendData] = await Promise.all([
        getDashboardAnalytics(),
        getIncidentTrends(),
      ]);

      setAnalytics(dashboardData);
      setTrends(trendData.trends);
    } catch {
      setError("Unable to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const severityData = useMemo(() => {
    if (!analytics) return [];

    return distributionToData(analytics.severity_distribution);
  }, [analytics]);

  const priorityData = useMemo(() => {
    if (!analytics) return [];

    return distributionToData(analytics.priority_distribution);
  }, [analytics]);

  const categoryData = useMemo(() => {
    if (!analytics) return [];

    return distributionToData(analytics.category_distribution);
  }, [analytics]);

  if (loading) {
    return (
      <LoadingState
        message="Loading ResQAI intelligence..."
      />
    );
  }

  if (error || !analytics) {
    return (
      <ErrorState
        title="Dashboard unavailable"
        message={
          error ||
          "Unable to load dashboard data."
        }
        onRetry={loadDashboard}
      />
    );
  }

  return (
    <div className="dashboard-page">
      <main className="dashboard-content">
        <section className="dashboard-intro">
          <div>
            <p className="eyebrow">OPERATIONS OVERVIEW</p>

            <h2>Emergency Intelligence Dashboard</h2>

            <p>
              Monitor incident activity, AI classifications and operational priority
              across the response system.
            </p>
          </div>
        </section>

        <section className="stats-grid">
          <StatCard
            label="Total Incidents"
            value={analytics.total_incidents}
            description="All recorded incidents"
          />

          <StatCard
            label="Critical"
            value={analytics.priority_distribution.critical ?? 0}
            description="Immediate attention"
          />

          <StatCard
            label="High Priority"
            value={analytics.priority_distribution.high ?? 0}
            description="Urgent response"
          />

          <StatCard
            label="AI Pending"
            value={analytics.ai_status_distribution.pending ?? 0}
            description="Awaiting analysis"
          />
        </section>

        <section className="dashboard-grid">
          <div className="panel panel-large">
            <div className="panel-header">
              <div>
                <h3>Incident Trends</h3>
                <p>Priority distribution over time</p>
              </div>
            </div>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trends}>
                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis dataKey="date" tickFormatter={formatDate} />

                  <YAxis allowDecimals={false} />

                  <Tooltip
                    labelFormatter={(value) => formatDate(String(value))}
                  />

                  <Legend />

                  <Bar
                    dataKey="critical_count"
                    name="Critical"
                    fill="#dc2626"
                    radius={[4, 4, 0, 0]}
                  />

                  <Bar
                    dataKey="high_count"
                    name="High"
                    fill="#ea580c"
                    radius={[4, 4, 0, 0]}
                  />

                  <Bar
                    dataKey="medium_count"
                    name="Medium"
                    fill="#ca8a04"
                    radius={[4, 4, 0, 0]}
                  />

                  <Bar
                    dataKey="low_count"
                    name="Low"
                    fill="#16a34a"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Priority Distribution</h3>
                <p>Current operational urgency</p>
              </div>
            </div>

            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={priorityData} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" />

                  <XAxis type="number" allowDecimals={false} />

                  <YAxis type="category" dataKey="name" width={70} />

                  <Tooltip />

                  <Bar
                    dataKey="value"
                    name="Incidents"
                    fill="#2563eb"
                    radius={[0, 5, 5, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="dashboard-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Severity Distribution</h3>
                <p>AI-predicted severity levels</p>
              </div>
            </div>

            <div className="distribution-list">
              {severityData.map((item) => (
                <div className="distribution-row" key={item.name}>
                  <span>{item.name}</span>
                  <strong>{item.value}</strong>
                </div>
              ))}
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h3>Top Incident Categories</h3>
                <p>AI-classified incident types</p>
              </div>
            </div>

            <div className="distribution-list">
              {categoryData
                .sort((a, b) => b.value - a.value)
                .slice(0, 6)
                .map((item) => (
                  <div className="distribution-row" key={item.name}>
                    <span>{item.name}</span>
                    <strong>{item.value}</strong>
                  </div>
                ))}
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h3>AI Processing Status</h3>
              <p>Current analysis pipeline</p>
            </div>
          </div>

          <div className="ai-status-grid">
            {Object.entries(analytics.ai_status_distribution).map(
              ([status, count]) => (
                <div className="ai-status-card" key={status}>
                  <span>{status}</span>
                  <strong>{count}</strong>
                </div>
              )
            )}
          </div>
        </section>
      </main>
    </div>
  );
}