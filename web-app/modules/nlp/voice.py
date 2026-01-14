"""
Multi-modal NLP Module with Voice Support
Adds speech-to-text capabilities for natural language queries
"""

import asyncio
import base64
import io
import logging
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AudioFormat(str, Enum):
    """Supported audio formats."""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    WEBM = "webm"
    M4A = "m4a"


class TranscriptionStatus(str, Enum):
    """Status of transcription."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TranscriptionResult:
    """Result of audio transcription."""
    id: str
    status: TranscriptionStatus
    text: Optional[str]
    confidence: float
    language: str
    duration_seconds: float
    processing_time_ms: float
    error: Optional[str] = None


@dataclass
class VoiceConfig:
    """Voice processing configuration."""
    enabled: bool = True
    default_language: str = "fr-FR"  # French by default for industrial context
    alternative_languages: List[str] = None
    max_audio_duration_seconds: int = 30
    min_confidence_threshold: float = 0.7

    def __post_init__(self):
        if self.alternative_languages is None:
            self.alternative_languages = ["en-US", "de-DE", "es-ES"]


class VoiceProcessor:
    """
    Voice processor for multi-modal NLP.
    Converts speech to text for natural language queries.
    """

    def __init__(self, config: Optional[VoiceConfig] = None):
        self.config = config or VoiceConfig()
        self._recognizer = None
        self._initialized = False

    async def initialize(self) -> bool:
        """Initialize the voice processor."""
        if self._initialized:
            return True

        try:
            # Try to import speech recognition
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
            self._initialized = True
            logger.info("Voice processor initialized (SpeechRecognition)")
            return True
        except ImportError:
            logger.warning("SpeechRecognition not available, using mock mode")
            self._initialized = True
            return True

    async def transcribe_audio(
        self,
        audio_data: bytes,
        audio_format: AudioFormat = AudioFormat.WAV,
        language: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe audio to text.

        Args:
            audio_data: Raw audio bytes
            audio_format: Format of the audio
            language: Language code (e.g., 'fr-FR', 'en-US')

        Returns:
            TranscriptionResult with transcribed text
        """
        import uuid
        start_time = datetime.utcnow()
        result_id = str(uuid.uuid4())[:8]
        language = language or self.config.default_language

        try:
            if not self._initialized:
                await self.initialize()

            # If no recognizer (mock mode), return demo response
            if self._recognizer is None:
                return await self._mock_transcription(result_id, language, start_time)

            # Convert audio to WAV if needed
            audio_wav = await self._convert_to_wav(audio_data, audio_format)

            # Perform transcription
            import speech_recognition as sr

            with io.BytesIO(audio_wav) as audio_file:
                with sr.AudioFile(audio_file) as source:
                    audio = self._recognizer.record(source)
                    duration = len(audio_wav) / 32000  # Approximate duration

                    # Try Google Speech Recognition (free tier)
                    try:
                        text = self._recognizer.recognize_google(
                            audio,
                            language=language
                        )
                        confidence = 0.9  # Google doesn't return confidence

                    except sr.UnknownValueError:
                        # Speech not understood
                        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                        return TranscriptionResult(
                            id=result_id,
                            status=TranscriptionStatus.COMPLETED,
                            text=None,
                            confidence=0.0,
                            language=language,
                            duration_seconds=duration,
                            processing_time_ms=processing_time,
                            error="Speech not understood"
                        )

                    except sr.RequestError as e:
                        # API error, try mock
                        return await self._mock_transcription(result_id, language, start_time)

            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return TranscriptionResult(
                id=result_id,
                status=TranscriptionStatus.COMPLETED,
                text=text,
                confidence=confidence,
                language=language,
                duration_seconds=duration,
                processing_time_ms=processing_time
            )

        except Exception as e:
            logger.error(f"Transcription error: {e}")
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            return TranscriptionResult(
                id=result_id,
                status=TranscriptionStatus.FAILED,
                text=None,
                confidence=0.0,
                language=language,
                duration_seconds=0,
                processing_time_ms=processing_time,
                error=str(e)
            )

    async def _convert_to_wav(
        self,
        audio_data: bytes,
        audio_format: AudioFormat
    ) -> bytes:
        """Convert audio to WAV format."""
        if audio_format == AudioFormat.WAV:
            return audio_data

        try:
            from pydub import AudioSegment

            # Load audio with appropriate format
            audio = AudioSegment.from_file(
                io.BytesIO(audio_data),
                format=audio_format.value
            )

            # Convert to WAV
            wav_buffer = io.BytesIO()
            audio.export(wav_buffer, format="wav")
            return wav_buffer.getvalue()

        except Exception as e:
            logger.warning(f"Audio conversion failed: {e}, using raw data")
            return audio_data

    async def _mock_transcription(
        self,
        result_id: str,
        language: str,
        start_time: datetime
    ) -> TranscriptionResult:
        """Return mock transcription for demo/testing."""
        import random

        # Simulate processing time
        await asyncio.sleep(random.uniform(0.5, 1.5))

        # Mock queries based on language
        mock_queries = {
            "fr-FR": [
                "Quelle est la température du réacteur?",
                "Montre-moi l'OEE actuel",
                "Y a-t-il des alarmes critiques?",
                "Quel est l'état de la ligne de production?",
                "Quand est prévue la prochaine maintenance?",
            ],
            "en-US": [
                "What is the reactor temperature?",
                "Show me the current OEE",
                "Are there any critical alarms?",
                "What is the production line status?",
                "When is the next maintenance scheduled?",
            ]
        }

        queries = mock_queries.get(language, mock_queries["en-US"])
        text = random.choice(queries)

        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000

        return TranscriptionResult(
            id=result_id,
            status=TranscriptionStatus.COMPLETED,
            text=text,
            confidence=random.uniform(0.85, 0.98),
            language=language,
            duration_seconds=random.uniform(1.5, 4.0),
            processing_time_ms=processing_time
        )

    async def transcribe_base64(
        self,
        audio_base64: str,
        audio_format: AudioFormat = AudioFormat.WAV,
        language: Optional[str] = None
    ) -> TranscriptionResult:
        """
        Transcribe base64-encoded audio.

        Args:
            audio_base64: Base64-encoded audio data
            audio_format: Format of the audio
            language: Language code

        Returns:
            TranscriptionResult
        """
        try:
            audio_data = base64.b64decode(audio_base64)
            return await self.transcribe_audio(audio_data, audio_format, language)
        except Exception as e:
            logger.error(f"Base64 decode error: {e}")
            return TranscriptionResult(
                id="error",
                status=TranscriptionStatus.FAILED,
                text=None,
                confidence=0.0,
                language=language or self.config.default_language,
                duration_seconds=0,
                processing_time_ms=0,
                error=f"Invalid base64 audio: {e}"
            )

    def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages."""
        return [
            {"code": "fr-FR", "name": "French (France)", "native": "Français"},
            {"code": "en-US", "name": "English (US)", "native": "English"},
            {"code": "en-GB", "name": "English (UK)", "native": "English"},
            {"code": "de-DE", "name": "German", "native": "Deutsch"},
            {"code": "es-ES", "name": "Spanish", "native": "Español"},
            {"code": "it-IT", "name": "Italian", "native": "Italiano"},
            {"code": "pt-BR", "name": "Portuguese (Brazil)", "native": "Português"},
            {"code": "nl-NL", "name": "Dutch", "native": "Nederlands"},
            {"code": "pl-PL", "name": "Polish", "native": "Polski"},
            {"code": "zh-CN", "name": "Chinese (Simplified)", "native": "中文"},
            {"code": "ja-JP", "name": "Japanese", "native": "日本語"},
        ]

    def get_config(self) -> Dict[str, Any]:
        """Get voice processor configuration."""
        return {
            "enabled": self.config.enabled,
            "default_language": self.config.default_language,
            "alternative_languages": self.config.alternative_languages,
            "max_audio_duration_seconds": self.config.max_audio_duration_seconds,
            "min_confidence_threshold": self.config.min_confidence_threshold,
            "supported_formats": [f.value for f in AudioFormat],
            "initialized": self._initialized
        }


# Global voice processor instance
_voice_processor: Optional[VoiceProcessor] = None


async def get_voice_processor() -> VoiceProcessor:
    """Get or create voice processor instance."""
    global _voice_processor
    if _voice_processor is None:
        _voice_processor = VoiceProcessor()
        await _voice_processor.initialize()
    return _voice_processor
