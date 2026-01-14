"""
Workflow Automation Engine for OOVMTEL
Supports auto-escalation, scheduled reports, and event-driven workflows
"""

import asyncio
import logging
import smtplib
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


class TriggerType(str, Enum):
    """Types of workflow triggers."""
    ALERT = "alert"
    SCHEDULE = "schedule"
    THRESHOLD = "threshold"
    EVENT = "event"
    MANUAL = "manual"


class ActionType(str, Enum):
    """Types of workflow actions."""
    EMAIL = "email"
    WEBHOOK = "webhook"
    ESCALATE = "escalate"
    CREATE_TICKET = "create_ticket"
    RUN_SCRIPT = "run_script"
    LOG = "log"
    REMEDIATE = "remediate"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowTrigger:
    """Workflow trigger configuration."""
    type: TriggerType
    condition: Dict[str, Any]
    schedule: Optional[str] = None  # Cron expression for scheduled triggers
    debounce_seconds: int = 60  # Minimum time between triggers


@dataclass
class WorkflowAction:
    """Workflow action configuration."""
    type: ActionType
    config: Dict[str, Any]
    on_failure: Optional[str] = None  # Action ID to run on failure
    retry_count: int = 0
    retry_delay_seconds: int = 30


@dataclass
class WorkflowRule:
    """A workflow automation rule."""
    id: str
    name: str
    description: str
    enabled: bool
    triggers: List[WorkflowTrigger]
    actions: List[WorkflowAction]
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_triggered: Optional[datetime] = None
    execution_count: int = 0


@dataclass
class WorkflowExecution:
    """Record of a workflow execution."""
    id: str
    rule_id: str
    rule_name: str
    trigger_type: TriggerType
    status: WorkflowStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    results: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None


class WorkflowEngine:
    """
    Workflow automation engine.
    Handles event-driven and scheduled workflow execution.
    """

    def __init__(self):
        self.rules: Dict[str, WorkflowRule] = {}
        self.executions: List[WorkflowExecution] = []
        self._scheduler = None
        self._running = False
        self._action_handlers: Dict[ActionType, Callable] = {}
        self._initialize_default_rules()
        self._register_action_handlers()

    def _initialize_default_rules(self):
        """Initialize default automation rules."""
        # Auto-escalation rule
        self.add_rule(WorkflowRule(
            id="auto-escalation-critical",
            name="Critical Alert Auto-Escalation",
            description="Escalate unacknowledged critical alerts after 15 minutes",
            enabled=True,
            triggers=[
                WorkflowTrigger(
                    type=TriggerType.ALERT,
                    condition={
                        "severity": "critical",
                        "acknowledged": False,
                        "age_minutes": 15
                    }
                )
            ],
            actions=[
                WorkflowAction(
                    type=ActionType.EMAIL,
                    config={
                        "to": ["supervisor@oovmtel.local"],
                        "subject": "ESCALATION: Unacknowledged Critical Alert",
                        "template": "escalation"
                    }
                ),
                WorkflowAction(
                    type=ActionType.LOG,
                    config={"level": "warning", "message": "Alert escalated to supervisor"}
                )
            ]
        ))

        # Daily report rule
        self.add_rule(WorkflowRule(
            id="daily-report",
            name="Daily Operations Report",
            description="Generate and email daily operations report at 6 AM",
            enabled=True,
            triggers=[
                WorkflowTrigger(
                    type=TriggerType.SCHEDULE,
                    condition={},
                    schedule="0 6 * * *"
                )
            ],
            actions=[
                WorkflowAction(
                    type=ActionType.EMAIL,
                    config={
                        "to": ["operations@oovmtel.local"],
                        "subject": "Daily Operations Report - {date}",
                        "template": "daily_report",
                        "include_metrics": True
                    }
                )
            ]
        ))

        # Maintenance prediction rule
        self.add_rule(WorkflowRule(
            id="maintenance-prediction",
            name="Predictive Maintenance Notification",
            description="Notify when equipment RUL is below threshold",
            enabled=True,
            triggers=[
                WorkflowTrigger(
                    type=TriggerType.THRESHOLD,
                    condition={
                        "metric": "equipment_rul_days",
                        "operator": "lt",
                        "value": 7
                    }
                )
            ],
            actions=[
                WorkflowAction(
                    type=ActionType.CREATE_TICKET,
                    config={
                        "type": "maintenance",
                        "priority": "high",
                        "template": "maintenance_required"
                    }
                ),
                WorkflowAction(
                    type=ActionType.EMAIL,
                    config={
                        "to": ["maintenance@oovmtel.local"],
                        "subject": "Maintenance Required: {equipment}",
                        "template": "maintenance_alert"
                    }
                )
            ]
        ))

        # Capacity planning rule
        self.add_rule(WorkflowRule(
            id="capacity-alert",
            name="Capacity Utilization Alert",
            description="Alert when resource utilization exceeds 80%",
            enabled=True,
            triggers=[
                WorkflowTrigger(
                    type=TriggerType.THRESHOLD,
                    condition={
                        "metric": "resource_utilization",
                        "operator": "gt",
                        "value": 80
                    }
                )
            ],
            actions=[
                WorkflowAction(
                    type=ActionType.EMAIL,
                    config={
                        "to": ["operations@oovmtel.local"],
                        "subject": "High Resource Utilization Alert",
                        "template": "capacity_alert"
                    }
                )
            ]
        ))

    def _register_action_handlers(self):
        """Register action handlers."""
        self._action_handlers = {
            ActionType.EMAIL: self._handle_email_action,
            ActionType.WEBHOOK: self._handle_webhook_action,
            ActionType.ESCALATE: self._handle_escalate_action,
            ActionType.CREATE_TICKET: self._handle_create_ticket_action,
            ActionType.LOG: self._handle_log_action,
            ActionType.REMEDIATE: self._handle_remediate_action,
        }

    def add_rule(self, rule: WorkflowRule) -> WorkflowRule:
        """Add a workflow rule."""
        self.rules[rule.id] = rule
        return rule

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a workflow rule."""
        if rule_id in self.rules:
            del self.rules[rule_id]
            return True
        return False

    def get_rule(self, rule_id: str) -> Optional[WorkflowRule]:
        """Get a workflow rule by ID."""
        return self.rules.get(rule_id)

    def list_rules(self, enabled_only: bool = False) -> List[WorkflowRule]:
        """List all workflow rules."""
        rules = list(self.rules.values())
        if enabled_only:
            rules = [r for r in rules if r.enabled]
        return rules

    async def trigger_event(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> List[WorkflowExecution]:
        """Trigger workflows based on an event."""
        executions = []

        for rule in self.list_rules(enabled_only=True):
            for trigger in rule.triggers:
                if self._matches_trigger(trigger, event_type, event_data):
                    execution = await self._execute_rule(rule, trigger, event_data)
                    executions.append(execution)
                    break

        return executions

    def _matches_trigger(
        self,
        trigger: WorkflowTrigger,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        """Check if event matches trigger conditions."""
        if trigger.type == TriggerType.ALERT:
            if event_type != "alert":
                return False
            for key, value in trigger.condition.items():
                if event_data.get(key) != value:
                    return False
            return True

        elif trigger.type == TriggerType.THRESHOLD:
            if event_type != "metric":
                return False
            metric = trigger.condition.get("metric")
            operator = trigger.condition.get("operator")
            threshold = trigger.condition.get("value")
            actual = event_data.get(metric)

            if actual is None:
                return False

            if operator == "gt":
                return actual > threshold
            elif operator == "lt":
                return actual < threshold
            elif operator == "eq":
                return actual == threshold
            elif operator == "gte":
                return actual >= threshold
            elif operator == "lte":
                return actual <= threshold

        elif trigger.type == TriggerType.EVENT:
            return event_type == trigger.condition.get("event_name")

        return False

    async def _execute_rule(
        self,
        rule: WorkflowRule,
        trigger: WorkflowTrigger,
        context: Dict[str, Any]
    ) -> WorkflowExecution:
        """Execute a workflow rule."""
        execution = WorkflowExecution(
            id=str(uuid4()),
            rule_id=rule.id,
            rule_name=rule.name,
            trigger_type=trigger.type,
            status=WorkflowStatus.RUNNING,
            started_at=datetime.utcnow()
        )

        try:
            for action in rule.actions:
                result = await self._execute_action(action, context)
                execution.results.append(result)

            execution.status = WorkflowStatus.COMPLETED
            rule.execution_count += 1
            rule.last_triggered = datetime.utcnow()

        except Exception as e:
            execution.status = WorkflowStatus.FAILED
            execution.error = str(e)
            logger.error(f"Workflow execution failed: {e}")

        execution.completed_at = datetime.utcnow()
        self.executions.append(execution)

        # Keep only last 1000 executions
        if len(self.executions) > 1000:
            self.executions = self.executions[-1000:]

        return execution

    async def _execute_action(
        self,
        action: WorkflowAction,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single action."""
        handler = self._action_handlers.get(action.type)
        if not handler:
            return {"status": "skipped", "reason": f"No handler for {action.type}"}

        try:
            result = await handler(action.config, context)
            return {"status": "success", "action": action.type.value, "result": result}
        except Exception as e:
            return {"status": "error", "action": action.type.value, "error": str(e)}

    async def _handle_email_action(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle email action."""
        # In production, use aiosmtplib for async email
        to_addresses = config.get("to", [])
        subject = config.get("subject", "OOVMTEL Notification").format(**context)
        template = config.get("template", "default")

        body = self._render_email_template(template, context)

        logger.info(f"Email action: To={to_addresses}, Subject={subject}")

        # Simulate email sending (replace with actual SMTP in production)
        return {
            "sent_to": to_addresses,
            "subject": subject,
            "template": template,
            "simulated": True
        }

    async def _handle_webhook_action(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle webhook action."""
        import httpx

        url = config.get("url")
        method = config.get("method", "POST")
        headers = config.get("headers", {})

        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                json=context,
                headers=headers,
                timeout=30.0
            )

        return {
            "status_code": response.status_code,
            "url": url
        }

    async def _handle_escalate_action(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle escalation action."""
        escalation_level = config.get("level", 1)
        escalation_targets = config.get("targets", [])

        logger.warning(f"Escalation triggered: Level {escalation_level}")

        return {
            "level": escalation_level,
            "targets": escalation_targets,
            "context": context.get("alert_id")
        }

    async def _handle_create_ticket_action(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle ticket creation action."""
        ticket_type = config.get("type", "incident")
        priority = config.get("priority", "medium")

        ticket_id = f"TKT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        logger.info(f"Created ticket: {ticket_id} ({ticket_type}, {priority})")

        return {
            "ticket_id": ticket_id,
            "type": ticket_type,
            "priority": priority
        }

    async def _handle_log_action(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle log action."""
        level = config.get("level", "info")
        message = config.get("message", "Workflow action executed").format(**context)

        log_func = getattr(logger, level, logger.info)
        log_func(f"[Workflow] {message}")

        return {"level": level, "message": message}

    async def _handle_remediate_action(
        self,
        config: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle remediation action."""
        runbook_id = config.get("runbook_id")
        target = config.get("target")

        logger.info(f"Remediation requested: {runbook_id} on {target}")

        return {
            "runbook_id": runbook_id,
            "target": target,
            "status": "queued"
        }

    def _render_email_template(
        self,
        template: str,
        context: Dict[str, Any]
    ) -> str:
        """Render email template."""
        templates = {
            "escalation": """
ALERT ESCALATION NOTICE

This alert has not been acknowledged within the required timeframe.

Alert Details:
- ID: {alert_id}
- Severity: {severity}
- Message: {message}
- Time: {timestamp}

Please review and take appropriate action immediately.

---
OOVMTEL Workflow Automation
            """,
            "daily_report": """
DAILY OPERATIONS REPORT
Date: {date}

=== Production Summary ===
Total Production: {production_count} units
OEE: {oee}%
Quality Rate: {quality_rate}%

=== System Health ===
Services Status: All systems operational
Alerts: {alert_count} active alerts

=== Recommendations ===
{recommendations}

---
Generated by OOVMTEL Workflow Automation
            """,
            "maintenance_alert": """
MAINTENANCE REQUIRED

Equipment: {equipment}
Predicted Remaining Useful Life: {rul_days} days

Recommended Actions:
- Schedule preventive maintenance
- Review equipment history
- Prepare spare parts

---
OOVMTEL Predictive Maintenance
            """,
            "capacity_alert": """
CAPACITY ALERT

Resource utilization has exceeded the threshold.

Current Utilization: {utilization}%
Threshold: 80%

Recommended Actions:
- Review resource allocation
- Consider scaling resources
- Optimize workload distribution

---
OOVMTEL Workflow Automation
            """,
            "default": """
OOVMTEL NOTIFICATION

{message}

---
OOVMTEL Workflow Automation
            """
        }

        template_str = templates.get(template, templates["default"])
        try:
            return template_str.format(**context)
        except KeyError:
            return template_str

    def get_execution_history(
        self,
        limit: int = 100,
        rule_id: Optional[str] = None
    ) -> List[WorkflowExecution]:
        """Get workflow execution history."""
        executions = self.executions
        if rule_id:
            executions = [e for e in executions if e.rule_id == rule_id]
        return executions[-limit:]

    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow statistics."""
        total_rules = len(self.rules)
        enabled_rules = len([r for r in self.rules.values() if r.enabled])
        total_executions = len(self.executions)

        recent_executions = [
            e for e in self.executions
            if e.started_at > datetime.utcnow() - timedelta(hours=24)
        ]
        successful = len([e for e in recent_executions if e.status == WorkflowStatus.COMPLETED])
        failed = len([e for e in recent_executions if e.status == WorkflowStatus.FAILED])

        return {
            "total_rules": total_rules,
            "enabled_rules": enabled_rules,
            "total_executions": total_executions,
            "executions_24h": len(recent_executions),
            "successful_24h": successful,
            "failed_24h": failed,
            "success_rate": (successful / len(recent_executions) * 100) if recent_executions else 100
        }


# Global workflow engine instance
_workflow_engine: Optional[WorkflowEngine] = None


def get_workflow_engine() -> WorkflowEngine:
    """Get or create workflow engine instance."""
    global _workflow_engine
    if _workflow_engine is None:
        _workflow_engine = WorkflowEngine()
    return _workflow_engine
