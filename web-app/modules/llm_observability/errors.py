"""
LLM Observability Error Handling.

Provides standardized error codes, user-friendly messages,
and resolution suggestions for better UX.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any
from fastapi import HTTPException
from fastapi.responses import JSONResponse


class ErrorCode(str, Enum):
    """Standardized error codes for LLM Observability."""

    # Module availability errors (LLM_OBS_001-099)
    MODULE_NOT_AVAILABLE = "LLM_OBS_001"
    OTEL_COLLECTOR_UNAVAILABLE = "LLM_OBS_002"
    METRICS_DISABLED = "LLM_OBS_003"
    TRACING_DISABLED = "LLM_OBS_004"

    # Configuration errors (LLM_OBS_100-199)
    INVALID_CONFIG = "LLM_OBS_100"
    MISSING_ENV_VAR = "LLM_OBS_101"
    INVALID_THRESHOLD = "LLM_OBS_102"

    # Data errors (LLM_OBS_200-299)
    INVALID_PROVIDER = "LLM_OBS_200"
    INVALID_TIME_WINDOW = "LLM_OBS_201"
    NO_DATA_AVAILABLE = "LLM_OBS_202"
    NORMALIZATION_FAILED = "LLM_OBS_203"

    # Industrial data errors (LLM_OBS_300-399)
    INVALID_SOURCE = "LLM_OBS_300"
    INVALID_DATA_FORMAT = "LLM_OBS_301"
    CORRELATION_FAILED = "LLM_OBS_302"

    # Alert errors (LLM_OBS_400-499)
    ALERT_CONFIG_INVALID = "LLM_OBS_400"
    ALERT_THRESHOLD_EXCEEDED = "LLM_OBS_401"

    # Internal errors (LLM_OBS_500-599)
    INTERNAL_ERROR = "LLM_OBS_500"
    EXPORT_FAILED = "LLM_OBS_501"
    DATABASE_ERROR = "LLM_OBS_502"


@dataclass
class ErrorDetail:
    """Detailed error information for user-friendly responses."""

    code: ErrorCode
    message: str
    details: Optional[str] = None
    suggestion: Optional[str] = None
    doc_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        result = {
            "code": self.code.value,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        if self.suggestion:
            result["suggestion"] = self.suggestion
        if self.doc_url:
            result["doc_url"] = self.doc_url
        return result


# Error catalog with translations and suggestions
ERROR_CATALOG: Dict[ErrorCode, Dict[str, Any]] = {
    ErrorCode.MODULE_NOT_AVAILABLE: {
        "message": {
            "fr": "Le module d'observabilit\u00e9 LLM n'est pas disponible",
            "en": "LLM Observability module is not available",
            "nl": "LLM Observability module is niet beschikbaar",
            "de": "LLM Observability Modul ist nicht verf\u00fcgbar",
        },
        "suggestion": {
            "fr": "V\u00e9rifiez que les d\u00e9pendances OpenTelemetry sont install\u00e9es",
            "en": "Check that OpenTelemetry dependencies are installed",
            "nl": "Controleer of OpenTelemetry dependencies zijn ge\u00efnstalleerd",
            "de": "Pr\u00fcfen Sie, ob OpenTelemetry Abh\u00e4ngigkeiten installiert sind",
        },
        "doc_url": "/docs/troubleshooting/llm-observability#module-not-available",
    },
    ErrorCode.OTEL_COLLECTOR_UNAVAILABLE: {
        "message": {
            "fr": "Le collecteur OpenTelemetry n'est pas accessible",
            "en": "OpenTelemetry Collector is not reachable",
            "nl": "OpenTelemetry Collector is niet bereikbaar",
            "de": "OpenTelemetry Collector ist nicht erreichbar",
        },
        "suggestion": {
            "fr": "V\u00e9rifiez que le conteneur otel-collector est d\u00e9marr\u00e9 et accessible sur le port 4318",
            "en": "Verify that the otel-collector container is running and accessible on port 4318",
            "nl": "Controleer of de otel-collector container draait en bereikbaar is op poort 4318",
            "de": "Stellen Sie sicher, dass der otel-collector Container l\u00e4uft und auf Port 4318 erreichbar ist",
        },
        "doc_url": "/docs/troubleshooting/llm-observability#otel-collector",
    },
    ErrorCode.METRICS_DISABLED: {
        "message": {
            "fr": "La collecte de m\u00e9triques est d\u00e9sactiv\u00e9e",
            "en": "Metrics collection is disabled",
            "nl": "Metrics verzameling is uitgeschakeld",
            "de": "Metrik-Erfassung ist deaktiviert",
        },
        "suggestion": {
            "fr": "D\u00e9finissez LLM_METRICS_ENABLED=true dans vos variables d'environnement",
            "en": "Set LLM_METRICS_ENABLED=true in your environment variables",
            "nl": "Stel LLM_METRICS_ENABLED=true in uw omgevingsvariabelen",
            "de": "Setzen Sie LLM_METRICS_ENABLED=true in Ihren Umgebungsvariablen",
        },
        "doc_url": "/docs/configuration/llm-observability#metrics",
    },
    ErrorCode.INVALID_PROVIDER: {
        "message": {
            "fr": "Fournisseur LLM non reconnu",
            "en": "Unrecognized LLM provider",
            "nl": "Niet-herkende LLM provider",
            "de": "Nicht erkannter LLM Anbieter",
        },
        "suggestion": {
            "fr": "Utilisez un des fournisseurs support\u00e9s: mistral, claude, openai, ollama",
            "en": "Use one of the supported providers: mistral, claude, openai, ollama",
            "nl": "Gebruik een van de ondersteunde providers: mistral, claude, openai, ollama",
            "de": "Verwenden Sie einen der unterst\u00fctzten Anbieter: mistral, claude, openai, ollama",
        },
        "doc_url": "/docs/llm-observability/providers",
    },
    ErrorCode.INVALID_TIME_WINDOW: {
        "message": {
            "fr": "Fen\u00eatre temporelle invalide",
            "en": "Invalid time window",
            "nl": "Ongeldig tijdsvenster",
            "de": "Ung\u00fcltiges Zeitfenster",
        },
        "suggestion": {
            "fr": "La fen\u00eatre doit \u00eatre entre 1 et 1440 minutes (24 heures)",
            "en": "Window must be between 1 and 1440 minutes (24 hours)",
            "nl": "Venster moet tussen 1 en 1440 minuten (24 uur) zijn",
            "de": "Fenster muss zwischen 1 und 1440 Minuten (24 Stunden) liegen",
        },
        "doc_url": "/docs/api/llm-observability#metrics",
    },
    ErrorCode.NO_DATA_AVAILABLE: {
        "message": {
            "fr": "Aucune donn\u00e9e disponible pour la p\u00e9riode demand\u00e9e",
            "en": "No data available for the requested period",
            "nl": "Geen gegevens beschikbaar voor de gevraagde periode",
            "de": "Keine Daten f\u00fcr den angeforderten Zeitraum verf\u00fcgbar",
        },
        "suggestion": {
            "fr": "V\u00e9rifiez que des requ\u00eates LLM ont \u00e9t\u00e9 effectu\u00e9es r\u00e9cemment ou \u00e9largissez la fen\u00eatre temporelle",
            "en": "Check that LLM requests have been made recently or expand the time window",
            "nl": "Controleer of er recent LLM verzoeken zijn gedaan of vergroot het tijdsvenster",
            "de": "Pr\u00fcfen Sie, ob k\u00fcrzlich LLM-Anfragen gestellt wurden, oder erweitern Sie das Zeitfenster",
        },
        "doc_url": "/docs/llm-observability/troubleshooting#no-data",
    },
    ErrorCode.INVALID_SOURCE: {
        "message": {
            "fr": "Source de donn\u00e9es industrielle non reconnue",
            "en": "Unrecognized industrial data source",
            "nl": "Niet-herkende industri\u00eble gegevensbron",
            "de": "Nicht erkannte industrielle Datenquelle",
        },
        "suggestion": {
            "fr": "Utilisez une des sources support\u00e9es: scada, mes, plm, opcua",
            "en": "Use one of the supported sources: scada, mes, plm, opcua",
            "nl": "Gebruik een van de ondersteunde bronnen: scada, mes, plm, opcua",
            "de": "Verwenden Sie eine der unterst\u00fctzten Quellen: scada, mes, plm, opcua",
        },
        "doc_url": "/docs/industrial-data/sources",
    },
    ErrorCode.ALERT_THRESHOLD_EXCEEDED: {
        "message": {
            "fr": "Seuil d'alerte d\u00e9pass\u00e9",
            "en": "Alert threshold exceeded",
            "nl": "Waarschuwingsdrempel overschreden",
            "de": "Alarmgrenzwert \u00fcberschritten",
        },
        "suggestion": {
            "fr": "Consultez le dashboard LLM Observability pour plus de d\u00e9tails",
            "en": "Check the LLM Observability dashboard for more details",
            "nl": "Bekijk het LLM Observability dashboard voor meer details",
            "de": "Pr\u00fcfen Sie das LLM Observability Dashboard f\u00fcr weitere Details",
        },
        "doc_url": "/docs/llm-observability/alerts",
    },
    ErrorCode.INTERNAL_ERROR: {
        "message": {
            "fr": "Une erreur interne s'est produite",
            "en": "An internal error occurred",
            "nl": "Er is een interne fout opgetreden",
            "de": "Ein interner Fehler ist aufgetreten",
        },
        "suggestion": {
            "fr": "R\u00e9essayez dans quelques instants. Si le probl\u00e8me persiste, contactez le support",
            "en": "Retry in a few moments. If the problem persists, contact support",
            "nl": "Probeer het over enkele momenten opnieuw. Als het probleem aanhoudt, neem contact op met support",
            "de": "Versuchen Sie es in einigen Augenblicken erneut. Bei anhaltendem Problem kontaktieren Sie den Support",
        },
        "doc_url": "/docs/support",
    },
}


def get_error_detail(
    code: ErrorCode,
    lang: str = "fr",
    details: Optional[str] = None,
    **kwargs
) -> ErrorDetail:
    """
    Get localized error detail.

    Args:
        code: Error code
        lang: Language code (fr, en, nl, de)
        details: Additional details
        **kwargs: Additional context for message formatting

    Returns:
        ErrorDetail with localized message and suggestion
    """
    catalog_entry = ERROR_CATALOG.get(code, {})

    # Get localized message
    messages = catalog_entry.get("message", {})
    message = messages.get(lang, messages.get("en", f"Error: {code.value}"))

    # Get localized suggestion
    suggestions = catalog_entry.get("suggestion", {})
    suggestion = suggestions.get(lang, suggestions.get("en"))

    # Get doc URL
    doc_url = catalog_entry.get("doc_url")

    # Format message with kwargs if provided
    if kwargs:
        try:
            message = message.format(**kwargs)
        except KeyError:
            pass

    return ErrorDetail(
        code=code,
        message=message,
        details=details,
        suggestion=suggestion,
        doc_url=doc_url,
    )


class LLMObservabilityError(HTTPException):
    """Custom exception for LLM Observability errors."""

    def __init__(
        self,
        code: ErrorCode,
        status_code: int = 500,
        lang: str = "fr",
        details: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize error with standardized format.

        Args:
            code: Error code from ErrorCode enum
            status_code: HTTP status code
            lang: Language for localized message
            details: Additional error details
            **kwargs: Additional context for message formatting
        """
        self.error_detail = get_error_detail(code, lang, details, **kwargs)
        super().__init__(
            status_code=status_code,
            detail=self.error_detail.to_dict()
        )


def create_error_response(
    code: ErrorCode,
    status_code: int = 500,
    lang: str = "fr",
    details: Optional[str] = None,
    **kwargs
) -> JSONResponse:
    """
    Create a standardized error response.

    Args:
        code: Error code
        status_code: HTTP status code
        lang: Language code
        details: Additional details
        **kwargs: Additional context

    Returns:
        JSONResponse with standardized error format
    """
    error_detail = get_error_detail(code, lang, details, **kwargs)
    return JSONResponse(
        status_code=status_code,
        content={"error": error_detail.to_dict()}
    )


# Convenience functions for common errors
def module_not_available_error(lang: str = "fr") -> LLMObservabilityError:
    """Create module not available error."""
    return LLMObservabilityError(
        code=ErrorCode.MODULE_NOT_AVAILABLE,
        status_code=503,
        lang=lang,
    )


def invalid_provider_error(provider: str, lang: str = "fr") -> LLMObservabilityError:
    """Create invalid provider error."""
    return LLMObservabilityError(
        code=ErrorCode.INVALID_PROVIDER,
        status_code=400,
        lang=lang,
        details=f"Provider '{provider}' is not supported",
    )


def invalid_time_window_error(window: int, lang: str = "fr") -> LLMObservabilityError:
    """Create invalid time window error."""
    return LLMObservabilityError(
        code=ErrorCode.INVALID_TIME_WINDOW,
        status_code=400,
        lang=lang,
        details=f"Window value {window} is out of range",
    )


def no_data_error(lang: str = "fr") -> LLMObservabilityError:
    """Create no data available error."""
    return LLMObservabilityError(
        code=ErrorCode.NO_DATA_AVAILABLE,
        status_code=404,
        lang=lang,
    )


def internal_error(exception: Exception, lang: str = "fr") -> LLMObservabilityError:
    """Create internal error from exception."""
    return LLMObservabilityError(
        code=ErrorCode.INTERNAL_ERROR,
        status_code=500,
        lang=lang,
        details=str(exception),
    )
