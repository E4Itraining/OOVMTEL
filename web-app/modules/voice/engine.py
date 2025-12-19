"""
Voice Engine - Main voice interface engine
"""

import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Awaitable

from .models import (
    VoiceConfig,
    TranscriptionResult,
    VoiceCommandResult,
    SupportedLanguage,
    VoiceState,
)
from .speech_recognizer import SpeechRecognizer, TextToSpeech
from .command_handler import VoiceCommandHandler

logger = logging.getLogger(__name__)


class VoiceEngine:
    """
    Main Voice Interface Engine for SYNAPSIX.

    Features:
    - Hands-free voice control
    - Multi-language support
    - Wake word activation
    - Command confirmation
    - Text-to-speech feedback
    - Integration with SYNAPSIX modules
    """

    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self.recognizer = SpeechRecognizer(self.config)
        self.command_handler = VoiceCommandHandler(self.config)
        self.tts = TextToSpeech(self.config)

        self._running = False
        self._session_id: Optional[str] = None
        self._command_history: List[VoiceCommandResult] = []

        # Callbacks
        self._on_state_change: List[Callable[[VoiceState], Awaitable[None]]] = []
        self._on_transcription: List[Callable[[TranscriptionResult], Awaitable[None]]] = []
        self._on_command: List[Callable[[VoiceCommandResult], Awaitable[None]]] = []

        # Wire up recognizer callback
        self.recognizer.on_transcription(self._handle_transcription)

        logger.info("Voice Engine initialized")

    async def start(self) -> str:
        """
        Start the voice engine.

        Returns:
            Session ID
        """
        self._running = True
        self._session_id = await self.recognizer.start_listening()

        await self._notify_state_change(VoiceState.LISTENING)

        if self.config.tts_enabled:
            await self.speak("Système vocal activé")

        logger.info(f"Voice Engine started: {self._session_id}")
        return self._session_id

    async def stop(self) -> None:
        """Stop the voice engine."""
        self._running = False

        if self.config.tts_enabled:
            await self.speak("Système vocal désactivé")

        await self.recognizer.stop_listening()
        await self._notify_state_change(VoiceState.IDLE)

        logger.info("Voice Engine stopped")

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def state(self) -> VoiceState:
        return self.recognizer.state

    async def process_audio(
        self,
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> Optional[VoiceCommandResult]:
        """
        Process audio input.

        Args:
            audio_data: Raw audio bytes
            sample_rate: Audio sample rate

        Returns:
            Command result if command detected
        """
        if not self._running:
            return None

        # Transcribe
        transcription = await self.recognizer.process_audio(audio_data, sample_rate)

        if transcription and transcription.text:
            return await self._process_command(transcription)

        return None

    async def process_text(self, text: str) -> VoiceCommandResult:
        """
        Process text input (simulated voice).

        Useful for testing or keyboard-based voice simulation.
        """
        transcription = TranscriptionResult(
            transcription_id=f"TEXT-{datetime.utcnow().timestamp()}",
            text=text,
            confidence=1.0,
            language=self.config.language.value,
            is_final=True,
            provider="text_input",
        )

        return await self._process_command(transcription)

    async def _handle_transcription(
        self,
        transcription: TranscriptionResult
    ) -> None:
        """Handle transcription from recognizer."""
        # Notify callbacks
        for callback in self._on_transcription:
            try:
                await callback(transcription)
            except Exception as e:
                logger.error(f"Transcription callback error: {e}")

        # Process as command
        if transcription.is_final and transcription.text:
            await self._process_command(transcription)

    async def _process_command(
        self,
        transcription: TranscriptionResult
    ) -> VoiceCommandResult:
        """Process transcription as command."""
        await self._notify_state_change(VoiceState.PROCESSING)

        # Handle command
        result = await self.command_handler.process_transcription(transcription)

        # Add to history
        self._command_history.append(result)

        # Speak response
        if self.config.tts_enabled and result.response_text:
            await self._notify_state_change(VoiceState.SPEAKING)
            await self.speak(result.response_text)
            result.response_spoken = True

        # Notify callbacks
        for callback in self._on_command:
            try:
                await callback(result)
            except Exception as e:
                logger.error(f"Command callback error: {e}")

        await self._notify_state_change(VoiceState.LISTENING)

        return result

    async def speak(self, text: str) -> bool:
        """
        Speak text using TTS.

        Args:
            text: Text to speak

        Returns:
            True if spoken successfully
        """
        await self._notify_state_change(VoiceState.SPEAKING)
        success = await self.tts.speak(text, self.config.language)
        await self._notify_state_change(VoiceState.LISTENING)
        return success

    # Configuration

    def set_language(self, language: SupportedLanguage) -> None:
        """Set recognition language."""
        self.config.language = language
        self.recognizer.set_language(language)
        logger.info(f"Language set to: {language.value}")

    def set_wake_word_enabled(self, enabled: bool) -> None:
        """Enable or disable wake word."""
        self.config.use_wake_word = enabled
        logger.info(f"Wake word {'enabled' if enabled else 'disabled'}")

    def add_wake_word(self, word: str) -> None:
        """Add a wake word."""
        if word not in self.config.wake_words:
            self.config.wake_words.append(word)

    # Action Handlers

    def register_action(
        self,
        action: str,
        handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> None:
        """Register handler for a voice action."""
        self.command_handler.register_action_handler(action, handler)

    # Callbacks

    def on_state_change(
        self,
        callback: Callable[[VoiceState], Awaitable[None]]
    ) -> None:
        """Register state change callback."""
        self._on_state_change.append(callback)

    def on_transcription(
        self,
        callback: Callable[[TranscriptionResult], Awaitable[None]]
    ) -> None:
        """Register transcription callback."""
        self._on_transcription.append(callback)

    def on_command(
        self,
        callback: Callable[[VoiceCommandResult], Awaitable[None]]
    ) -> None:
        """Register command callback."""
        self._on_command.append(callback)

    async def _notify_state_change(self, state: VoiceState) -> None:
        """Notify state change callbacks."""
        for callback in self._on_state_change:
            try:
                await callback(state)
            except Exception as e:
                logger.error(f"State change callback error: {e}")

    # History

    def get_command_history(self, limit: int = 50) -> List[VoiceCommandResult]:
        """Get command history."""
        return self._command_history[-limit:]

    def clear_history(self) -> None:
        """Clear command history."""
        self._command_history.clear()

    # Stats

    def get_stats(self) -> Dict[str, Any]:
        """Get voice engine statistics."""
        successful = sum(1 for c in self._command_history if c.success)
        total = len(self._command_history)

        return {
            "running": self._running,
            "state": self.state.value,
            "session_id": self._session_id,
            "language": self.config.language.value,
            "wake_word_enabled": self.config.use_wake_word,
            "commands_total": total,
            "commands_successful": successful,
            "success_rate": successful / total if total > 0 else 0,
            "avg_confidence": sum(c.overall_confidence for c in self._command_history) / total if total > 0 else 0,
        }

    async def get_help_text(self) -> str:
        """Get help text for available commands."""
        lang = self.config.language.value
        lines = ["Commandes vocales disponibles:\n"]

        for cmd_id, cmd_def in self.command_handler._commands.items():
            phrases = cmd_def.phrases.get(lang, [])
            if phrases:
                lines.append(f"• {cmd_def.name}: \"{phrases[0]}\"")
                if cmd_def.description:
                    lines.append(f"  {cmd_def.description}")

        return "\n".join(lines)
