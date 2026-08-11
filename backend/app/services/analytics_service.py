from app.repositories.analytics_repository import AnalyticsRepository
from app.services.cache_service import CacheService


class AnalyticsService:
    def __init__(self, db):
        self.repo = AnalyticsRepository(db)

    def get_dashboard(self):
        cache_key = "dashboard"

        cached_data = CacheService.get(cache_key)
        if cached_data:
            return cached_data

        dashboard = {
            "total_incidents": self.repo.total_incidents(),
            "status_distribution": self.repo.incidents_by_status(),
            "severity_distribution": self.repo.incidents_by_severity(),
            "category_distribution": self.repo.incidents_by_category(),
        }

        CacheService.set(
            cache_key,
            dashboard,
            expire=300,
        )

        return dashboard

    def get_trends(self):
        cache_key = "trends"

        cached_data = CacheService.get(cache_key)
        if cached_data:
            return cached_data

        trends = self.repo.incident_trends()

        CacheService.set(
            cache_key,
            trends,
            expire=300,
        )

        return trends

    def get_heatmap(self):
        cache_key = "heatmap"

        cached_data = CacheService.get(cache_key)
        if cached_data:
            return cached_data

        heatmap = self.repo.incident_heatmap()

        CacheService.set(
            cache_key,
            heatmap,
            expire=300,
        )

        return heatmap