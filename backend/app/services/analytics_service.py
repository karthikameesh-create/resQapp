from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, db):
        self.repo = AnalyticsRepository(db)

    def get_dashboard(self):
        return {
            "total_incidents": self.repo.total_incidents(),
            "status_distribution": self.repo.incidents_by_status(),
            "severity_distribution": self.repo.incidents_by_severity(),
            "category_distribution": self.repo.incidents_by_category(),
        }

    def get_trends(self):
        return self.repo.incident_trends()

    def get_heatmap(self):
        return self.repo.incident_heatmap()    