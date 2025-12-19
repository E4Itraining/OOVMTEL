"""
Voice Command Handler - Process and execute voice commands
"""

import logging
import re
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Awaitable, Tuple

from .models import (
    VoiceConfig,
    TranscriptionResult,
    VoiceCommandResult,
    CommandDefinition,
    SupportedLanguage,
    INDUSTRIAL_COMMANDS,
)

logger = logging.getLogger(__name__)


class VoiceCommand:
    """Represents a parsed voice command."""

    def __init__(
        self,
        command_def: CommandDefinition,
        parameters: Dict[str, Any],
        raw_text: str,
        confidence: float = 1.0
    ):
        self.definition = command_def
        self.parameters = parameters
        self.raw_text = raw_text
        self.confidence = confidence


class VoiceCommandHandler:
    """
    Voice command parsing and execution.

    Features:
    - Intent recognition from speech
    - Parameter extraction
    - Multi-language support
    - Command confirmation
    - Context management
    """

    def __init__(self, config: VoiceConfig):
        self.config = config
        self._commands: Dict[str, CommandDefinition] = dict(INDUSTRIAL_COMMANDS)
        self._action_handlers: Dict[str, Callable] = {}
        self._context: Dict[str, Any] = {}
        self._pending_confirmation: Optional[VoiceCommand] = None

        logger.info("Voice Command Handler initialized")

    def register_command(self, command: CommandDefinition) -> None:
        """Register a voice command."""
        self._commands[command.command_id] = command
        logger.info(f"Registered command: {command.name}")

    def register_action_handler(
        self,
        action: str,
        handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> None:
        """Register handler for an action."""
        self._action_handlers[action] = handler
        logger.info(f"Registered handler for action: {action}")

    async def process_transcription(
        self,
        transcription: TranscriptionResult
    ) -> VoiceCommandResult:
        """
        Process a transcription and execute the command.

        Args:
            transcription: Speech transcription result

        Returns:
            Command execution result
        """
        start_time = time.time()
        command_id = f"CMD-{uuid.uuid4().hex[:8]}"

        result = VoiceCommandResult(
            command_id=command_id,
            success=False,
            command_text=transcription.text,
        )

        try:
            text = transcription.text.lower().strip()

            # Check for confirmation/cancellation
            if self._pending_confirmation:
                return await self._handle_confirmation(text, transcription, result)

            # Parse command
            command = self._parse_command(text, transcription.language)

            if not command:
                result.error = "Commande non reconnue"
                result.response_text = "Je n'ai pas compris la commande. Dites 'aide' pour la liste des commandes."
                return result

            result.recognized_intent = command.definition.command_id
            result.parameters = command.parameters
            result.intent_confidence = command.confidence
            result.overall_confidence = transcription.confidence * command.confidence

            # Check if confirmation required
            if command.definition.requires_confirmation:
                self._pending_confirmation = command
                result.requires_confirmation = True
                result.response_text = self._get_confirmation_prompt(command)
                result.success = True
                return result

            # Execute command
            execution_result = await self._execute_command(command)

            result.success = execution_result.get("success", False)
            result.action_taken = execution_result.get("action", "")
            result.response_text = execution_result.get("response", "")
            result.error = execution_result.get("error")

        except Exception as e:
            logger.error(f"Command processing error: {e}")
            result.error = str(e)
            result.response_text = "Une erreur s'est produite lors du traitement de la commande."

        finally:
            result.processing_time_ms = (time.time() - start_time) * 1000
            result.recognition_time_ms = transcription.duration_seconds * 1000
            result.total_time_ms = result.recognition_time_ms + result.processing_time_ms

        return result

    def _parse_command(
        self,
        text: str,
        language: str
    ) -> Optional[VoiceCommand]:
        """Parse text to find matching command."""
        best_match: Optional[Tuple[CommandDefinition, float, Dict]] = None
        best_score = 0.0

        for cmd_id, cmd_def in self._commands.items():
            # Get phrases for this language (fallback to any language)
            phrases = cmd_def.phrases.get(language, [])
            if not phrases:
                for lang_phrases in cmd_def.phrases.values():
                    phrases.extend(lang_phrases)

            for phrase in phrases:
                score, params = self._match_phrase(text, phrase, cmd_def)
                if score > best_score:
                    best_score = score
                    best_match = (cmd_def, score, params)

        if best_match and best_score > 0.5:
            cmd_def, score, params = best_match
            return VoiceCommand(cmd_def, params, text, score)

        return None

    def _match_phrase(
        self,
        text: str,
        phrase: str,
        cmd_def: CommandDefinition
    ) -> Tuple[float, Dict[str, Any]]:
        """Match text against phrase pattern."""
        text_lower = text.lower()
        phrase_lower = phrase.lower()

        # Direct match
        if phrase_lower in text_lower:
            score = len(phrase_lower) / len(text_lower)
            params = self._extract_parameters(text, cmd_def)
            return (score, params)

        # Fuzzy match using word overlap
        text_words = set(text_lower.split())
        phrase_words = set(phrase_lower.split())
        common_words = text_words & phrase_words

        if len(phrase_words) > 0:
            score = len(common_words) / len(phrase_words)
            if score > 0.5:
                params = self._extract_parameters(text, cmd_def)
                return (score * 0.8, params)

        return (0.0, {})

    def _extract_parameters(
        self,
        text: str,
        cmd_def: CommandDefinition
    ) -> Dict[str, Any]:
        """Extract parameters from text."""
        params = {}

        for param_def in cmd_def.parameters:
            param_name = param_def["name"]
            param_type = param_def.get("type", "string")
            patterns = param_def.get("patterns", [])

            value = None

            # Try patterns
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match and match.groups():
                    value = match.group(1).strip()
                    break

            # Type-specific extraction
            if value is None and param_type == "equipment_name":
                value = self._extract_equipment_name(text)

            if value is not None:
                params[param_name] = value

        return params

    def _extract_equipment_name(self, text: str) -> Optional[str]:
        """Extract equipment name from text."""
        # Common patterns for equipment reference
        patterns = [
            r"(?:de|du|pour|for|of)\s+(?:l[ae]?\s+)?(.+?)(?:\s*$|\s+(?:et|and|ou|or))",
            r"(?:équipement|equipment|machine)\s+(.+?)(?:\s*$|\s+(?:et|and))",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        # Try to find capitalized words
        words = text.split()
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                return word

        return None

    async def _execute_command(
        self,
        command: VoiceCommand
    ) -> Dict[str, Any]:
        """Execute a parsed command."""
        action = command.definition.action

        if action in self._action_handlers:
            handler = self._action_handlers[action]
            try:
                result = await handler(command.parameters)
                return {
                    "success": True,
                    "action": action,
                    "response": self._format_response(command, result),
                    **result
                }
            except Exception as e:
                logger.error(f"Action handler error: {e}")
                return {"success": False, "error": str(e)}

        # Default actions
        if action == "show_help":
            return self._show_help()
        elif action == "get_temperature":
            return self._mock_get_temperature(command.parameters)
        elif action == "get_status":
            return self._mock_get_status(command.parameters)
        elif action == "get_alerts":
            return self._mock_get_alerts()
        elif action == "get_oee":
            return self._mock_get_oee()

        return {
            "success": False,
            "error": f"Action non implémentée: {action}"
        }

    def _format_response(
        self,
        command: VoiceCommand,
        result: Dict[str, Any]
    ) -> str:
        """Format response using template."""
        lang = self.config.language.value
        templates = command.definition.response_templates

        template = templates.get(lang) or templates.get("fr-FR") or templates.get("en-US")

        if template:
            try:
                return template.format(**command.parameters, **result)
            except KeyError:
                pass

        return result.get("response", "Commande exécutée")

    async def _handle_confirmation(
        self,
        text: str,
        transcription: TranscriptionResult,
        result: VoiceCommandResult
    ) -> VoiceCommandResult:
        """Handle confirmation response."""
        command = self._pending_confirmation

        # Check for confirmation
        is_confirmed = any(
            word in text for word in self.config.confirmation_words
        )
        is_cancelled = any(
            word in text for word in self.config.cancellation_words
        )

        if is_confirmed:
            self._pending_confirmation = None
            execution_result = await self._execute_command(command)
            result.success = execution_result.get("success", False)
            result.action_taken = execution_result.get("action", "")
            result.response_text = execution_result.get("response", "Commande exécutée")
            result.recognized_intent = command.definition.command_id

        elif is_cancelled:
            self._pending_confirmation = None
            result.success = True
            result.response_text = "Commande annulée"
            result.action_taken = "cancelled"

        else:
            result.requires_confirmation = True
            result.response_text = "Veuillez confirmer avec 'oui' ou annuler avec 'non'"

        return result

    def _get_confirmation_prompt(self, command: VoiceCommand) -> str:
        """Get confirmation prompt for a command."""
        action_desc = command.definition.name

        if command.parameters.get("equipment"):
            action_desc += f" pour {command.parameters['equipment']}"

        if command.definition.dangerous:
            return f"Attention: {action_desc}. Êtes-vous sûr? Dites 'oui' pour confirmer."

        return f"Voulez-vous {action_desc.lower()}? Dites 'oui' pour confirmer."

    # Mock implementations for default actions

    def _show_help(self) -> Dict[str, Any]:
        """Show available commands."""
        lang = self.config.language.value
        commands_list = []

        for cmd_id, cmd_def in self._commands.items():
            phrases = cmd_def.phrases.get(lang, [])
            if phrases:
                commands_list.append(f"- {cmd_def.name}: '{phrases[0]}'")

        response = "Commandes disponibles:\n" + "\n".join(commands_list[:10])

        return {"success": True, "response": response, "commands": list(self._commands.keys())}

    def _mock_get_temperature(self, params: Dict) -> Dict[str, Any]:
        """Mock temperature query."""
        equipment = params.get("equipment", "système")
        import random
        temp = round(20 + random.random() * 40, 1)

        return {
            "success": True,
            "value": temp,
            "equipment": equipment,
            "response": f"La température de {equipment} est de {temp} degrés Celsius"
        }

    def _mock_get_status(self, params: Dict) -> Dict[str, Any]:
        """Mock status query."""
        equipment = params.get("equipment", "système")

        return {
            "success": True,
            "status": "running",
            "equipment": equipment,
            "response": f"{equipment} fonctionne normalement"
        }

    def _mock_get_alerts(self) -> Dict[str, Any]:
        """Mock alerts query."""
        return {
            "success": True,
            "alert_count": 2,
            "response": "Il y a 2 alertes actives: 1 critique, 1 avertissement"
        }

    def _mock_get_oee(self) -> Dict[str, Any]:
        """Mock OEE query."""
        import random
        oee = round(75 + random.random() * 20, 1)

        return {
            "success": True,
            "oee": oee,
            "response": f"Le TRS global est de {oee} pourcent"
        }

    def set_context(self, key: str, value: Any) -> None:
        """Set context value."""
        self._context[key] = value

    def get_context(self, key: str) -> Optional[Any]:
        """Get context value."""
        return self._context.get(key)

    def clear_context(self) -> None:
        """Clear all context."""
        self._context.clear()
        self._pending_confirmation = None
