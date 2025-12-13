"""
Auto-Remediation Module Data Models
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from pydantic import BaseModel, Field


class ApprovalLevel(str, Enum):
    """Approval levels for remediation actions."""
    AUTO = "auto"                    # No approval needed
    SINGLE = "single"                # Single approver
    DOUBLE = "double"                # Two approvers required
    EMERGENCY = "emergency"          # Bypass approval (logged)


class ActionStatus(str, Enum):
    """Status of a remediation action."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class StepType(str, Enum):
    """Types of runbook steps."""
    COMMAND = "command"              # Shell command
    API_CALL = "api_call"            # REST API call
    SCRIPT = "script"                # Python script
    WAIT = "wait"                    # Wait/delay
    CONDITION = "condition"          # Conditional check
    NOTIFICATION = "notification"    # Send notification
    MANUAL = "manual"                # Manual step (requires human)


class RunbookStep(BaseModel):
    """A single step in a runbook."""
    id: str
    name: str
    description: str = ""
    step_type: StepType
    sequence: int
    command: Optional[str] = None           # For COMMAND type
    api_endpoint: Optional[str] = None      # For API_CALL type
    api_method: str = "POST"
    api_payload: Optional[Dict[str, Any]] = None
    script: Optional[str] = None            # For SCRIPT type
    wait_seconds: int = 0                   # For WAIT type
    condition: Optional[str] = None         # For CONDITION type
    notification_channel: Optional[str] = None  # For NOTIFICATION
    timeout_seconds: int = 300
    retry_count: int = 0
    retry_delay_seconds: int = 30
    rollback_step_id: Optional[str] = None  # Step to execute on failure
    continue_on_failure: bool = False
    validation_command: Optional[str] = None  # Command to validate success


class Runbook(BaseModel):
    """A runbook defining remediation steps."""
    id: str
    name: str
    description: str
    category: str                       # restart, reconfigure, scale, etc.
    target_type: str                    # service, equipment, container, etc.
    trigger_conditions: List[str] = Field(default_factory=list)
    steps: List[RunbookStep] = Field(default_factory=list)
    approval_level: ApprovalLevel = ApprovalLevel.SINGLE
    estimated_duration_minutes: int = 5
    requires_downtime: bool = False
    risk_level: str = "low"             # low, medium, high
    tags: List[str] = Field(default_factory=list)
    version: str = "1.0"
    author: str = "system"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    success_rate: float = 0.0           # Historical success rate
    execution_count: int = 0


class ActionResult(BaseModel):
    """Result of executing a remediation action."""
    step_id: str
    step_name: str
    status: ActionStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: float = 0
    output: str = ""
    error: Optional[str] = None
    metrics_before: Dict[str, Any] = Field(default_factory=dict)
    metrics_after: Dict[str, Any] = Field(default_factory=dict)
    rollback_executed: bool = False


class ApprovalRequest(BaseModel):
    """Request for action approval."""
    id: str
    action_id: str
    runbook_id: str
    runbook_name: str
    requested_by: str = "system"
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    reason: str
    risk_summary: str
    approval_level: ApprovalLevel
    approvers_required: int = 1
    approvers: List[str] = Field(default_factory=list)
    approved_by: List[str] = Field(default_factory=list)
    rejected_by: Optional[str] = None
    status: str = "pending"             # pending, approved, rejected, expired
    notes: str = ""


class AuditLog(BaseModel):
    """Audit log entry for remediation actions."""
    id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    action_id: str
    runbook_id: str
    event_type: str                     # started, step_completed, approved, etc.
    actor: str                          # user or system
    details: Dict[str, Any] = Field(default_factory=dict)
    target: str = ""                    # What was affected
    result: Optional[str] = None


class RemediationAction(BaseModel):
    """A remediation action instance."""
    id: str
    incident_id: Optional[str] = None
    runbook_id: str
    runbook_name: str
    target: str                         # What we're remediating
    status: ActionStatus = ActionStatus.PENDING
    approval_request: Optional[ApprovalRequest] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    triggered_by: str = "system"        # system, user, schedule
    trigger_reason: str = ""
    steps_completed: int = 0
    total_steps: int = 0
    results: List[ActionResult] = Field(default_factory=list)
    overall_success: bool = False
    rollback_available: bool = True
    metrics_snapshot: Dict[str, Any] = Field(default_factory=dict)
    audit_log: List[AuditLog] = Field(default_factory=list)


class RemediationPlan(BaseModel):
    """A plan containing multiple remediation actions."""
    id: str
    name: str
    description: str
    incident_id: Optional[str] = None
    actions: List[RemediationAction] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "draft"               # draft, approved, executing, completed
    estimated_duration_minutes: int = 0
    requires_downtime: bool = False
    overall_risk: str = "low"


# Pre-defined runbook templates
RUNBOOK_TEMPLATES = {
    "restart_service": Runbook(
        id="RB-RESTART-001",
        name="Restart Service",
        description="Safely restart a service with health verification",
        category="restart",
        target_type="service",
        trigger_conditions=["high_cpu", "memory_leak", "service_unresponsive"],
        approval_level=ApprovalLevel.SINGLE,
        estimated_duration_minutes=5,
        requires_downtime=True,
        risk_level="low",
        tags=["service", "restart", "common"],
        success_rate=0.95,
        steps=[
            RunbookStep(
                id="step-1",
                name="Notify stakeholders",
                description="Send notification about planned restart",
                step_type=StepType.NOTIFICATION,
                sequence=1,
                notification_channel="slack",
                timeout_seconds=30
            ),
            RunbookStep(
                id="step-2",
                name="Check current service status",
                description="Verify service is running before restart",
                step_type=StepType.COMMAND,
                sequence=2,
                command="systemctl status {service_name}",
                timeout_seconds=30
            ),
            RunbookStep(
                id="step-3",
                name="Graceful stop",
                description="Stop the service gracefully",
                step_type=StepType.COMMAND,
                sequence=3,
                command="systemctl stop {service_name}",
                timeout_seconds=60,
                retry_count=2
            ),
            RunbookStep(
                id="step-4",
                name="Wait for cleanup",
                description="Wait for resources to be released",
                step_type=StepType.WAIT,
                sequence=4,
                wait_seconds=10
            ),
            RunbookStep(
                id="step-5",
                name="Start service",
                description="Start the service",
                step_type=StepType.COMMAND,
                sequence=5,
                command="systemctl start {service_name}",
                timeout_seconds=60,
                retry_count=3,
                retry_delay_seconds=10
            ),
            RunbookStep(
                id="step-6",
                name="Verify health",
                description="Verify service is healthy",
                step_type=StepType.COMMAND,
                sequence=6,
                command="curl -sf http://localhost:{port}/health",
                timeout_seconds=60,
                validation_command="echo $? -eq 0"
            ),
            RunbookStep(
                id="step-7",
                name="Notify completion",
                description="Send completion notification",
                step_type=StepType.NOTIFICATION,
                sequence=7,
                notification_channel="slack"
            )
        ]
    ),
    "clear_cache": Runbook(
        id="RB-CACHE-001",
        name="Clear Application Cache",
        description="Clear application caches to free memory",
        category="maintenance",
        target_type="application",
        trigger_conditions=["high_memory", "cache_overflow"],
        approval_level=ApprovalLevel.AUTO,
        estimated_duration_minutes=2,
        requires_downtime=False,
        risk_level="low",
        tags=["cache", "memory", "common"],
        success_rate=0.98,
        steps=[
            RunbookStep(
                id="step-1",
                name="Check current memory",
                description="Record current memory usage",
                step_type=StepType.COMMAND,
                sequence=1,
                command="free -m",
                timeout_seconds=10
            ),
            RunbookStep(
                id="step-2",
                name="Clear cache via API",
                description="Call cache clear endpoint",
                step_type=StepType.API_CALL,
                sequence=2,
                api_endpoint="http://localhost:{port}/admin/cache/clear",
                api_method="POST",
                timeout_seconds=30
            ),
            RunbookStep(
                id="step-3",
                name="Verify memory freed",
                description="Check memory was freed",
                step_type=StepType.COMMAND,
                sequence=3,
                command="free -m",
                timeout_seconds=10
            )
        ]
    ),
    "scale_container": Runbook(
        id="RB-SCALE-001",
        name="Scale Container Replicas",
        description="Scale container replicas up or down",
        category="scale",
        target_type="container",
        trigger_conditions=["high_load", "low_load"],
        approval_level=ApprovalLevel.SINGLE,
        estimated_duration_minutes=3,
        requires_downtime=False,
        risk_level="medium",
        tags=["scale", "container", "kubernetes"],
        success_rate=0.92,
        steps=[
            RunbookStep(
                id="step-1",
                name="Check current replicas",
                description="Get current replica count",
                step_type=StepType.COMMAND,
                sequence=1,
                command="docker-compose ps {service_name}",
                timeout_seconds=30
            ),
            RunbookStep(
                id="step-2",
                name="Scale replicas",
                description="Scale to target count",
                step_type=StepType.COMMAND,
                sequence=2,
                command="docker-compose up -d --scale {service_name}={replicas}",
                timeout_seconds=120
            ),
            RunbookStep(
                id="step-3",
                name="Wait for stabilization",
                description="Wait for new replicas to be ready",
                step_type=StepType.WAIT,
                sequence=3,
                wait_seconds=30
            ),
            RunbookStep(
                id="step-4",
                name="Verify scaling",
                description="Verify correct number of replicas",
                step_type=StepType.COMMAND,
                sequence=4,
                command="docker-compose ps {service_name} | grep -c Running",
                timeout_seconds=30
            )
        ]
    ),
    "recalibrate_sensor": Runbook(
        id="RB-CALIBRATE-001",
        name="Recalibrate Sensor",
        description="Recalibrate industrial sensor",
        category="maintenance",
        target_type="equipment",
        trigger_conditions=["sensor_drift", "calibration_due"],
        approval_level=ApprovalLevel.SINGLE,
        estimated_duration_minutes=15,
        requires_downtime=True,
        risk_level="medium",
        tags=["sensor", "calibration", "maintenance"],
        success_rate=0.88,
        steps=[
            RunbookStep(
                id="step-1",
                name="Notify operator",
                description="Alert operator about calibration",
                step_type=StepType.NOTIFICATION,
                sequence=1,
                notification_channel="operator_panel"
            ),
            RunbookStep(
                id="step-2",
                name="Record current readings",
                description="Log current sensor values",
                step_type=StepType.COMMAND,
                sequence=2,
                command="read_sensor {sensor_id}",
                timeout_seconds=30
            ),
            RunbookStep(
                id="step-3",
                name="Manual calibration step",
                description="Operator must perform physical calibration",
                step_type=StepType.MANUAL,
                sequence=3,
                timeout_seconds=600
            ),
            RunbookStep(
                id="step-4",
                name="Verify calibration",
                description="Verify sensor readings are within spec",
                step_type=StepType.COMMAND,
                sequence=4,
                command="verify_sensor_calibration {sensor_id}",
                timeout_seconds=60
            ),
            RunbookStep(
                id="step-5",
                name="Update calibration record",
                description="Log calibration in maintenance system",
                step_type=StepType.API_CALL,
                sequence=5,
                api_endpoint="http://mes/api/calibration",
                api_method="POST",
                api_payload={"sensor_id": "{sensor_id}", "calibrated_at": "{timestamp}"}
            )
        ]
    ),
    "failover_database": Runbook(
        id="RB-FAILOVER-001",
        name="Database Failover",
        description="Failover to standby database",
        category="failover",
        target_type="database",
        trigger_conditions=["primary_failure", "primary_unresponsive"],
        approval_level=ApprovalLevel.DOUBLE,
        estimated_duration_minutes=10,
        requires_downtime=True,
        risk_level="high",
        tags=["database", "failover", "critical"],
        success_rate=0.90,
        steps=[
            RunbookStep(
                id="step-1",
                name="Verify primary is down",
                description="Confirm primary database is unresponsive",
                step_type=StepType.COMMAND,
                sequence=1,
                command="pg_isready -h {primary_host}",
                timeout_seconds=30
            ),
            RunbookStep(
                id="step-2",
                name="Check standby status",
                description="Verify standby is ready for promotion",
                step_type=StepType.COMMAND,
                sequence=2,
                command="pg_isready -h {standby_host}",
                timeout_seconds=30
            ),
            RunbookStep(
                id="step-3",
                name="Promote standby",
                description="Promote standby to primary",
                step_type=StepType.COMMAND,
                sequence=3,
                command="pg_ctl promote -D {data_dir}",
                timeout_seconds=120
            ),
            RunbookStep(
                id="step-4",
                name="Update DNS/connection strings",
                description="Point applications to new primary",
                step_type=StepType.API_CALL,
                sequence=4,
                api_endpoint="http://config-server/api/database/failover",
                api_method="POST",
                timeout_seconds=60
            ),
            RunbookStep(
                id="step-5",
                name="Verify applications connected",
                description="Verify applications reconnected successfully",
                step_type=StepType.COMMAND,
                sequence=5,
                command="check_app_connections",
                timeout_seconds=120
            ),
            RunbookStep(
                id="step-6",
                name="Alert operations team",
                description="Notify team of completed failover",
                step_type=StepType.NOTIFICATION,
                sequence=6,
                notification_channel="ops_critical"
            )
        ]
    )
}
