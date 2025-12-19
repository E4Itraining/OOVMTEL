"""
Voice Interface - Data Models
"""

from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from enum import Enum
from pydantic import BaseModel, Field


class SupportedLanguage(str, Enum):
    """Supported languages for voice recognition."""
    FRENCH = "fr-FR"
    ENGLISH = "en-US"
    ENGLISH_UK = "en-GB"
    GERMAN = "de-DE"
    SPANISH = "es-ES"
    ITALIAN = "it-IT"
    PORTUGUESE = "pt-BR"
    DUTCH = "nl-NL"


class VoiceState(str, Enum):
    """Voice engine state."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    ERROR = "error"


class RecognitionProvider(str, Enum):
    """Speech recognition provider."""
    BROWSER = "browser"          # Web Speech API
    WHISPER = "whisper"          # OpenAI Whisper
    AZURE = "azure"              # Azure Cognitive Services
    GOOGLE = "google"            # Google Cloud Speech
    VOSK = "vosk"                # Offline Vosk
    LOCAL = "local"              # Local model


class VoiceConfig(BaseModel):
    """Voice interface configuration."""
    # Language
    language: SupportedLanguage = SupportedLanguage.FRENCH
    secondary_language: Optional[SupportedLanguage] = SupportedLanguage.ENGLISH

    # Recognition settings
    provider: RecognitionProvider = RecognitionProvider.BROWSER
    continuous: bool = True            # Continuous listening
    interim_results: bool = True       # Show intermediate results
    max_alternatives: int = 3

    # Wake word
    use_wake_word: bool = True
    wake_words: List[str] = Field(default_factory=lambda: ["synapsix", "système", "system"])
    wake_word_sensitivity: float = 0.5

    # Audio settings
    sample_rate: int = 16000
    channels: int = 1
    noise_suppression: bool = True
    auto_gain_control: bool = True

    # Timeouts
    speech_timeout_seconds: float = 5.0
    max_speech_duration_seconds: float = 30.0
    silence_threshold_db: float = -40.0

    # Text-to-speech
    tts_enabled: bool = True
    tts_voice: str = "default"
    tts_rate: float = 1.0
    tts_volume: float = 1.0

    # Commands
    confirmation_required: bool = True
    confirmation_words: List[str] = Field(default_factory=lambda: ["oui", "yes", "confirme", "confirm"])
    cancellation_words: List[str] = Field(default_factory=lambda: ["non", "no", "annule", "cancel"])


class TranscriptionResult(BaseModel):
    """Result of speech-to-text transcription."""
    transcription_id: str
    text: str
    confidence: float = 0.0
    language: str = ""
    is_final: bool = True

    # Alternatives
    alternatives: List[Dict[str, Any]] = Field(default_factory=list)

    # Timing
    start_time: float = 0.0
    end_time: float = 0.0
    duration_seconds: float = 0.0

    # Audio info
    audio_duration_seconds: float = 0.0

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    provider: str = ""


class VoiceCommandResult(BaseModel):
    """Result of voice command execution."""
    command_id: str
    success: bool
    command_text: str
    recognized_intent: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)

    # Execution
    action_taken: str = ""
    response_text: str = ""
    response_spoken: bool = False

    # Confidence
    intent_confidence: float = 0.0
    overall_confidence: float = 0.0

    # Errors
    error: Optional[str] = None

    # Timing
    recognition_time_ms: float = 0.0
    processing_time_ms: float = 0.0
    total_time_ms: float = 0.0

    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    requires_confirmation: bool = False


class CommandDefinition(BaseModel):
    """Definition of a voice command."""
    command_id: str
    name: str
    description: str = ""

    # Trigger phrases (multi-language)
    phrases: Dict[str, List[str]] = Field(default_factory=dict)
    # e.g., {"fr-FR": ["montre température", "affiche température"], "en-US": ["show temperature"]}

    # Parameters
    parameters: List[Dict[str, Any]] = Field(default_factory=list)
    # Each: {"name": str, "type": str, "required": bool, "patterns": List[str]}

    # Execution
    action: str = ""                   # Action identifier
    requires_confirmation: bool = False
    dangerous: bool = False            # Requires extra confirmation

    # Response templates
    response_templates: Dict[str, str] = Field(default_factory=dict)
    # e.g., {"fr-FR": "La température est de {value} degrés", "en-US": "Temperature is {value} degrees"}

    # Context
    context_required: List[str] = Field(default_factory=list)  # Required context keys
    sets_context: Dict[str, str] = Field(default_factory=dict)  # Context to set after execution


# Pre-defined industrial voice commands
INDUSTRIAL_COMMANDS = {
    "show_temperature": CommandDefinition(
        command_id="show_temperature",
        name="Show Temperature",
        description="Display temperature for equipment",
        phrases={
            "fr-FR": ["montre température", "affiche température", "quelle est la température",
                      "température de", "donne moi la température"],
            "en-US": ["show temperature", "display temperature", "what is the temperature",
                      "temperature of", "give me temperature"],
        },
        parameters=[
            {"name": "equipment", "type": "equipment_name", "required": False,
             "patterns": ["de (.*)", "of (.*)", "pour (.*)", "for (.*)"]}
        ],
        action="get_temperature",
        response_templates={
            "fr-FR": "La température de {equipment} est de {value} degrés Celsius",
            "en-US": "The temperature of {equipment} is {value} degrees Celsius",
        }
    ),
    "show_status": CommandDefinition(
        command_id="show_status",
        name="Show Status",
        description="Display equipment or system status",
        phrases={
            "fr-FR": ["montre statut", "affiche statut", "état de", "comment va",
                      "quel est l'état", "status"],
            "en-US": ["show status", "display status", "status of", "how is",
                      "what is the status"],
        },
        parameters=[
            {"name": "equipment", "type": "equipment_name", "required": False}
        ],
        action="get_status",
    ),
    "show_alerts": CommandDefinition(
        command_id="show_alerts",
        name="Show Alerts",
        description="Display current alerts",
        phrases={
            "fr-FR": ["montre alertes", "affiche alertes", "quelles alertes",
                      "y a-t-il des alertes", "alertes actives"],
            "en-US": ["show alerts", "display alerts", "what alerts",
                      "are there alerts", "active alerts"],
        },
        action="get_alerts",
    ),
    "acknowledge_alert": CommandDefinition(
        command_id="acknowledge_alert",
        name="Acknowledge Alert",
        description="Acknowledge an active alert",
        phrases={
            "fr-FR": ["acquitte alerte", "confirme alerte", "j'ai vu l'alerte"],
            "en-US": ["acknowledge alert", "confirm alert", "ack alert"],
        },
        parameters=[
            {"name": "alert_id", "type": "string", "required": False}
        ],
        action="acknowledge_alert",
        requires_confirmation=True,
    ),
    "start_equipment": CommandDefinition(
        command_id="start_equipment",
        name="Start Equipment",
        description="Start equipment",
        phrases={
            "fr-FR": ["démarre", "lance", "active", "mets en marche"],
            "en-US": ["start", "launch", "activate", "turn on"],
        },
        parameters=[
            {"name": "equipment", "type": "equipment_name", "required": True}
        ],
        action="start_equipment",
        requires_confirmation=True,
        dangerous=True,
    ),
    "stop_equipment": CommandDefinition(
        command_id="stop_equipment",
        name="Stop Equipment",
        description="Stop equipment",
        phrases={
            "fr-FR": ["arrête", "stoppe", "désactive", "coupe"],
            "en-US": ["stop", "halt", "deactivate", "turn off"],
        },
        parameters=[
            {"name": "equipment", "type": "equipment_name", "required": True}
        ],
        action="stop_equipment",
        requires_confirmation=True,
        dangerous=True,
    ),
    "show_oee": CommandDefinition(
        command_id="show_oee",
        name="Show OEE",
        description="Display OEE metrics",
        phrases={
            "fr-FR": ["montre oee", "affiche oee", "quel est l'oee", "performance",
                      "taux de rendement"],
            "en-US": ["show oee", "display oee", "what is the oee", "performance",
                      "overall equipment effectiveness"],
        },
        action="get_oee",
    ),
    "navigate": CommandDefinition(
        command_id="navigate",
        name="Navigate",
        description="Navigate to a dashboard or page",
        phrases={
            "fr-FR": ["va à", "navigue vers", "montre", "affiche", "ouvre"],
            "en-US": ["go to", "navigate to", "show", "display", "open"],
        },
        parameters=[
            {"name": "destination", "type": "page_name", "required": True}
        ],
        action="navigate",
    ),
    "help": CommandDefinition(
        command_id="help",
        name="Help",
        description="Show available commands",
        phrases={
            "fr-FR": ["aide", "help", "qu'est-ce que tu peux faire", "commandes"],
            "en-US": ["help", "what can you do", "commands", "assistance"],
        },
        action="show_help",
    ),
}
