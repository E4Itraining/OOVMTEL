"""
Escalation Manager - Alert escalation and notification routing
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Awaitable
import uuid

from .models import (
    Alert,
    AlertSeverity,
    AlertState,
    EscalationLevel,
    NotificationChannel,
    NotificationConfig,
    EscalationConfig,
    DEFAULT_ESCALATION_DELAYS,
    SEVERITY_PRIORITY,
)

logger = logging.getLogger(__name__)


class EscalationPolicy:
    """
    Escalation policy for alerts.

    Defines who gets notified and when based on severity and time.
    """

    def __init__(self, config: EscalationConfig):
        self.config = config
        self._escalation_history: Dict[str, List[Dict]] = {}

    def get_current_level(self, alert: Alert) -> EscalationLevel:
        """Get current escalation level for an alert."""
        return alert.escalation_level

    def get_next_level(self, alert: Alert) -> Optional[EscalationLevel]:
        """Get next escalation level."""
        current = alert.escalation_level.value
        if current >= EscalationLevel.L5.value:
            return None
        return EscalationLevel(current + 1)

    def should_escalate(self, alert: Alert) -> bool:
        """Check if alert should be escalated."""
        if alert.state != AlertState.ACTIVE:
            return False

        if self.config.stop_on_acknowledge and alert.state == AlertState.ACKNOWLEDGED:
            return False

        if alert.escalation_count >= self.config.max_escalations:
            return False

        # Check time since last escalation
        delay_minutes = self._get_delay_for_level(
            alert.severity,
            alert.escalation_level
        )

        if alert.last_escalated_at:
            elapsed = (datetime.utcnow() - alert.last_escalated_at).total_seconds() / 60
            return elapsed >= delay_minutes

        # First escalation - check time since alert started
        elapsed = (datetime.utcnow() - alert.started_at).total_seconds() / 60
        return elapsed >= delay_minutes

    def _get_delay_for_level(
        self,
        severity: AlertSeverity,
        level: EscalationLevel
    ) -> int:
        """Get delay in minutes for escalation level."""
        # Check policy configuration first
        for level_config in self.config.levels:
            if level_config.get("level") == level.value:
                return level_config.get("delay_minutes", 15)

        # Fall back to defaults
        default_delays = DEFAULT_ESCALATION_DELAYS.get(severity, [30])
        level_idx = level.value - 1
        if level_idx < len(default_delays):
            return default_delays[level_idx]
        return default_delays[-1] if default_delays else 30

    def get_recipients_for_level(
        self,
        level: EscalationLevel
    ) -> List[Dict[str, Any]]:
        """Get notification recipients for escalation level."""
        for level_config in self.config.levels:
            if level_config.get("level") == level.value:
                return [{
                    "recipients": level_config.get("recipients", []),
                    "channels": level_config.get("channels", [NotificationChannel.EMAIL]),
                }]
        return []

    def record_escalation(
        self,
        alert: Alert,
        to_level: EscalationLevel,
        notified: List[str]
    ) -> None:
        """Record an escalation event."""
        if alert.alert_id not in self._escalation_history:
            self._escalation_history[alert.alert_id] = []

        self._escalation_history[alert.alert_id].append({
            "from_level": alert.escalation_level.value,
            "to_level": to_level.value,
            "timestamp": datetime.utcnow().isoformat(),
            "notified": notified,
        })


class EscalationManager:
    """
    Alert escalation and notification manager.

    Features:
    - Multi-level escalation
    - Multiple notification channels
    - Quiet hours support
    - Rate limiting
    - Notification templates
    """

    def __init__(self):
        self._policies: Dict[str, EscalationPolicy] = {}
        self._notification_configs: Dict[str, NotificationConfig] = {}
        self._notification_handlers: Dict[NotificationChannel, Callable] = {}
        self._pending_escalations: Dict[str, datetime] = {}
        self._notification_history: List[Dict] = []
        self._running = False

        logger.info("Escalation Manager initialized")

    def add_policy(self, config: EscalationConfig) -> str:
        """Add an escalation policy."""
        policy = EscalationPolicy(config)
        self._policies[config.policy_id] = policy
        logger.info(f"Added escalation policy: {config.name}")
        return config.policy_id

    def add_notification_config(self, config: NotificationConfig) -> None:
        """Add notification channel configuration."""
        key = f"{config.channel.value}_{uuid.uuid4().hex[:8]}"
        self._notification_configs[key] = config
        logger.info(f"Added notification config for {config.channel.value}")

    def register_notification_handler(
        self,
        channel: NotificationChannel,
        handler: Callable[[Alert, List[str]], Awaitable[bool]]
    ) -> None:
        """Register a handler for a notification channel."""
        self._notification_handlers[channel] = handler
        logger.info(f"Registered handler for {channel.value}")

    async def process_alert(
        self,
        alert: Alert,
        policy_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process alert for escalation and notification.

        Returns:
            Dict with notification results
        """
        result = {
            "alert_id": alert.alert_id,
            "notifications_sent": [],
            "escalated": False,
            "new_level": None,
        }

        # Get applicable policy
        policy = self._get_policy(alert, policy_id)
        if not policy:
            # Use default notification
            await self._send_default_notification(alert)
            return result

        # Check if should escalate
        if policy.should_escalate(alert):
            next_level = policy.get_next_level(alert)
            if next_level:
                # Escalate
                old_level = alert.escalation_level
                alert.escalation_level = next_level
                alert.escalation_count += 1
                alert.last_escalated_at = datetime.utcnow()

                result["escalated"] = True
                result["new_level"] = next_level.value

                logger.info(
                    f"Escalated alert {alert.alert_id} from L{old_level.value} to L{next_level.value}"
                )

        # Send notifications for current level
        recipients_config = policy.get_recipients_for_level(alert.escalation_level)

        for config in recipients_config:
            for channel in config.get("channels", []):
                if isinstance(channel, str):
                    channel = NotificationChannel(channel)

                notifications = await self._send_notification(
                    alert,
                    channel,
                    config.get("recipients", [])
                )
                result["notifications_sent"].extend(notifications)

        # Record escalation
        if result["escalated"]:
            policy.record_escalation(
                alert,
                alert.escalation_level,
                [n["recipient"] for n in result["notifications_sent"]]
            )

        return result

    def _get_policy(
        self,
        alert: Alert,
        policy_id: Optional[str]
    ) -> Optional[EscalationPolicy]:
        """Get escalation policy for alert."""
        if policy_id and policy_id in self._policies:
            return self._policies[policy_id]

        # Find matching policy by severity
        for policy in self._policies.values():
            if policy.config.enabled:
                return policy

        return None

    async def _send_notification(
        self,
        alert: Alert,
        channel: NotificationChannel,
        recipients: List[str]
    ) -> List[Dict]:
        """Send notification through a channel."""
        results = []

        # Check quiet hours
        if self._is_quiet_hours(channel):
            logger.debug(f"Skipping {channel.value} notification - quiet hours")
            return results

        # Check rate limit
        if not self._check_rate_limit(channel):
            logger.warning(f"Rate limit exceeded for {channel.value}")
            return results

        # Get handler
        handler = self._notification_handlers.get(channel)

        for recipient in recipients:
            try:
                if handler:
                    success = await handler(alert, [recipient])
                else:
                    success = await self._default_notification_handler(
                        alert, channel, recipient
                    )

                result = {
                    "channel": channel.value,
                    "recipient": recipient,
                    "success": success,
                    "timestamp": datetime.utcnow().isoformat(),
                }
                results.append(result)

                # Record in history
                self._notification_history.append({
                    **result,
                    "alert_id": alert.alert_id,
                })

                if success:
                    alert.notifications_sent += 1
                    alert.last_notification_at = datetime.utcnow()

            except Exception as e:
                logger.error(f"Notification failed for {recipient}: {e}")
                results.append({
                    "channel": channel.value,
                    "recipient": recipient,
                    "success": False,
                    "error": str(e),
                })

        return results

    async def _default_notification_handler(
        self,
        alert: Alert,
        channel: NotificationChannel,
        recipient: str
    ) -> bool:
        """Default notification handler (logs only)."""
        message = self._format_notification(alert)

        logger.info(
            f"[{channel.value.upper()}] To: {recipient}\n"
            f"Subject: {alert.title}\n"
            f"Message: {message}"
        )

        # Simulate async operation
        await asyncio.sleep(0.1)
        return True

    async def _send_default_notification(self, alert: Alert) -> None:
        """Send notification using default channels."""
        # Find all enabled notification configs
        for config in self._notification_configs.values():
            if not config.enabled:
                continue

            # Check severity filter
            if SEVERITY_PRIORITY[alert.severity] > SEVERITY_PRIORITY[config.min_severity]:
                continue

            # Check rule filters
            if config.include_rules and alert.rule_id not in config.include_rules:
                continue
            if config.exclude_rules and alert.rule_id in config.exclude_rules:
                continue

            await self._send_notification(
                alert,
                config.channel,
                config.recipients
            )

    def _format_notification(self, alert: Alert) -> str:
        """Format alert for notification."""
        lines = [
            f"[{alert.severity.value.upper()}] {alert.title}",
            "",
            alert.message,
            "",
            f"Metric: {alert.metric}",
            f"Value: {alert.current_value}",
            f"Threshold: {alert.threshold_value}",
        ]

        if alert.equipment:
            lines.append(f"Equipment: {alert.equipment}")

        if alert.recommendations:
            lines.append("")
            lines.append("Recommendations:")
            for rec in alert.recommendations[:3]:
                lines.append(f"  - {rec}")

        lines.append("")
        lines.append(f"Alert ID: {alert.alert_id}")
        lines.append(f"Started: {alert.started_at.isoformat()}")

        return "\n".join(lines)

    def _is_quiet_hours(self, channel: NotificationChannel) -> bool:
        """Check if currently in quiet hours for channel."""
        now = datetime.utcnow()

        for config in self._notification_configs.values():
            if config.channel != channel:
                continue

            # Check quiet days
            day_name = now.strftime("%A")
            if day_name in config.quiet_days:
                return True

            # Check quiet hours
            if config.quiet_hours_start and config.quiet_hours_end:
                try:
                    start = datetime.strptime(config.quiet_hours_start, "%H:%M").time()
                    end = datetime.strptime(config.quiet_hours_end, "%H:%M").time()
                    current = now.time()

                    if start < end:
                        if start <= current <= end:
                            return True
                    else:
                        # Spans midnight
                        if current >= start or current <= end:
                            return True
                except ValueError:
                    pass

        return False

    def _check_rate_limit(self, channel: NotificationChannel) -> bool:
        """Check if under rate limit for channel."""
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)

        # Count recent notifications
        recent_count = sum(
            1 for n in self._notification_history
            if n.get("channel") == channel.value
            and datetime.fromisoformat(n["timestamp"]) > one_hour_ago
        )

        # Find limit
        for config in self._notification_configs.values():
            if config.channel == channel:
                return recent_count < config.max_notifications_per_hour

        return True  # No limit configured

    async def start(self) -> None:
        """Start escalation manager."""
        self._running = True
        asyncio.create_task(self._escalation_loop())
        logger.info("Escalation manager started")

    async def stop(self) -> None:
        """Stop escalation manager."""
        self._running = False
        logger.info("Escalation manager stopped")

    async def _escalation_loop(self) -> None:
        """Background loop for checking pending escalations."""
        while self._running:
            await asyncio.sleep(60)  # Check every minute

            # Check pending escalations
            now = datetime.utcnow()
            for alert_id, scheduled_at in list(self._pending_escalations.items()):
                if scheduled_at <= now:
                    del self._pending_escalations[alert_id]
                    # Trigger escalation check
                    logger.debug(f"Processing pending escalation for {alert_id}")

    def get_notification_history(
        self,
        limit: int = 100,
        alert_id: Optional[str] = None
    ) -> List[Dict]:
        """Get notification history."""
        history = self._notification_history

        if alert_id:
            history = [n for n in history if n.get("alert_id") == alert_id]

        return history[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Get escalation statistics."""
        now = datetime.utcnow()
        one_hour_ago = now - timedelta(hours=1)

        recent_notifications = [
            n for n in self._notification_history
            if datetime.fromisoformat(n["timestamp"]) > one_hour_ago
        ]

        return {
            "policies": len(self._policies),
            "notification_configs": len(self._notification_configs),
            "handlers_registered": len(self._notification_handlers),
            "pending_escalations": len(self._pending_escalations),
            "notifications_last_hour": len(recent_notifications),
            "notifications_by_channel": {
                channel.value: sum(
                    1 for n in recent_notifications
                    if n.get("channel") == channel.value
                )
                for channel in NotificationChannel
            },
        }
