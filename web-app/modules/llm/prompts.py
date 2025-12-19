"""
Industrial Prompts Module.

Contains system prompts and templates optimized for industrial observability,
OT/IT convergence, and manufacturing analytics contexts.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class PromptLanguage(str, Enum):
    """Supported languages for prompts."""
    FRENCH = "fr"
    ENGLISH = "en"


@dataclass
class PromptTemplate:
    """Template for a prompt with variable substitution."""
    template: str
    variables: List[str] = field(default_factory=list)
    description: str = ""

    def format(self, **kwargs) -> str:
        """Format the template with provided variables."""
        return self.template.format(**kwargs)


class IndustrialPrompts:
    """
    Collection of industrial-context prompts for the SYNAPSIX platform.

    Provides specialized prompts for:
    - Conversational analytics (NLP queries)
    - Root cause analysis
    - Predictive maintenance
    - Alarm interpretation
    - OEE analysis
    """

    # ==========================================================================
    # SYSTEM PROMPTS - Core personality and context
    # ==========================================================================

    SYSTEM_PROMPT_FR = """Tu es SYNAPSIX, un assistant IA spécialisé dans l'observabilité industrielle et l'analyse de données de production.

## Ton rôle
- Analyser les métriques de production (OEE, TRS, qualité, disponibilité, performance)
- Interpréter les données SCADA et capteurs industriels (température, pression, vibration)
- Aider à diagnostiquer les problèmes d'équipements
- Fournir des insights sur les tendances de production
- Supporter la maintenance prédictive

## Contexte technique
- Plateforme d'observabilité unifiée IT/OT
- Sources de données: VictoriaMetrics (métriques), OpenSearch (logs), OpenTelemetry (traces)
- Environnement industriel: usines, lignes de production, équipements SCADA

## Style de réponse
- Concis et factuel
- Utilise les unités appropriées (%, °C, bar, mm/s)
- Mentionne les seuils critiques quand pertinent
- Propose des actions concrètes si approprié
- Adapte le niveau technique à l'utilisateur

## Règles importantes
- Ne jamais inventer de données
- Indiquer clairement si une information est manquante
- Prioriser la sécurité industrielle dans les recommandations
- Respecter la confidentialité des données de production"""

    SYSTEM_PROMPT_EN = """You are SYNAPSIX, an AI assistant specialized in industrial observability and production data analysis.

## Your role
- Analyze production metrics (OEE, quality rate, availability, performance)
- Interpret SCADA and industrial sensor data (temperature, pressure, vibration)
- Help diagnose equipment issues
- Provide insights on production trends
- Support predictive maintenance

## Technical context
- Unified IT/OT observability platform
- Data sources: VictoriaMetrics (metrics), OpenSearch (logs), OpenTelemetry (traces)
- Industrial environment: factories, production lines, SCADA equipment

## Response style
- Concise and factual
- Use appropriate units (%, °C, bar, mm/s)
- Mention critical thresholds when relevant
- Suggest concrete actions when appropriate
- Adapt technical level to the user

## Important rules
- Never invent data
- Clearly indicate if information is missing
- Prioritize industrial safety in recommendations
- Respect production data confidentiality"""

    # ==========================================================================
    # INTENT-SPECIFIC PROMPTS
    # ==========================================================================

    METRICS_QUERY_PROMPT_FR = """Analyse la requête suivante sur les métriques de production.

Données disponibles:
{metrics_context}

Question: {query}

Fournis une réponse claire avec:
1. La valeur demandée avec son unité
2. Une comparaison avec les seuils normaux si pertinent
3. Une tendance si des données historiques sont disponibles
4. Une recommandation si la valeur est anormale"""

    METRICS_QUERY_PROMPT_EN = """Analyze the following query about production metrics.

Available data:
{metrics_context}

Question: {query}

Provide a clear answer with:
1. The requested value with its unit
2. Comparison with normal thresholds if relevant
3. Trend if historical data is available
4. Recommendation if the value is abnormal"""

    TROUBLESHOOTING_PROMPT_FR = """Tu dois aider à diagnostiquer un problème sur un équipement industriel.

Contexte de l'équipement:
{equipment_context}

Métriques actuelles:
{metrics_context}

Alarmes actives:
{alarms_context}

Question de l'opérateur: {query}

Analyse systématiquement:
1. Les symptômes observés
2. Les causes possibles (de la plus probable à la moins probable)
3. Les vérifications à effectuer
4. Les actions correctives recommandées
5. Les risques si le problème n'est pas traité"""

    TROUBLESHOOTING_PROMPT_EN = """You need to help diagnose an issue on industrial equipment.

Equipment context:
{equipment_context}

Current metrics:
{metrics_context}

Active alarms:
{alarms_context}

Operator question: {query}

Systematically analyze:
1. Observed symptoms
2. Possible causes (from most to least probable)
3. Checks to perform
4. Recommended corrective actions
5. Risks if the issue is not addressed"""

    ROOT_CAUSE_ANALYSIS_PROMPT_FR = """Effectue une analyse de cause racine pour l'incident suivant.

Incident: {incident_title}
Description: {incident_description}
Sévérité: {severity}
Détecté le: {detected_at}

Métriques au moment de l'incident:
{metrics_context}

Timeline des événements:
{timeline}

Analyse en utilisant la méthode des 5 Pourquoi et fournis:
1. La cause racine identifiée
2. Les facteurs contributifs
3. La chaîne causale complète
4. Les actions correctives immédiates
5. Les actions préventives pour éviter la récurrence"""

    ROOT_CAUSE_ANALYSIS_PROMPT_EN = """Perform a root cause analysis for the following incident.

Incident: {incident_title}
Description: {incident_description}
Severity: {severity}
Detected at: {detected_at}

Metrics at the time of incident:
{metrics_context}

Event timeline:
{timeline}

Analyze using the 5 Whys method and provide:
1. Identified root cause
2. Contributing factors
3. Complete causal chain
4. Immediate corrective actions
5. Preventive actions to avoid recurrence"""

    PREDICTIVE_MAINTENANCE_PROMPT_FR = """Analyse les données de l'équipement pour prédire les besoins de maintenance.

Équipement: {equipment_name}
Type: {equipment_type}

Métriques actuelles:
{current_metrics}

Historique des 30 derniers jours:
{historical_metrics}

Historique de maintenance:
{maintenance_history}

Fournis:
1. Score de santé global (0-100)
2. Durée de vie résiduelle estimée (RUL)
3. Anomalies détectées
4. Probabilité de panne dans les 7/30 prochains jours
5. Recommandations de maintenance priorisées"""

    PREDICTIVE_MAINTENANCE_PROMPT_EN = """Analyze equipment data to predict maintenance needs.

Equipment: {equipment_name}
Type: {equipment_type}

Current metrics:
{current_metrics}

Last 30 days history:
{historical_metrics}

Maintenance history:
{maintenance_history}

Provide:
1. Overall health score (0-100)
2. Estimated remaining useful life (RUL)
3. Detected anomalies
4. Failure probability in next 7/30 days
5. Prioritized maintenance recommendations"""

    OEE_ANALYSIS_PROMPT_FR = """Analyse les indicateurs OEE/TRS pour la période demandée.

Données OEE:
- OEE global: {oee}%
- Disponibilité: {availability}%
- Performance: {performance}%
- Qualité: {quality}%

Production:
- Produits fabriqués: {production_count}
- Défauts: {defects_count}
- Temps de cycle moyen: {cycle_time}s

Question: {query}

Fournis une analyse incluant:
1. Interprétation des valeurs actuelles
2. Identification du facteur limitant (disponibilité, performance ou qualité)
3. Comparaison avec les objectifs standard (OEE World Class: 85%)
4. Pistes d'amélioration prioritaires
5. Impact financier estimé des pertes"""

    OEE_ANALYSIS_PROMPT_EN = """Analyze OEE indicators for the requested period.

OEE Data:
- Overall OEE: {oee}%
- Availability: {availability}%
- Performance: {performance}%
- Quality: {quality}%

Production:
- Products manufactured: {production_count}
- Defects: {defects_count}
- Average cycle time: {cycle_time}s

Question: {query}

Provide an analysis including:
1. Interpretation of current values
2. Identification of the limiting factor (availability, performance, or quality)
3. Comparison with standard objectives (World Class OEE: 85%)
4. Priority improvement areas
5. Estimated financial impact of losses"""

    ALARM_INTERPRETATION_PROMPT_FR = """Interprète les alarmes actives et fournis des recommandations.

Alarmes actives:
{alarms}

Contexte des équipements:
{equipment_context}

Métriques actuelles:
{metrics_context}

Pour chaque alarme, fournis:
1. Signification et cause probable
2. Niveau de criticité réel
3. Actions immédiates requises
4. Impact potentiel sur la production
5. Corrélations avec d'autres alarmes"""

    ALARM_INTERPRETATION_PROMPT_EN = """Interpret active alarms and provide recommendations.

Active alarms:
{alarms}

Equipment context:
{equipment_context}

Current metrics:
{metrics_context}

For each alarm, provide:
1. Meaning and probable cause
2. Actual criticality level
3. Immediate required actions
4. Potential impact on production
5. Correlations with other alarms"""

    # ==========================================================================
    # RESPONSE FORMATTING PROMPTS
    # ==========================================================================

    JSON_RESPONSE_FORMAT = """Réponds uniquement avec un JSON valide suivant ce schéma:
{schema}

Ne fournis aucun texte en dehors du JSON."""

    STRUCTURED_ANSWER_FORMAT_FR = """Structure ta réponse ainsi:
## Résumé
[1-2 phrases de synthèse]

## Détails
[Analyse détaillée]

## Recommandations
[Actions suggérées]"""

    STRUCTURED_ANSWER_FORMAT_EN = """Structure your answer as follows:
## Summary
[1-2 sentence summary]

## Details
[Detailed analysis]

## Recommendations
[Suggested actions]"""

    # ==========================================================================
    # HELPER METHODS
    # ==========================================================================

    @classmethod
    def get_system_prompt(cls, language: str = "fr") -> str:
        """Get the system prompt for the specified language."""
        if language.lower() in ["fr", "french", "français"]:
            return cls.SYSTEM_PROMPT_FR
        return cls.SYSTEM_PROMPT_EN

    @classmethod
    def get_metrics_query_prompt(
        cls,
        query: str,
        metrics_context: str,
        language: str = "fr"
    ) -> str:
        """Get formatted metrics query prompt."""
        template = cls.METRICS_QUERY_PROMPT_FR if language == "fr" else cls.METRICS_QUERY_PROMPT_EN
        return template.format(
            query=query,
            metrics_context=metrics_context
        )

    @classmethod
    def get_troubleshooting_prompt(
        cls,
        query: str,
        equipment_context: str,
        metrics_context: str,
        alarms_context: str,
        language: str = "fr"
    ) -> str:
        """Get formatted troubleshooting prompt."""
        template = cls.TROUBLESHOOTING_PROMPT_FR if language == "fr" else cls.TROUBLESHOOTING_PROMPT_EN
        return template.format(
            query=query,
            equipment_context=equipment_context,
            metrics_context=metrics_context,
            alarms_context=alarms_context
        )

    @classmethod
    def get_rca_prompt(
        cls,
        incident_title: str,
        incident_description: str,
        severity: str,
        detected_at: str,
        metrics_context: str,
        timeline: str,
        language: str = "fr"
    ) -> str:
        """Get formatted root cause analysis prompt."""
        template = cls.ROOT_CAUSE_ANALYSIS_PROMPT_FR if language == "fr" else cls.ROOT_CAUSE_ANALYSIS_PROMPT_EN
        return template.format(
            incident_title=incident_title,
            incident_description=incident_description,
            severity=severity,
            detected_at=detected_at,
            metrics_context=metrics_context,
            timeline=timeline
        )

    @classmethod
    def get_predictive_prompt(
        cls,
        equipment_name: str,
        equipment_type: str,
        current_metrics: str,
        historical_metrics: str,
        maintenance_history: str,
        language: str = "fr"
    ) -> str:
        """Get formatted predictive maintenance prompt."""
        template = cls.PREDICTIVE_MAINTENANCE_PROMPT_FR if language == "fr" else cls.PREDICTIVE_MAINTENANCE_PROMPT_EN
        return template.format(
            equipment_name=equipment_name,
            equipment_type=equipment_type,
            current_metrics=current_metrics,
            historical_metrics=historical_metrics,
            maintenance_history=maintenance_history
        )

    @classmethod
    def get_oee_prompt(
        cls,
        query: str,
        oee: float,
        availability: float,
        performance: float,
        quality: float,
        production_count: int,
        defects_count: int,
        cycle_time: float,
        language: str = "fr"
    ) -> str:
        """Get formatted OEE analysis prompt."""
        template = cls.OEE_ANALYSIS_PROMPT_FR if language == "fr" else cls.OEE_ANALYSIS_PROMPT_EN
        return template.format(
            query=query,
            oee=oee,
            availability=availability,
            performance=performance,
            quality=quality,
            production_count=production_count,
            defects_count=defects_count,
            cycle_time=cycle_time
        )

    @classmethod
    def get_alarm_prompt(
        cls,
        alarms: str,
        equipment_context: str,
        metrics_context: str,
        language: str = "fr"
    ) -> str:
        """Get formatted alarm interpretation prompt."""
        template = cls.ALARM_INTERPRETATION_PROMPT_FR if language == "fr" else cls.ALARM_INTERPRETATION_PROMPT_EN
        return template.format(
            alarms=alarms,
            equipment_context=equipment_context,
            metrics_context=metrics_context
        )

    @classmethod
    def format_metrics_context(cls, metrics: Dict[str, Any]) -> str:
        """Format metrics dictionary into readable context."""
        lines = []

        business = metrics.get("business", {})
        if business:
            lines.append("## Métriques Business")
            lines.append(f"- OEE: {business.get('oee', 'N/A')}%")
            lines.append(f"- Qualité: {business.get('quality_rate', 'N/A')}%")
            lines.append(f"- Disponibilité: {business.get('availability', 'N/A')}%")
            lines.append(f"- Performance: {business.get('performance', 'N/A')}%")
            lines.append(f"- Production du jour: {business.get('production_today', 'N/A')} unités")
            lines.append(f"- Défauts: {business.get('defects_today', 'N/A')}")
            lines.append(f"- Temps de cycle: {business.get('cycle_time', 'N/A')}s")
            lines.append(f"- Alarmes critiques: {business.get('critical_alarms', 'N/A')}")

        equipment = business.get("equipment", [])
        if equipment:
            lines.append("\n## État des Équipements")
            for eq in equipment:
                status_emoji = "🟢" if eq.get("status") == "running" else "🟡" if eq.get("status") == "warning" else "🔴"
                lines.append(f"- {eq.get('name', 'Unknown')}: {status_emoji} {eq.get('status', 'N/A')}")
                if eq.get("temp"):
                    lines.append(f"  - Température: {eq.get('temp'):.1f}°C")
                if eq.get("pressure"):
                    lines.append(f"  - Pression: {eq.get('pressure'):.1f} bar")

        alarms = business.get("alarms", [])
        if alarms:
            lines.append("\n## Alarmes Actives")
            for alarm in alarms:
                severity_emoji = "🔴" if alarm.get("severity") == "critical" else "🟡"
                lines.append(f"- {severity_emoji} [{alarm.get('severity', 'info')}] {alarm.get('message', 'N/A')}")

        tech = metrics.get("tech", {})
        if tech:
            lines.append("\n## Métriques Techniques")
            lines.append(f"- Débit métriques: {tech.get('metrics_rate', 'N/A')}/s")
            lines.append(f"- Débit logs: {tech.get('logs_rate', 'N/A')}/s")
            lines.append(f"- CPU: {tech.get('cpu_usage', 'N/A')}%")
            lines.append(f"- Mémoire: {tech.get('memory_usage', 'N/A')}%")

        return "\n".join(lines)

    @classmethod
    def format_equipment_context(cls, equipment: List[Dict[str, Any]]) -> str:
        """Format equipment list into readable context."""
        lines = []
        for eq in equipment:
            lines.append(f"### {eq.get('name', 'Unknown')}")
            lines.append(f"- Statut: {eq.get('status', 'N/A')}")
            if eq.get("temp"):
                lines.append(f"- Température: {eq.get('temp'):.1f}°C")
            if eq.get("pressure"):
                lines.append(f"- Pression: {eq.get('pressure'):.1f} bar")
            if eq.get("power"):
                lines.append(f"- Puissance: {eq.get('power'):.1f} kW")
            lines.append("")
        return "\n".join(lines)

    @classmethod
    def format_alarms_context(cls, alarms: List[Dict[str, str]]) -> str:
        """Format alarms list into readable context."""
        if not alarms:
            return "Aucune alarme active"

        lines = []
        for alarm in alarms:
            severity = alarm.get("severity", "info").upper()
            message = alarm.get("message", "N/A")
            lines.append(f"- [{severity}] {message}")
        return "\n".join(lines)
