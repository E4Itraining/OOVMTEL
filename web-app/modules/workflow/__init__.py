"""
Workflow Automation Module for OOVMTEL
Auto-escalation, report generation, and scheduled tasks
"""

from .automation import (
    WorkflowEngine,
    WorkflowRule,
    WorkflowTrigger,
    WorkflowAction,
    get_workflow_engine,
)

__all__ = [
    "WorkflowEngine",
    "WorkflowRule",
    "WorkflowTrigger",
    "WorkflowAction",
    "get_workflow_engine",
]
