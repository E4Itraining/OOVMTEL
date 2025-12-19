"""
Assistant Personas Module.

Defines different personas for the SYNAPSIX AI assistant,
allowing adaptive communication styles based on user role and context.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum


class PersonaType(str, Enum):
    """Types of assistant personas."""
    EXPERT = "expert"           # Technical expert mode
    OPERATOR = "operator"       # Simplified for shop floor
    MANAGER = "manager"         # Business-focused
    MAINTENANCE = "maintenance" # Maintenance technician focus
    ANALYST = "analyst"         # Data analysis focus
    SAFETY = "safety"           # Safety officer focus
    DEFAULT = "default"         # Balanced default


@dataclass
class Persona:
    """Definition of an assistant persona."""
    name: str
    type: PersonaType
    description: str
    tone: str
    vocabulary_level: str  # simple, moderate, technical
    focus_areas: List[str] = field(default_factory=list)
    response_style: str = ""
    emoji_usage: bool = True
    max_response_length: str = "medium"  # short, medium, long
    include_explanations: bool = True
    include_recommendations: bool = True

    def get_style_instructions(self, language: str = "fr") -> str:
        """Get persona-specific style instructions."""
        if language == "fr":
            return self._get_french_instructions()
        return self._get_english_instructions()

    def _get_french_instructions(self) -> str:
        base = f"\n## Style de communication: {self.name}\n"
        base += f"- Ton: {self.tone}\n"
        base += f"- Niveau de vocabulaire: {self.vocabulary_level}\n"

        if self.focus_areas:
            base += f"- Focus prioritaire: {', '.join(self.focus_areas)}\n"

        if self.response_style:
            base += f"- Style de réponse: {self.response_style}\n"

        length_map = {"short": "courtes", "medium": "modérées", "long": "détaillées"}
        base += f"- Longueur des réponses: {length_map.get(self.max_response_length, 'modérées')}\n"

        if self.include_explanations:
            base += "- Inclure des explications pédagogiques\n"
        if self.include_recommendations:
            base += "- Toujours proposer des recommandations actionnables\n"

        return base

    def _get_english_instructions(self) -> str:
        base = f"\n## Communication style: {self.name}\n"
        base += f"- Tone: {self.tone}\n"
        base += f"- Vocabulary level: {self.vocabulary_level}\n"

        if self.focus_areas:
            base += f"- Priority focus: {', '.join(self.focus_areas)}\n"

        if self.response_style:
            base += f"- Response style: {self.response_style}\n"

        base += f"- Response length: {self.max_response_length}\n"

        if self.include_explanations:
            base += "- Include educational explanations\n"
        if self.include_recommendations:
            base += "- Always provide actionable recommendations\n"

        return base


class PersonaManager:
    """
    Manages assistant personas for adaptive communication.

    Features:
    - Automatic persona detection based on query context
    - Manual persona override
    - Persona-specific response formatting
    """

    # Pre-defined personas
    PERSONAS: Dict[PersonaType, Persona] = {
        PersonaType.DEFAULT: Persona(
            name="SYNAPSIX Standard",
            type=PersonaType.DEFAULT,
            description="Balanced assistant for general industrial queries",
            tone="Professionnel et accessible",
            vocabulary_level="moderate",
            focus_areas=["métriques de production", "état des équipements", "alertes"],
            response_style="Concis avec détails si nécessaire",
            emoji_usage=True,
            include_explanations=True,
            include_recommendations=True
        ),

        PersonaType.EXPERT: Persona(
            name="Expert Technique",
            type=PersonaType.EXPERT,
            description="Deep technical analysis mode",
            tone="Technique et précis",
            vocabulary_level="technical",
            focus_areas=["analyse approfondie", "données techniques", "corrélations", "métriques avancées"],
            response_style="Détaillé avec données brutes et formules",
            emoji_usage=False,
            max_response_length="long",
            include_explanations=False,
            include_recommendations=True
        ),

        PersonaType.OPERATOR: Persona(
            name="Assistant Opérateur",
            type=PersonaType.OPERATOR,
            description="Simplified mode for production floor operators",
            tone="Simple et direct",
            vocabulary_level="simple",
            focus_areas=["actions immédiates", "alertes critiques", "procédures"],
            response_style="Court et actionnable, étapes numérotées",
            emoji_usage=True,
            max_response_length="short",
            include_explanations=False,
            include_recommendations=True
        ),

        PersonaType.MANAGER: Persona(
            name="Business Intelligence",
            type=PersonaType.MANAGER,
            description="Business-focused insights for management",
            tone="Professionnel et orienté business",
            vocabulary_level="moderate",
            focus_areas=["KPIs", "OEE", "productivité", "coûts", "tendances"],
            response_style="Synthétique avec indicateurs clés et impacts business",
            emoji_usage=True,
            max_response_length="medium",
            include_explanations=True,
            include_recommendations=True
        ),

        PersonaType.MAINTENANCE: Persona(
            name="Expert Maintenance",
            type=PersonaType.MAINTENANCE,
            description="Maintenance technician focused assistance",
            tone="Technique mais pratique",
            vocabulary_level="technical",
            focus_areas=["diagnostic", "maintenance préventive", "pièces détachées", "procédures"],
            response_style="Procédural avec check-lists et références techniques",
            emoji_usage=True,
            max_response_length="medium",
            include_explanations=True,
            include_recommendations=True
        ),

        PersonaType.ANALYST: Persona(
            name="Analyste de Données",
            type=PersonaType.ANALYST,
            description="Data analysis and statistics focused",
            tone="Analytique et objectif",
            vocabulary_level="technical",
            focus_areas=["statistiques", "corrélations", "anomalies", "tendances", "prédictions"],
            response_style="Structuré avec données chiffrées et visualisations",
            emoji_usage=False,
            max_response_length="long",
            include_explanations=True,
            include_recommendations=True
        ),

        PersonaType.SAFETY: Persona(
            name="Responsable Sécurité",
            type=PersonaType.SAFETY,
            description="Safety officer focused assistance",
            tone="Rigoureux et prudent",
            vocabulary_level="moderate",
            focus_areas=["sécurité", "risques", "conformité", "incidents", "procédures d'urgence"],
            response_style="Priorisation des risques avec actions préventives",
            emoji_usage=True,
            max_response_length="medium",
            include_explanations=True,
            include_recommendations=True
        )
    }

    # Keywords for automatic persona detection
    PERSONA_KEYWORDS: Dict[str, Dict[PersonaType, List[str]]] = {
        "fr": {
            PersonaType.EXPERT: [
                "technique", "détaillé", "approfondi", "analyse complète",
                "données brutes", "corrélation", "formule"
            ],
            PersonaType.OPERATOR: [
                "que faire", "procédure", "urgent", "immédiat",
                "simple", "étapes", "action"
            ],
            PersonaType.MANAGER: [
                "coût", "budget", "kpi", "rendement", "productivité",
                "objectif", "performance globale", "rapport"
            ],
            PersonaType.MAINTENANCE: [
                "maintenance", "réparation", "pièce", "intervention",
                "préventif", "diagnostic", "panne"
            ],
            PersonaType.ANALYST: [
                "statistique", "corrélation", "tendance", "analyse",
                "prédiction", "anomalie", "pattern"
            ],
            PersonaType.SAFETY: [
                "sécurité", "risque", "danger", "incident", "urgence",
                "conformité", "protection", "accident"
            ]
        },
        "en": {
            PersonaType.EXPERT: [
                "technical", "detailed", "in-depth", "complete analysis",
                "raw data", "correlation", "formula"
            ],
            PersonaType.OPERATOR: [
                "what to do", "procedure", "urgent", "immediate",
                "simple", "steps", "action"
            ],
            PersonaType.MANAGER: [
                "cost", "budget", "kpi", "yield", "productivity",
                "target", "overall performance", "report"
            ],
            PersonaType.MAINTENANCE: [
                "maintenance", "repair", "part", "intervention",
                "preventive", "diagnostic", "breakdown"
            ],
            PersonaType.ANALYST: [
                "statistic", "correlation", "trend", "analysis",
                "prediction", "anomaly", "pattern"
            ],
            PersonaType.SAFETY: [
                "safety", "risk", "danger", "incident", "emergency",
                "compliance", "protection", "accident"
            ]
        }
    }

    def __init__(self, default_persona: PersonaType = PersonaType.DEFAULT):
        """Initialize the persona manager."""
        self.current_persona = self.PERSONAS[default_persona]
        self._user_preferences: Dict[str, PersonaType] = {}

    def get_persona(self, persona_type: PersonaType) -> Persona:
        """Get a specific persona."""
        return self.PERSONAS.get(persona_type, self.PERSONAS[PersonaType.DEFAULT])

    def set_persona(self, persona_type: PersonaType) -> Persona:
        """Set the current persona."""
        self.current_persona = self.get_persona(persona_type)
        return self.current_persona

    def detect_persona(self, query: str, language: str = "fr") -> Persona:
        """
        Automatically detect the best persona based on query content.

        Args:
            query: User's query text
            language: Language code (fr/en)

        Returns:
            Most appropriate persona for the query
        """
        query_lower = query.lower()
        keywords = self.PERSONA_KEYWORDS.get(language, self.PERSONA_KEYWORDS["fr"])

        # Score each persona type
        scores: Dict[PersonaType, int] = {}
        for persona_type, keywords_list in keywords.items():
            score = sum(1 for kw in keywords_list if kw in query_lower)
            if score > 0:
                scores[persona_type] = score

        # Return highest scoring persona or default
        if scores:
            best_type = max(scores, key=scores.get)
            return self.PERSONAS[best_type]

        return self.PERSONAS[PersonaType.DEFAULT]

    def set_user_preference(self, user_id: str, persona_type: PersonaType):
        """Set a user's preferred persona."""
        self._user_preferences[user_id] = persona_type

    def get_user_persona(self, user_id: str) -> Optional[Persona]:
        """Get a user's preferred persona if set."""
        pref = self._user_preferences.get(user_id)
        if pref:
            return self.PERSONAS[pref]
        return None

    def get_system_prompt_modifier(
        self,
        persona: Persona,
        language: str = "fr"
    ) -> str:
        """
        Generate system prompt modification for a persona.

        Args:
            persona: The persona to use
            language: Response language

        Returns:
            Additional prompt text to append to system prompt
        """
        return persona.get_style_instructions(language)

    def format_response(
        self,
        content: str,
        persona: Persona,
        language: str = "fr"
    ) -> str:
        """
        Format a response according to persona style.

        Args:
            content: Raw response content
            persona: The persona to use for formatting
            language: Response language

        Returns:
            Formatted response
        """
        # Add persona-specific formatting
        if persona.max_response_length == "short" and len(content) > 500:
            # Truncate for operator mode
            lines = content.split('\n')
            important_lines = [l for l in lines if l.strip() and not l.startswith('##')][:5]
            content = '\n'.join(important_lines)

            suffix = "\n\n💡 " if persona.emoji_usage else "\n\n"
            suffix += "Pour plus de détails, consultez le tableau de bord." if language == "fr" else "For more details, check the dashboard."
            content += suffix

        return content


# Global persona manager instance
_persona_manager: Optional[PersonaManager] = None


def get_persona_manager() -> PersonaManager:
    """Get or create the global persona manager."""
    global _persona_manager
    if _persona_manager is None:
        _persona_manager = PersonaManager()
    return _persona_manager
