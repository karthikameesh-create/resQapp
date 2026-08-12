import re


class PriorityService:

    @staticmethod
    def calculate_priority(
        severity: str,
        predicted_severity: str | None = None,
        severity_confidence: float | None = None,
        incident_type: str | None = None,
        description: str | None = None,
    ) -> str:

        score = 0.0

        # Normalize inputs
        ai_severity = (predicted_severity or "").lower()
        reported_severity = (severity or "").lower()
        incident_type_lower = (incident_type or "").lower()
        text = (description or "").lower()

        # -------------------------------------------------
        # 1. AI predicted severity - strongest signal
        # -------------------------------------------------
        if ai_severity == "critical":
            score += 5
        elif ai_severity == "high":
            score += 3
        elif ai_severity == "medium":
            score += 2
        elif ai_severity == "low":
            score += 1

        # -------------------------------------------------
        # 2. AI confidence - supporting signal
        # -------------------------------------------------
        if severity_confidence is not None:
            if severity_confidence >= 0.90:
                score += 1
            elif severity_confidence >= 0.75:
                score += 0.5

        # -------------------------------------------------
        # 3. Reported/manual severity - secondary signal
        # -------------------------------------------------
        if reported_severity == "critical":
            score += 3
        elif reported_severity == "high":
            score += 2
        elif reported_severity == "medium":
            score += 1

        # -------------------------------------------------
        # 4. Incident type
        # -------------------------------------------------
        critical_types = [
            "explosion",
            "building collapse",
            "earthquake",
        ]

        high_risk_types = [
            "fire",
            "medical",
            "accident",
            "traffic accident",
            "flood",
            "landslide",
            "chemical",
        ]

        if any(
            keyword in incident_type_lower
            for keyword in critical_types
        ):
            score += 2
        elif any(
            keyword in incident_type_lower
            for keyword in high_risk_types
        ):
            score += 1

        # -------------------------------------------------
        # 5. Emergency keywords
        # -------------------------------------------------
        critical_keywords = [
            "unconscious",
            "not breathing",
            "cardiac arrest",
            "multiple casualties",
            "mass casualty",
            "trapped",
            "severe bleeding",
            "critical condition",
        ]

        high_keywords = [
            "injured",
            "injury",
            "bleeding",
            "burn",
            "fracture",
            "hospital",
            "ambulance",
            "rescue",
        ]

        has_critical_keyword = any(
            keyword in text
            for keyword in critical_keywords
        )

        has_high_keyword = any(
            keyword in text
            for keyword in high_keywords
        )

        if has_critical_keyword:
            score += 3
        elif has_high_keyword:
            score += 1

        # -------------------------------------------------
        # 6. Casualty count
        # Only count numbers explicitly associated with
        # people/casualties/injuries.
        # -------------------------------------------------
        casualty_pattern = re.compile(
            r"\b(\d+)\b\s*"
            r"(?:people|persons|passengers|victims|casualties|"
            r"injured|injuries|patients)\b"
        )

        casualty_matches = casualty_pattern.findall(text)

        for number in casualty_matches:
            count = int(number)

            if count >= 10:
                score += 3
                break
            elif count >= 5:
                score += 2
                break
            elif count >= 2:
                score += 1
                break

        # -------------------------------------------------
        # 7. Safety guardrails
        # -------------------------------------------------
        minimum_priority = "low"

        # High-confidence critical AI prediction should
        # never be downgraded below high priority.
        if (
            ai_severity == "critical"
            and severity_confidence is not None
            and severity_confidence >= 0.90
        ):
            minimum_priority = "high"

        # A manually reported critical incident should
        # never fall below high priority.
        if reported_severity == "critical":
            minimum_priority = "high"

        # A manually reported high-severity incident
        # should never fall below high priority.
        if reported_severity == "high":
            minimum_priority = "high"

        # Critical emergency evidence should never be
        # treated as low/medium priority.
        if has_critical_keyword:
            minimum_priority = "high"

        # High-confidence high AI prediction should be
        # at least high priority.
        if (
            ai_severity == "high"
            and severity_confidence is not None
            and severity_confidence >= 0.90
        ):
            minimum_priority = "high"

        # -------------------------------------------------
        # 8. Convert score into priority
        # -------------------------------------------------
        if score >= 10:
            calculated_priority = "critical"
        elif score >= 7:
            calculated_priority = "high"
        elif score >= 4:
            calculated_priority = "medium"
        else:
            calculated_priority = "low"

        # -------------------------------------------------
        # 9. Apply minimum-priority guardrail
        # -------------------------------------------------
        priority_rank = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4,
        }

        if priority_rank[calculated_priority] < priority_rank[minimum_priority]:
            return minimum_priority

        return calculated_priority