"""
Alert Deduplication - Prevent duplicate and related alerts
"""

import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict

from .models import (
    Alert,
    AlertSeverity,
    AlertState,
    AlertGroup,
    AlertCorrelation,
)

logger = logging.getLogger(__name__)


class AlertDeduplicator:
    """
    Alert deduplication and correlation.

    Features:
    - Fingerprint-based deduplication
    - Alert grouping by labels
    - Temporal correlation
    - Severity aggregation
    - Suppression management
    """

    def __init__(
        self,
        dedup_window_minutes: int = 60,
        group_wait_seconds: int = 30,
        correlation_window_seconds: int = 300,
    ):
        self.dedup_window_minutes = dedup_window_minutes
        self.group_wait_seconds = group_wait_seconds
        self.correlation_window_seconds = correlation_window_seconds

        # Active alerts by fingerprint
        self._active_alerts: Dict[str, Alert] = {}

        # Alert groups
        self._groups: Dict[str, AlertGroup] = {}

        # Correlations
        self._correlations: Dict[str, AlertCorrelation] = {}

        # Suppression rules
        self._suppressions: Dict[str, Dict[str, Any]] = {}

        # Recent alert history for correlation
        self._recent_alerts: List[Alert] = []

        logger.info("Alert Deduplicator initialized")

    def process_alert(self, alert: Alert) -> Dict[str, Any]:
        """
        Process an incoming alert for deduplication.

        Returns:
            Dict with: {
                action: "new" | "deduplicated" | "suppressed" | "grouped",
                alert: processed alert,
                group: optional group,
                correlation: optional correlation
            }
        """
        # 1. Check suppression
        if self._is_suppressed(alert):
            return {
                "action": "suppressed",
                "alert": alert,
                "reason": self._get_suppression_reason(alert),
            }

        # 2. Generate fingerprint
        fingerprint = self._generate_fingerprint(alert)
        alert.fingerprint = fingerprint

        # 3. Check for duplicate
        if fingerprint in self._active_alerts:
            existing = self._active_alerts[fingerprint]
            return self._handle_duplicate(existing, alert)

        # 4. Add to active alerts
        self._active_alerts[fingerprint] = alert
        self._recent_alerts.append(alert)
        self._cleanup_recent_alerts()

        # 5. Check for correlation with recent alerts
        correlation = self._find_correlation(alert)
        if correlation:
            self._correlations[correlation.correlation_id] = correlation

        # 6. Try to add to group
        group = self._find_or_create_group(alert)

        return {
            "action": "new",
            "alert": alert,
            "group": group,
            "correlation": correlation,
        }

    def _generate_fingerprint(self, alert: Alert) -> str:
        """Generate unique fingerprint for deduplication."""
        # Components that define uniqueness
        components = [
            alert.rule_id,
            alert.metric,
            alert.equipment or "",
            str(alert.severity.value),
        ]

        # Add relevant labels
        for key in sorted(alert.labels.keys()):
            components.append(f"{key}={alert.labels[key]}")

        fingerprint_str = "|".join(components)
        return hashlib.md5(fingerprint_str.encode()).hexdigest()

    def _handle_duplicate(
        self,
        existing: Alert,
        new: Alert
    ) -> Dict[str, Any]:
        """Handle duplicate alert."""
        # Update occurrence count
        existing.occurrence_count += 1
        existing.last_triggered_at = new.started_at

        # Update value if changed
        if new.current_value != existing.current_value:
            existing.current_value = new.current_value
            existing.details["value_history"] = existing.details.get("value_history", [])
            existing.details["value_history"].append({
                "value": new.current_value,
                "timestamp": new.started_at.isoformat(),
            })

        # Escalate severity if new is worse
        from .models import SEVERITY_PRIORITY
        if SEVERITY_PRIORITY[new.severity] < SEVERITY_PRIORITY[existing.severity]:
            existing.severity = new.severity
            existing.threshold_value = new.threshold_value

        logger.debug(f"Deduplicated alert: {existing.alert_id} (count: {existing.occurrence_count})")

        return {
            "action": "deduplicated",
            "alert": existing,
            "new_occurrence": new,
        }

    def _is_suppressed(self, alert: Alert) -> bool:
        """Check if alert should be suppressed."""
        now = datetime.utcnow()

        for sup_id, suppression in self._suppressions.items():
            if not suppression.get("active", True):
                continue

            # Check expiration
            if suppression.get("expires_at") and suppression["expires_at"] < now:
                suppression["active"] = False
                continue

            # Check matchers
            if self._matches_suppression(alert, suppression):
                return True

        return False

    def _matches_suppression(
        self,
        alert: Alert,
        suppression: Dict[str, Any]
    ) -> bool:
        """Check if alert matches suppression rule."""
        matchers = suppression.get("matchers", {})

        if "rule_id" in matchers:
            if alert.rule_id not in matchers["rule_id"]:
                return False

        if "equipment" in matchers:
            if alert.equipment not in matchers["equipment"]:
                return False

        if "severity" in matchers:
            if alert.severity.value not in matchers["severity"]:
                return False

        if "labels" in matchers:
            for key, values in matchers["labels"].items():
                if alert.labels.get(key) not in values:
                    return False

        return True

    def _get_suppression_reason(self, alert: Alert) -> str:
        """Get the reason for suppression."""
        for sup_id, suppression in self._suppressions.items():
            if self._matches_suppression(alert, suppression):
                return suppression.get("reason", "Suppressed by rule")
        return "Unknown"

    def _find_correlation(self, alert: Alert) -> Optional[AlertCorrelation]:
        """Find correlation with recent alerts."""
        cutoff = alert.started_at - timedelta(seconds=self.correlation_window_seconds)
        related_alerts = []

        for recent in self._recent_alerts:
            if recent.alert_id == alert.alert_id:
                continue
            if recent.started_at < cutoff:
                continue

            # Check for correlation criteria
            correlation_score = self._calculate_correlation_score(alert, recent)
            if correlation_score > 0.5:
                related_alerts.append((recent, correlation_score))

        if not related_alerts:
            return None

        # Create correlation
        import uuid
        correlation = AlertCorrelation(
            correlation_id=f"COR-{uuid.uuid4().hex[:8]}",
            name=f"Correlated alerts for {alert.metric}",
            alert_ids=[alert.alert_id] + [a.alert_id for a, _ in related_alerts],
            primary_alert_id=alert.alert_id,
            correlation_type="temporal",
            correlation_score=max(score for _, score in related_alerts),
            time_window_seconds=self.correlation_window_seconds,
        )

        # Try to identify root cause
        correlation.probable_root_cause = self._infer_root_cause(
            [alert] + [a for a, _ in related_alerts]
        )

        return correlation

    def _calculate_correlation_score(
        self,
        alert1: Alert,
        alert2: Alert
    ) -> float:
        """Calculate correlation score between two alerts."""
        score = 0.0

        # Same equipment
        if alert1.equipment and alert1.equipment == alert2.equipment:
            score += 0.4

        # Same location
        if alert1.location and alert1.location == alert2.location:
            score += 0.2

        # Related metrics
        related_metrics = {
            ("temperature", "vibration"): 0.3,
            ("temperature", "power"): 0.2,
            ("cpu_usage", "memory_usage"): 0.3,
            ("oee", "quality_rate"): 0.2,
        }
        metric_pair = tuple(sorted([alert1.metric, alert2.metric]))
        score += related_metrics.get(metric_pair, 0)

        # Temporal proximity
        time_diff = abs((alert1.started_at - alert2.started_at).total_seconds())
        if time_diff < 60:
            score += 0.3
        elif time_diff < 300:
            score += 0.1

        return min(score, 1.0)

    def _infer_root_cause(self, alerts: List[Alert]) -> Optional[str]:
        """Try to infer root cause from correlated alerts."""
        if not alerts:
            return None

        # Simple heuristics
        metrics = [a.metric for a in alerts]
        equipments = [a.equipment for a in alerts if a.equipment]

        # Temperature spike often causes other issues
        if "temperature" in metrics and len(metrics) > 1:
            temp_alert = next((a for a in alerts if a.metric == "temperature"), None)
            if temp_alert:
                return f"Probable root cause: Temperature anomaly on {temp_alert.equipment}"

        # Power issues cascade
        if "power" in metrics:
            return "Probable root cause: Power supply issue"

        # Single equipment with multiple alerts
        if len(set(equipments)) == 1 and equipments:
            return f"Multiple issues detected on {equipments[0]} - investigate equipment"

        return None

    def _find_or_create_group(self, alert: Alert) -> Optional[AlertGroup]:
        """Find or create alert group."""
        # Generate group key from labels
        group_key = self._generate_group_key(alert)
        if not group_key:
            return None

        if group_key in self._groups:
            group = self._groups[group_key]
            if alert.alert_id not in group.alert_ids:
                group.alert_ids.append(alert.alert_id)
                group.alert_count = len(group.alert_ids)
                group.last_alert_at = alert.started_at

                # Update group severity to highest
                from .models import SEVERITY_PRIORITY
                if SEVERITY_PRIORITY[alert.severity] < SEVERITY_PRIORITY[group.severity]:
                    group.severity = alert.severity

            return group

        # Create new group
        import uuid
        group = AlertGroup(
            group_id=f"GRP-{uuid.uuid4().hex[:8]}",
            name=f"Alert group: {group_key}",
            group_key=group_key,
            group_labels=alert.labels,
            alert_ids=[alert.alert_id],
            alert_count=1,
            severity=alert.severity,
        )

        self._groups[group_key] = group
        return group

    def _generate_group_key(self, alert: Alert) -> Optional[str]:
        """Generate group key from alert."""
        # Group by equipment and location
        components = []
        if alert.equipment:
            components.append(f"equipment={alert.equipment}")
        if alert.location:
            components.append(f"location={alert.location}")

        if not components:
            return None

        return "|".join(sorted(components))

    def resolve_alert(self, fingerprint: str) -> Optional[Alert]:
        """Mark an alert as resolved."""
        if fingerprint in self._active_alerts:
            alert = self._active_alerts[fingerprint]
            alert.state = AlertState.RESOLVED
            alert.resolved_at = datetime.utcnow()
            alert.duration_seconds = int(
                (alert.resolved_at - alert.started_at).total_seconds()
            )

            del self._active_alerts[fingerprint]

            # Update group
            for group in self._groups.values():
                if alert.alert_id in group.alert_ids:
                    group.alert_ids.remove(alert.alert_id)
                    group.alert_count = len(group.alert_ids)
                    if group.alert_count == 0:
                        group.state = AlertState.RESOLVED

            return alert

        return None

    def add_suppression(
        self,
        suppression_id: str,
        matchers: Dict[str, Any],
        reason: str,
        duration_minutes: Optional[int] = None,
    ) -> None:
        """Add a suppression rule."""
        suppression = {
            "matchers": matchers,
            "reason": reason,
            "active": True,
            "created_at": datetime.utcnow(),
        }

        if duration_minutes:
            suppression["expires_at"] = datetime.utcnow() + timedelta(minutes=duration_minutes)

        self._suppressions[suppression_id] = suppression
        logger.info(f"Added suppression: {suppression_id}")

    def remove_suppression(self, suppression_id: str) -> bool:
        """Remove a suppression rule."""
        if suppression_id in self._suppressions:
            del self._suppressions[suppression_id]
            return True
        return False

    def _cleanup_recent_alerts(self) -> None:
        """Clean up old alerts from recent list."""
        cutoff = datetime.utcnow() - timedelta(seconds=self.correlation_window_seconds * 2)
        self._recent_alerts = [
            a for a in self._recent_alerts
            if a.started_at > cutoff
        ]

    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return list(self._active_alerts.values())

    def get_groups(self) -> List[AlertGroup]:
        """Get all alert groups."""
        return list(self._groups.values())

    def get_correlations(self) -> List[AlertCorrelation]:
        """Get all correlations."""
        return list(self._correlations.values())

    def get_stats(self) -> Dict[str, Any]:
        """Get deduplication statistics."""
        return {
            "active_alerts": len(self._active_alerts),
            "groups": len(self._groups),
            "correlations": len(self._correlations),
            "suppressions": len([s for s in self._suppressions.values() if s.get("active")]),
            "recent_alerts": len(self._recent_alerts),
        }
