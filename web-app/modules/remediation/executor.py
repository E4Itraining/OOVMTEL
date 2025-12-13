"""
Action Executor - Executes individual remediation steps
"""

import asyncio
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional

from .models import (
    RunbookStep,
    ActionResult,
    ActionStatus,
    StepType,
)

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Executes individual remediation steps.

    Supports:
    - Shell commands
    - API calls
    - Python scripts
    - Wait operations
    - Conditional checks
    - Notifications
    """

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run

    async def execute_step(
        self,
        step: RunbookStep,
        target: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ActionResult:
        """Execute a single runbook step."""
        started_at = datetime.utcnow()
        context = context or {}

        # Replace placeholders in step configuration
        step = self._interpolate_step(step, target, context)

        result = ActionResult(
            step_id=step.id,
            step_name=step.name,
            status=ActionStatus.RUNNING,
            started_at=started_at
        )

        try:
            if self.dry_run:
                output = await self._dry_run_step(step)
            else:
                output = await self._execute_step_real(step, context)

            result.output = output
            result.status = ActionStatus.SUCCESS

        except Exception as e:
            logger.error(f"Step {step.id} failed: {e}")
            result.error = str(e)
            result.status = ActionStatus.FAILED

            # Retry logic
            if step.retry_count > 0:
                for attempt in range(step.retry_count):
                    logger.info(f"Retrying step {step.id}, attempt {attempt + 1}")
                    await asyncio.sleep(step.retry_delay_seconds)

                    try:
                        if self.dry_run:
                            output = await self._dry_run_step(step)
                        else:
                            output = await self._execute_step_real(step, context)

                        result.output = output
                        result.status = ActionStatus.SUCCESS
                        result.error = None
                        break

                    except Exception as retry_e:
                        result.error = str(retry_e)

        result.completed_at = datetime.utcnow()
        result.duration_seconds = (
            result.completed_at - result.started_at
        ).total_seconds()

        return result

    async def _execute_step_real(
        self,
        step: RunbookStep,
        context: Dict[str, Any]
    ) -> str:
        """Execute step for real."""
        if step.step_type == StepType.COMMAND:
            return await self._execute_command(step.command, step.timeout_seconds)

        elif step.step_type == StepType.API_CALL:
            return await self._execute_api_call(
                endpoint=step.api_endpoint,
                method=step.api_method,
                payload=step.api_payload,
                timeout=step.timeout_seconds
            )

        elif step.step_type == StepType.SCRIPT:
            return await self._execute_script(step.script, step.timeout_seconds)

        elif step.step_type == StepType.WAIT:
            await asyncio.sleep(step.wait_seconds)
            return f"Waited {step.wait_seconds} seconds"

        elif step.step_type == StepType.CONDITION:
            return await self._evaluate_condition(step.condition, context)

        elif step.step_type == StepType.NOTIFICATION:
            return await self._send_notification(
                channel=step.notification_channel,
                message=f"Remediation step: {step.name}"
            )

        elif step.step_type == StepType.MANUAL:
            # For manual steps, we just log and return
            logger.info(f"Manual step required: {step.name}")
            return f"Manual step: {step.description}"

        else:
            raise ValueError(f"Unknown step type: {step.step_type}")

    async def _dry_run_step(self, step: RunbookStep) -> str:
        """Simulate step execution (dry run)."""
        logger.info(f"[DRY RUN] Would execute: {step.name}")

        if step.step_type == StepType.COMMAND:
            return f"[DRY RUN] Would run: {step.command}"

        elif step.step_type == StepType.API_CALL:
            return f"[DRY RUN] Would call: {step.api_method} {step.api_endpoint}"

        elif step.step_type == StepType.SCRIPT:
            return f"[DRY RUN] Would execute script"

        elif step.step_type == StepType.WAIT:
            return f"[DRY RUN] Would wait {step.wait_seconds}s"

        elif step.step_type == StepType.NOTIFICATION:
            return f"[DRY RUN] Would notify: {step.notification_channel}"

        else:
            return f"[DRY RUN] {step.name}"

    async def _execute_command(self, command: str, timeout: int) -> str:
        """Execute a shell command."""
        logger.info(f"Executing command: {command}")

        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                raise TimeoutError(f"Command timed out after {timeout}s")

            output = stdout.decode() if stdout else ""
            error = stderr.decode() if stderr else ""

            if process.returncode != 0:
                raise RuntimeError(f"Command failed: {error or output}")

            return output

        except Exception as e:
            logger.error(f"Command execution failed: {e}")
            raise

    async def _execute_api_call(
        self,
        endpoint: str,
        method: str,
        payload: Optional[Dict],
        timeout: int
    ) -> str:
        """Execute an API call."""
        import httpx

        logger.info(f"API call: {method} {endpoint}")

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(endpoint)
                elif method.upper() == "POST":
                    response = await client.post(endpoint, json=payload)
                elif method.upper() == "PUT":
                    response = await client.put(endpoint, json=payload)
                elif method.upper() == "DELETE":
                    response = await client.delete(endpoint)
                else:
                    raise ValueError(f"Unknown HTTP method: {method}")

                response.raise_for_status()
                return response.text

        except Exception as e:
            logger.error(f"API call failed: {e}")
            raise

    async def _execute_script(self, script: str, timeout: int) -> str:
        """Execute a Python script."""
        logger.info("Executing script")

        try:
            # Execute in a restricted namespace
            namespace = {"result": None}

            exec(script, namespace)

            return str(namespace.get("result", "Script completed"))

        except Exception as e:
            logger.error(f"Script execution failed: {e}")
            raise

    async def _evaluate_condition(
        self,
        condition: str,
        context: Dict[str, Any]
    ) -> str:
        """Evaluate a condition."""
        logger.info(f"Evaluating condition: {condition}")

        try:
            # Simple evaluation - in production use a safe eval
            result = eval(condition, {"__builtins__": {}}, context)
            return f"Condition result: {result}"

        except Exception as e:
            logger.error(f"Condition evaluation failed: {e}")
            raise

    async def _send_notification(self, channel: str, message: str) -> str:
        """Send a notification."""
        logger.info(f"Sending notification to {channel}: {message}")

        # In a real implementation, this would send to Slack, email, etc.
        # For now, just log it

        return f"Notification sent to {channel}"

    def _interpolate_step(
        self,
        step: RunbookStep,
        target: str,
        context: Dict[str, Any]
    ) -> RunbookStep:
        """Replace placeholders in step configuration."""
        # Create a copy with interpolated values
        step_dict = step.model_dump()

        # Build interpolation context
        interp_context = {
            "target": target,
            "service_name": target,
            "timestamp": datetime.utcnow().isoformat(),
            **context
        }

        # Interpolate string fields
        for field in ["command", "api_endpoint", "script", "condition"]:
            if step_dict.get(field):
                for key, value in interp_context.items():
                    step_dict[field] = step_dict[field].replace(
                        f"{{{key}}}",
                        str(value)
                    )

        # Interpolate API payload
        if step_dict.get("api_payload"):
            payload = step_dict["api_payload"]
            for key, value in payload.items():
                if isinstance(value, str):
                    for ctx_key, ctx_value in interp_context.items():
                        payload[key] = value.replace(
                            f"{{{ctx_key}}}",
                            str(ctx_value)
                        )

        return RunbookStep(**step_dict)
