"""
Alerting Engine - Main intelligent alerting engine
"""

import logging
import asyncio
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Awaitable

from .models import (
    Alert,
    AlertSeverity,
    AlertState,
    AlertType,
    AlertRule,
    ThresholdConfig,
    EscalationLevel,
    NotificationChannel,
    EscalationConfig,
    NotificationConfig,
    ALERT_TEMPLATES,
)
from .adaptive_thresholds import AdaptiveThresholdManager
from .deduplication import AlertDeduplicator
from .escalation import EscalationManager

logger = logging.getLogger(__name__)


class AlertingEngine:
    """
    Intelligent Alerting Engine for SYNAPSIX.

    Features:
    - Adaptive thresholds
    - Alert deduplication
    - Correlation detection
    - Multi-level escalation
    - Multi-channel notifications
    - Seasonal awareness
    - Context-rich alerts
    """

    def __init__(
        self,
        victoria_metrics_url: str = "http://victoria-metrics:8428",
        evaluation_interval_seconds: int = 60,
    ):
        self.victoria_metrics_url = victoria_metrics_url
        self.evaluation_interval_seconds = evaluation_interval_seconds

        # Components
        self.threshold_manager = AdaptiveThresholdManager()
        self.deduplicator = AlertDeduplicator()
        self.escalation_manager = EscalationManager()

        # Alert rules
        self._rules: Dict[str, AlertRule] = {}

        # Active alerts
        self._active_alerts: Dict[str, Alert] = {}

        # Alert history
        self._alert_history: List[Alert] = []

        # Callbacks
        self._on_alert_callbacks: List[Callable[[Alert], Awaitable[None]]] = []

        # Status
        self._running = False
        self._last_evaluation: Optional[datetime] = None

        logger.info("Alerting Engine initialized")

    async def start(self) -> None:
        """Start the alerting engine."""
        self._running = True
        await self.escalation_manager.start()
        asyncio.create_task(self._evaluation_loop())
        logger.info("Alerting Engine started")

    async def stop(self) -> None:
        """Stop the alerting engine."""
        self._running = False
        await self.escalation_manager.stop()
        logger.info("Alerting Engine stopped")

    # Rule Management

    def add_rule(self, rule: AlertRule) -> str:
        """Add an alert rule."""
        self._rules[rule.rule_id] = rule
        logger.info(f"Added alert rule: {rule.name} ({rule.rule_id})")
        return rule.rule_id

    def add_rule_from_template(
        self,
        template_name: str,
        equipment_filter: Optional[str] = None,
        **overrides
    ) -> Optional[str]:
        """Create rule from template."""
        if template_name not in ALERT_TEMPLATES:
            logger.error(f"Unknown template: {template_name}")
            return None

        template = ALERT_TEMPLATES[template_name]

        rule = AlertRule(
            rule_id=f"RULE-{uuid.uuid4().hex[:8]}",
            name=template["name"],
            metric=template["metric"],
            equipment_filter=equipment_filter,
            threshold=ThresholdConfig(**template.get("threshold", {})),
            **overrides
        )

        return self.add_rule(rule)

    def remove_rule(self, rule_id: str) -> bool:
        """Remove an alert rule."""
        if rule_id in self._rules:
            del self._rules[rule_id]
            logger.info(f"Removed alert rule: {rule_id}")
            return True
        return False

    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """Get a rule by ID."""
        return self._rules.get(rule_id)

    def get_all_rules(self) -> List[AlertRule]:
        """Get all rules."""
        return list(self._rules.values())

    def enable_rule(self, rule_id: str, enabled: bool = True) -> bool:
        """Enable or disable a rule."""
        if rule_id in self._rules:
            self._rules[rule_id].enabled = enabled
            return True
        return False

    # Alert Evaluation

    async def evaluate(
        self,
        metrics_data: Dict[str, Any]
    ) -> List[Alert]:
        """
        Evaluate metrics against all rules.

        Args:
            metrics_data: Current metrics data

        Returns:
            List of new or updated alerts
        """
        start_time = time.time()
        new_alerts = []

        for rule_id, rule in self._rules.items():
            if not rule.enabled:
                continue

            try:
                alerts = await self._evaluate_rule(rule, metrics_data)
                new_alerts.extend(alerts)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule_id}: {e}")

        self._last_evaluation = datetime.utcnow()

        # Check for resolution
        await self._check_resolutions(metrics_data)

        # Process escalations
        for alert in self._active_alerts.values():
            if alert.state == AlertState.ACTIVE:
                await self.escalation_manager.process_alert(alert)

        duration_ms = (time.time() - start_time) * 1000
        logger.debug(f"Alert evaluation completed in {duration_ms:.1f}ms, {len(new_alerts)} alerts")

        return new_alerts

    async def _evaluate_rule(
        self,
        rule: AlertRule,
        metrics_data: Dict[str, Any]
    ) -> List[Alert]:
        """Evaluate a single rule against metrics."""
        alerts = []

        # Extract relevant values
        values = self._extract_values(rule.metric, metrics_data, rule.equipment_filter)

        for equipment, value in values.items():
            # Update baseline
            self.threshold_manager.update_baseline(rule.metric, equipment, value)

            if rule.threshold.seasonal_enabled:
                self.threshold_manager.update_seasonal_pattern(rule.metric, equipment, value)

            # Check threshold
            result = self.threshold_manager.check_value(
                rule.metric,
                equipment,
                value,
                rule.threshold
            )

            # Check rate of change
            rate_result = self.threshold_manager.check_rate_of_change(
                rule.metric,
                equipment,
                value,
                rule.threshold
            )

            # Create alert if breached
            if result["breached"] or rate_result.get("breached"):
                alert = await self._create_alert(rule, equipment, value, result, rate_result)
                if alert:
                    alerts.append(alert)

        return alerts

    def _extract_values(
        self,
        metric: str,
        metrics_data: Dict[str, Any],
        equipment_filter: Optional[str]
    ) -> Dict[str, float]:
        """Extract metric values from data."""
        import re

        values = {}
        business = metrics_data.get("business", {})
        tech = metrics_data.get("tech", {})

        # Check business metrics
        if metric in business:
            values["global"] = business[metric]

        # Check equipment
        for eq in business.get("equipment", []):
            eq_name = eq.get("name", "")

            if equipment_filter:
                if not re.search(equipment_filter, eq_name):
                    continue

            # Map metric names to equipment fields
            metric_mapping = {
                "temperature": "temp",
                "vibration": "vibration",
                "power": "power",
                "pressure": "pressure",
            }

            field = metric_mapping.get(metric, metric)
            if field in eq:
                values[eq_name] = eq[field]

        # Check tech metrics
        if metric in tech:
            values["system"] = tech[metric]

        return values

    async def _create_alert(
        self,
        rule: AlertRule,
        equipment: str,
        value: float,
        threshold_result: Dict[str, Any],
        rate_result: Dict[str, Any]
    ) -> Optional[Alert]:
        """Create an alert from evaluation results."""
        severity = threshold_result.get("severity", AlertSeverity.MEDIUM)

        # Determine alert type
        if rate_result.get("breached"):
            alert_type = AlertType.TREND
            message = f"Rapid change detected: {rate_result.get('rate_per_minute', 0):.2f}/min"
        elif rule.threshold.adaptive_enabled:
            alert_type = AlertType.ANOMALY
            message = f"Anomaly detected: value {value} deviates from baseline"
        else:
            alert_type = AlertType.THRESHOLD
            message = f"Threshold breached: {value} {'>' if rule.threshold.comparison == 'greater_than' else '<'} {threshold_result['threshold']}"

        # Generate recommendations
        recommendations = self._generate_recommendations(rule, equipment, value, threshold_result)

        alert = Alert(
            alert_id=f"ALT-{uuid.uuid4().hex[:8]}",
            rule_id=rule.rule_id,
            rule_name=rule.name,
            severity=severity,
            alert_type=alert_type,
            metric=rule.metric,
            equipment=equipment if equipment != "global" and equipment != "system" else None,
            labels=rule.labels,
            current_value=value,
            threshold_value=threshold_result.get("threshold", 0),
            baseline_value=threshold_result.get("baseline_mean"),
            deviation_percent=threshold_result.get("deviation_percent"),
            title=f"{rule.name}: {equipment}",
            message=message,
            details={
                "warning_threshold": threshold_result.get("warning_threshold"),
                "critical_threshold": threshold_result.get("critical_threshold"),
                "baseline_std": threshold_result.get("baseline_std"),
                "rate_per_minute": rate_result.get("rate_per_minute"),
            },
            recommendations=recommendations,
        )

        # Process through deduplicator
        result = self.deduplicator.process_alert(alert)

        if result["action"] == "suppressed":
            logger.debug(f"Alert suppressed: {result.get('reason')}")
            return None

        if result["action"] == "deduplicated":
            # Update existing alert
            return result["alert"]

        # New alert
        self._active_alerts[alert.alert_id] = alert

        # Notify callbacks
        for callback in self._on_alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")

        # Send notifications
        await self.escalation_manager.process_alert(alert)

        return alert

    def _generate_recommendations(
        self,
        rule: AlertRule,
        equipment: str,
        value: float,
        result: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations for an alert."""
        recommendations = []

        metric = rule.metric.lower()

        if "temperature" in metric:
            recommendations.append("Vérifier le système de refroidissement")
            recommendations.append("Contrôler la charge de l'équipement")
            if value > 80:
                recommendations.append("Envisager un arrêt préventif si la température continue d'augmenter")

        elif "vibration" in metric:
            recommendations.append("Inspecter les fixations et supports")
            recommendations.append("Vérifier l'équilibrage et l'alignement")
            recommendations.append("Analyser le spectre vibratoire pour identifier la cause")

        elif "pressure" in metric:
            recommendations.append("Vérifier les vannes et régulateurs")
            recommendations.append("Contrôler les fuites potentielles")

        elif "oee" in metric or "performance" in metric:
            recommendations.append("Analyser les causes de pertes de performance")
            recommendations.append("Vérifier les micro-arrêts et ralentissements")

        # Generic recommendations
        if result.get("deviation_percent", 0) > 50:
            recommendations.append("Variation importante - investiguer la cause racine")

        return recommendations[:5]

    async def _check_resolutions(self, metrics_data: Dict[str, Any]) -> None:
        """Check if any active alerts should be resolved."""
        for alert_id, alert in list(self._active_alerts.items()):
            if alert.state != AlertState.ACTIVE:
                continue

            rule = self._rules.get(alert.rule_id)
            if not rule:
                continue

            # Get current value
            values = self._extract_values(rule.metric, metrics_data, rule.equipment_filter)
            equipment = alert.equipment or "global"

            if equipment not in values:
                continue

            current_value = values[equipment]

            # Check if still breaching (with hysteresis)
            result = self.threshold_manager.check_value(
                rule.metric,
                equipment,
                current_value,
                rule.threshold
            )

            still_alerting = self.threshold_manager.apply_hysteresis(
                True,
                current_value,
                alert.threshold_value,
                rule.threshold
            )

            if not result["breached"] and not still_alerting:
                # Resolve alert
                await self.resolve_alert(alert_id, "auto_resolved")

    # Alert Management

    async def resolve_alert(
        self,
        alert_id: str,
        resolved_by: str = "system"
    ) -> Optional[Alert]:
        """Resolve an alert."""
        if alert_id not in self._active_alerts:
            return None

        alert = self._active_alerts[alert_id]
        alert.state = AlertState.RESOLVED
        alert.resolved_at = datetime.utcnow()
        alert.duration_seconds = int(
            (alert.resolved_at - alert.started_at).total_seconds()
        )

        # Remove from active
        del self._active_alerts[alert_id]

        # Add to history
        self._alert_history.append(alert)

        # Update deduplicator
        self.deduplicator.resolve_alert(alert.fingerprint)

        logger.info(f"Alert resolved: {alert_id} (duration: {alert.duration_seconds}s)")

        # Send resolution notification if configured
        rule = self._rules.get(alert.rule_id)
        if rule and rule.notify_on_resolve:
            # Notification handled by escalation manager
            pass

        return alert

    async def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str
    ) -> Optional[Alert]:
        """Acknowledge an alert."""
        if alert_id not in self._active_alerts:
            return None

        alert = self._active_alerts[alert_id]
        alert.state = AlertState.ACKNOWLEDGED
        alert.acknowledged_at = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by

        logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
        return alert

    async def suppress_alerts(
        self,
        matchers: Dict[str, Any],
        reason: str,
        duration_minutes: int
    ) -> str:
        """Suppress matching alerts."""
        suppression_id = f"SUP-{uuid.uuid4().hex[:8]}"
        self.deduplicator.add_suppression(
            suppression_id,
            matchers,
            reason,
            duration_minutes
        )
        return suppression_id

    # Queries

    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        equipment: Optional[str] = None
    ) -> List[Alert]:
        """Get active alerts with optional filtering."""
        alerts = list(self._active_alerts.values())

        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        if equipment:
            alerts = [a for a in alerts if a.equipment == equipment]

        return sorted(alerts, key=lambda a: a.started_at, reverse=True)

    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get an alert by ID."""
        return self._active_alerts.get(alert_id)

    def get_alert_history(
        self,
        limit: int = 100,
        since: Optional[datetime] = None
    ) -> List[Alert]:
        """Get alert history."""
        history = self._alert_history

        if since:
            history = [a for a in history if a.started_at >= since]

        return history[-limit:]

    # Callbacks

    def on_alert(
        self,
        callback: Callable[[Alert], Awaitable[None]]
    ) -> None:
        """Register callback for new alerts."""
        self._on_alert_callbacks.append(callback)

    # Background Loop

    async def _evaluation_loop(self) -> None:
        """Background evaluation loop."""
        while self._running:
            await asyncio.sleep(self.evaluation_interval_seconds)
            # Note: Actual evaluation is triggered externally with metrics data

    # Statistics

    def get_stats(self) -> Dict[str, Any]:
        """Get alerting statistics."""
        active = list(self._active_alerts.values())

        return {
            "rules": {
                "total": len(self._rules),
                "enabled": len([r for r in self._rules.values() if r.enabled]),
            },
            "alerts": {
                "active": len(active),
                "by_severity": {
                    s.value: len([a for a in active if a.severity == s])
                    for s in AlertSeverity
                },
                "history_count": len(self._alert_history),
            },
            "deduplication": self.deduplicator.get_stats(),
            "escalation": self.escalation_manager.get_stats(),
            "last_evaluation": self._last_evaluation.isoformat() if self._last_evaluation else None,
        }

    async def get_summary(self) -> str:
        """Get human-readable alert summary."""
        active = self.get_active_alerts()

        lines = ["## Résumé des Alertes\n"]

        if not active:
            lines.append("Aucune alerte active.")
            return "\n".join(lines)

        # Count by severity
        critical = [a for a in active if a.severity == AlertSeverity.CRITICAL]
        high = [a for a in active if a.severity == AlertSeverity.HIGH]
        medium = [a for a in active if a.severity == AlertSeverity.MEDIUM]

        lines.append(f"**Alertes actives:** {len(active)}")
        if critical:
            lines.append(f"  - 🔴 Critiques: {len(critical)}")
        if high:
            lines.append(f"  - 🟠 Hautes: {len(high)}")
        if medium:
            lines.append(f"  - 🟡 Moyennes: {len(medium)}")

        lines.append("")

        # Top alerts
        lines.append("**Alertes prioritaires:**")
        for alert in active[:5]:
            duration = (datetime.utcnow() - alert.started_at).total_seconds() / 60
            lines.append(
                f"  - [{alert.severity.value.upper()}] {alert.title} "
                f"(depuis {duration:.0f} min)"
            )

        return "\n".join(lines)
