"""
Speech Recognizer - Speech-to-text conversion
"""

import logging
import asyncio
import uuid
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable, Awaitable
import re

from .models import (
    VoiceConfig,
    TranscriptionResult,
    SupportedLanguage,
    RecognitionProvider,
    VoiceState,
)

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """
    Speech-to-text recognizer for SYNAPSIX.

    Features:
    - Multiple provider support
    - Multi-language recognition
    - Wake word detection
    - Noise filtering
    - Streaming transcription
    """

    def __init__(self, config: VoiceConfig):
        self.config = config
        self.state = VoiceState.IDLE
        self._callbacks: List[Callable[[TranscriptionResult], Awaitable[None]]] = []
        self._wake_word_detected = False
        self._session_id: Optional[str] = None

        logger.info(f"Speech Recognizer initialized with provider: {config.provider.value}")

    async def start_listening(self) -> str:
        """
        Start listening for speech.

        Returns:
            Session ID
        """
        self._session_id = f"SESSION-{uuid.uuid4().hex[:8]}"
        self.state = VoiceState.LISTENING

        if not self.config.use_wake_word:
            self._wake_word_detected = True

        logger.info(f"Started listening session: {self._session_id}")
        return self._session_id

    async def stop_listening(self) -> None:
        """Stop listening for speech."""
        self.state = VoiceState.IDLE
        self._wake_word_detected = False
        logger.info(f"Stopped listening session: {self._session_id}")
        self._session_id = None

    def on_transcription(
        self,
        callback: Callable[[TranscriptionResult], Awaitable[None]]
    ) -> None:
        """Register callback for transcription results."""
        self._callbacks.append(callback)

    async def process_audio(
        self,
        audio_data: bytes,
        sample_rate: int = 16000
    ) -> Optional[TranscriptionResult]:
        """
        Process audio data and return transcription.

        Args:
            audio_data: Raw audio bytes (PCM)
            sample_rate: Audio sample rate

        Returns:
            Transcription result or None
        """
        if self.state != VoiceState.LISTENING:
            return None

        self.state = VoiceState.PROCESSING
        start_time = time.time()

        try:
            # Select provider
            if self.config.provider == RecognitionProvider.WHISPER:
                result = await self._transcribe_whisper(audio_data, sample_rate)
            elif self.config.provider == RecognitionProvider.VOSK:
                result = await self._transcribe_vosk(audio_data, sample_rate)
            else:
                # Simulate transcription for browser/local
                result = await self._transcribe_simulated(audio_data, sample_rate)

            if result:
                result.duration_seconds = time.time() - start_time

                # Check for wake word if needed
                if self.config.use_wake_word and not self._wake_word_detected:
                    if self._check_wake_word(result.text):
                        self._wake_word_detected = True
                        result.text = self._remove_wake_word(result.text)
                    else:
                        # Ignore non-wake word speech
                        self.state = VoiceState.LISTENING
                        return None

                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        await callback(result)
                    except Exception as e:
                        logger.error(f"Callback error: {e}")

            self.state = VoiceState.LISTENING
            return result

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            self.state = VoiceState.ERROR
            return None

    async def _transcribe_whisper(
        self,
        audio_data: bytes,
        sample_rate: int
    ) -> Optional[TranscriptionResult]:
        """Transcribe using OpenAI Whisper API."""
        try:
            import httpx

            # Would need actual Whisper API implementation
            # This is a placeholder

            async with httpx.AsyncClient() as client:
                # Convert audio to appropriate format
                # Send to Whisper API
                pass

        except ImportError:
            logger.warning("httpx not available for Whisper API")

        return None

    async def _transcribe_vosk(
        self,
        audio_data: bytes,
        sample_rate: int
    ) -> Optional[TranscriptionResult]:
        """Transcribe using Vosk offline model."""
        try:
            # Would need Vosk library
            # This is a placeholder
            pass
        except Exception as e:
            logger.error(f"Vosk transcription error: {e}")

        return None

    async def _transcribe_simulated(
        self,
        audio_data: bytes,
        sample_rate: int
    ) -> TranscriptionResult:
        """Simulated transcription for testing."""
        # Simulate processing delay
        await asyncio.sleep(0.5)

        # Return simulated result
        return TranscriptionResult(
            transcription_id=f"TRANS-{uuid.uuid4().hex[:8]}",
            text="commande simulée",
            confidence=0.95,
            language=self.config.language.value,
            is_final=True,
            audio_duration_seconds=len(audio_data) / (sample_rate * 2),
            provider="simulated",
        )

    def _check_wake_word(self, text: str) -> bool:
        """Check if text contains wake word."""
        text_lower = text.lower()

        for wake_word in self.config.wake_words:
            if wake_word.lower() in text_lower:
                return True

        return False

    def _remove_wake_word(self, text: str) -> str:
        """Remove wake word from text."""
        text_lower = text.lower()

        for wake_word in self.config.wake_words:
            pattern = re.compile(re.escape(wake_word), re.IGNORECASE)
            text = pattern.sub("", text).strip()

        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    async def transcribe_from_file(
        self,
        file_path: str
    ) -> Optional[TranscriptionResult]:
        """Transcribe from audio file."""
        try:
            # Read audio file
            with open(file_path, 'rb') as f:
                audio_data = f.read()

            return await self.process_audio(audio_data)

        except Exception as e:
            logger.error(f"File transcription error: {e}")
            return None

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages."""
        return [lang.value for lang in SupportedLanguage]

    def set_language(self, language: SupportedLanguage) -> None:
        """Set recognition language."""
        self.config.language = language
        logger.info(f"Language set to: {language.value}")


class TextToSpeech:
    """Text-to-speech synthesis."""

    def __init__(self, config: VoiceConfig):
        self.config = config

    async def speak(
        self,
        text: str,
        language: Optional[SupportedLanguage] = None
    ) -> bool:
        """
        Synthesize speech from text.

        This would integrate with browser TTS or cloud TTS APIs.
        """
        lang = language or self.config.language

        logger.info(f"TTS: {text} ({lang.value})")

        # Would call actual TTS API
        return True

    def get_available_voices(
        self,
        language: Optional[SupportedLanguage] = None
    ) -> List[Dict[str, str]]:
        """Get available TTS voices."""
        # Would query TTS API
        return [
            {"id": "default", "name": "Default Voice", "language": "fr-FR"},
            {"id": "male1", "name": "Male Voice 1", "language": "fr-FR"},
            {"id": "female1", "name": "Female Voice 1", "language": "fr-FR"},
        ]
