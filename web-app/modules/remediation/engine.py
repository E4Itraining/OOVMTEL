"""
Remediation Engine - Main auto-remediation engine
"""

import uuid
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from .models import (
    Runbook,
    RunbookStep,
    RemediationAction,
    ActionStatus,
    ActionResult,
    ApprovalLevel,
    ApprovalRequest,
    AuditLog,
    RemediationPlan,
    StepType,
    RUNBOOK_TEMPLATES,
)
from .executor import ActionExecutor
from .runbook_library import RunbookLibrary

logger = logging.getLogger(__name__)


class RemediationEngine:
    """
    Main Auto-Remediation Engine.

    Features:
    - Automatic incident remediation
    - Runbook execution with approval workflow
    - Action auditing and rollback
    - Multi-level approval
    - Dry-run mode
    """

    def __init__(
        self,
        dry_run: bool = False,
        auto_approve_low_risk: bool = True,
        max_concurrent_actions: int = 5,
    ):
        self.dry_run = dry_run
        self.auto_approve_low_risk = auto_approve_low_risk
        self.max_concurrent_actions = max_concurrent_actions

        self.executor = ActionExecutor(dry_run=dry_run)
        self.runbook_library = RunbookLibrary()

        # Active actions
        self.active_actions: Dict[str, RemediationAction] = {}
        self.pending_approvals: Dict[str, ApprovalRequest] = {}

        # Action history
        self.action_history: List[RemediationAction] = []

        logger.info(f"Remediation Engine initialized (dry_run={dry_run})")

    async def create_remediation_plan(
        self,
        incident_id: str,
        root_cause: str,
        affected_targets: List[str],
        context: Optional[Dict[str, Any]] = None
    ) -> RemediationPlan:
        """
        Create a remediation plan for an incident.

        Args:
            incident_id: ID of the incident
            root_cause: Identified root cause
            affected_targets: List of affected targets
            context: Additional context

        Returns:
            RemediationPlan with suggested actions
        """
        plan_id = f"PLAN-{uuid.uuid4().hex[:8].upper()}"

        # Find matching runbooks for the root cause
        matching_runbooks = self.runbook_library.find_runbooks_for_condition(root_cause)

        actions = []
        total_duration = 0
        requires_downtime = False
        max_risk = "low"

        for target in affected_targets:
            for runbook in matching_runbooks[:2]:  # Max 2 runbooks per target
                action = await self.create_action(
                    runbook_id=runbook.id,
                    target=target,
                    incident_id=incident_id,
                    context=context
                )
                actions.append(action)
                total_duration += runbook.estimated_duration_minutes

                if runbook.requires_downtime:
                    requires_downtime = True

                if runbook.risk_level == "high":
                    max_risk = "high"
                elif runbook.risk_level == "medium" and max_risk != "high":
                    max_risk = "medium"

        return RemediationPlan(
            id=plan_id,
            name=f"Remediation plan for {incident_id}",
            description=f"Auto-generated plan to address: {root_cause}",
            incident_id=incident_id,
            actions=actions,
            estimated_duration_minutes=total_duration,
            requires_downtime=requires_downtime,
            overall_risk=max_risk
        )

    async def create_action(
        self,
        runbook_id: str,
        target: str,
        incident_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        triggered_by: str = "system"
    ) -> RemediationAction:
        """Create a new remediation action."""
        runbook = self.runbook_library.get_runbook(runbook_id)
        if not runbook:
            raise ValueError(f"Runbook {runbook_id} not found")

        action_id = f"ACT-{uuid.uuid4().hex[:8].upper()}"

        action = RemediationAction(
            id=action_id,
            incident_id=incident_id,
            runbook_id=runbook_id,
            runbook_name=runbook.name,
            target=target,
            status=ActionStatus.PENDING,
            triggered_by=triggered_by,
            trigger_reason=f"Triggered for {target}",
            total_steps=len(runbook.steps),
            metrics_snapshot=context or {}
        )

        # Create approval request if needed
        if runbook.approval_level != ApprovalLevel.AUTO:
            approval = await self._create_approval_request(action, runbook)
            action.approval_request = approval
            self.pending_approvals[approval.id] = approval
        elif self.auto_approve_low_risk and runbook.risk_level == "low":
            action.status = ActionStatus.APPROVED

        # Log action creation
        self._add_audit_log(action, "created", "system", {
            "runbook": runbook_id,
            "target": target,
            "approval_level": runbook.approval_level.value
        })

        return action

    async def execute_action(
        self,
        action: RemediationAction,
        context: Optional[Dict[str, Any]] = None
    ) -> RemediationAction:
        """Execute a remediation action."""
        if action.status not in [ActionStatus.APPROVED, ActionStatus.PENDING]:
            if action.status == ActionStatus.PENDING and action.approval_request:
                raise ValueError(f"Action {action.id} requires approval")
            elif action.status != ActionStatus.APPROVED:
                raise ValueError(f"Action {action.id} cannot be executed (status: {action.status})")

        # Get runbook
        runbook = self.runbook_library.get_runbook(action.runbook_id)
        if not runbook:
            raise ValueError(f"Runbook {action.runbook_id} not found")

        # Check concurrent limit
        running_count = len([a for a in self.active_actions.values()
                           if a.status == ActionStatus.RUNNING])
        if running_count >= self.max_concurrent_actions:
            raise ValueError("Maximum concurrent actions reached")

        # Update status
        action.status = ActionStatus.RUNNING
        action.started_at = datetime.utcnow()
        self.active_actions[action.id] = action

        self._add_audit_log(action, "started", "system", {
            "steps": len(runbook.steps),
            "target": action.target
        })

        try:
            # Execute each step
            for step in sorted(runbook.steps, key=lambda s: s.sequence):
                result = await self.executor.execute_step(
                    step=step,
                    target=action.target,
                    context=context
                )

                action.results.append(result)
                action.steps_completed += 1

                self._add_audit_log(action, "step_completed", "system", {
                    "step_id": step.id,
                    "step_name": step.name,
                    "status": result.status.value
                })

                # Check for failure
                if result.status == ActionStatus.FAILED:
                    if not step.continue_on_failure:
                        # Attempt rollback if available
                        if step.rollback_step_id:
                            await self._execute_rollback(action, runbook, step)

                        action.status = ActionStatus.FAILED
                        action.overall_success = False
                        break

            # All steps completed successfully
            if action.status == ActionStatus.RUNNING:
                action.status = ActionStatus.SUCCESS
                action.overall_success = True

        except Exception as e:
            logger.error(f"Error executing action {action.id}: {e}")
            action.status = ActionStatus.FAILED
            action.overall_success = False

        finally:
            action.completed_at = datetime.utcnow()
            if action.id in self.active_actions:
                del self.active_actions[action.id]
            self.action_history.append(action)

            self._add_audit_log(action, "completed", "system", {
                "status": action.status.value,
                "success": action.overall_success,
                "steps_completed": action.steps_completed
            })

        return action

    async def approve_action(
        self,
        approval_id: str,
        approver: str,
        notes: str = ""
    ) -> ApprovalRequest:
        """Approve a pending action."""
        approval = self.pending_approvals.get(approval_id)
        if not approval:
            raise ValueError(f"Approval request {approval_id} not found")

        if approval.status != "pending":
            raise ValueError(f"Approval request already {approval.status}")

        # Check expiration
        if datetime.utcnow() > approval.expires_at:
            approval.status = "expired"
            raise ValueError("Approval request has expired")

        # Add approver
        approval.approved_by.append(approver)
        approval.notes = notes

        # Check if enough approvals
        if len(approval.approved_by) >= approval.approvers_required:
            approval.status = "approved"

            # Update action status
            action = next(
                (a for a in self.active_actions.values() if a.id == approval.action_id),
                None
            )
            if action:
                action.status = ActionStatus.APPROVED

        return approval

    async def reject_action(
        self,
        approval_id: str,
        rejector: str,
        reason: str
    ) -> ApprovalRequest:
        """Reject a pending action."""
        approval = self.pending_approvals.get(approval_id)
        if not approval:
            raise ValueError(f"Approval request {approval_id} not found")

        approval.status = "rejected"
        approval.rejected_by = rejector
        approval.notes = reason

        return approval

    async def rollback_action(self, action_id: str) -> RemediationAction:
        """Rollback a completed action."""
        action = next(
            (a for a in self.action_history if a.id == action_id),
            None
        )
        if not action:
            raise ValueError(f"Action {action_id} not found")

        if not action.rollback_available:
            raise ValueError(f"Action {action_id} does not support rollback")

        runbook = self.runbook_library.get_runbook(action.runbook_id)
        if not runbook:
            raise ValueError(f"Runbook {action.runbook_id} not found")

        self._add_audit_log(action, "rollback_started", "system", {})

        # Execute rollback steps in reverse order
        for result in reversed(action.results):
            step = next(
                (s for s in runbook.steps if s.id == result.step_id),
                None
            )
            if step and step.rollback_step_id:
                rollback_step = next(
                    (s for s in runbook.steps if s.id == step.rollback_step_id),
                    None
                )
                if rollback_step:
                    await self.executor.execute_step(
                        step=rollback_step,
                        target=action.target,
                        context={}
                    )

        action.status = ActionStatus.ROLLED_BACK
        self._add_audit_log(action, "rollback_completed", "system", {})

        return action

    async def _create_approval_request(
        self,
        action: RemediationAction,
        runbook: Runbook
    ) -> ApprovalRequest:
        """Create an approval request for an action."""
        approval_id = f"APR-{uuid.uuid4().hex[:8].upper()}"

        approvers_required = 1
        if runbook.approval_level == ApprovalLevel.DOUBLE:
            approvers_required = 2

        return ApprovalRequest(
            id=approval_id,
            action_id=action.id,
            runbook_id=runbook.id,
            runbook_name=runbook.name,
            expires_at=datetime.utcnow() + timedelta(hours=4),
            reason=f"Execute {runbook.name} on {action.target}",
            risk_summary=f"Risk level: {runbook.risk_level}, "
                        f"Downtime: {'Yes' if runbook.requires_downtime else 'No'}",
            approval_level=runbook.approval_level,
            approvers_required=approvers_required
        )

    async def _execute_rollback(
        self,
        action: RemediationAction,
        runbook: Runbook,
        failed_step: RunbookStep
    ):
        """Execute rollback for a failed step."""
        rollback_step = next(
            (s for s in runbook.steps if s.id == failed_step.rollback_step_id),
            None
        )
        if rollback_step:
            result = await self.executor.execute_step(
                step=rollback_step,
                target=action.target,
                context={}
            )
            result.rollback_executed = True
            action.results.append(result)

    def _add_audit_log(
        self,
        action: RemediationAction,
        event_type: str,
        actor: str,
        details: Dict[str, Any]
    ):
        """Add an audit log entry."""
        log = AuditLog(
            id=f"LOG-{uuid.uuid4().hex[:8].upper()}",
            action_id=action.id,
            runbook_id=action.runbook_id,
            event_type=event_type,
            actor=actor,
            details=details,
            target=action.target
        )
        action.audit_log.append(log)

    def get_action_status(self, action_id: str) -> Optional[RemediationAction]:
        """Get current status of an action."""
        # Check active actions
        if action_id in self.active_actions:
            return self.active_actions[action_id]

        # Check history
        return next(
            (a for a in self.action_history if a.id == action_id),
            None
        )

    def get_pending_approvals(self) -> List[ApprovalRequest]:
        """Get all pending approval requests."""
        return [a for a in self.pending_approvals.values() if a.status == "pending"]

    def get_action_history(
        self,
        limit: int = 100,
        status_filter: Optional[ActionStatus] = None
    ) -> List[RemediationAction]:
        """Get action history."""
        history = self.action_history

        if status_filter:
            history = [a for a in history if a.status == status_filter]

        return sorted(
            history,
            key=lambda a: a.created_at,
            reverse=True
        )[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get remediation statistics."""
        total = len(self.action_history)
        successful = len([a for a in self.action_history if a.overall_success])
        failed = len([a for a in self.action_history if a.status == ActionStatus.FAILED])

        return {
            "total_actions": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "active_actions": len(self.active_actions),
            "pending_approvals": len(self.get_pending_approvals()),
            "runbooks_available": self.runbook_library.count()
        }
