"""
OOVMTEL Auto-Remediation Module

This module provides automatic remediation capabilities for industrial incidents.
It executes predefined runbooks to resolve common issues automatically.

Features:
- Runbook management and execution
- Approval workflow
- Action auditing
- Rollback capabilities
- Integration with monitoring
"""

from .engine import RemediationEngine
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
)
from .executor import ActionExecutor
from .runbook_library import RunbookLibrary

__all__ = [
    'RemediationEngine',
    'Runbook',
    'RunbookStep',
    'RemediationAction',
    'ActionStatus',
    'ActionResult',
    'ApprovalLevel',
    'ApprovalRequest',
    'AuditLog',
    'RemediationPlan',
    'ActionExecutor',
    'RunbookLibrary',
]
