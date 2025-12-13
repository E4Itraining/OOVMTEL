"""
OOVMTEL NLP/Conversational Analytics Module

This module provides natural language query capabilities for industrial observability data.
Operators can ask questions in plain French or English instead of writing PromQL/SQL queries.

Features:
- Intent detection (metrics, alerts, comparison, troubleshooting)
- Entity extraction (equipment, time ranges, KPIs)
- Query generation (PromQL, OpenSearch queries)
- Response generation with visualizations
- Context-aware follow-up questions
"""

from .engine import NLPEngine
from .models import (
    ConversationalQuery,
    QueryIntent,
    ExtractedEntities,
    QueryResult,
    SuggestedVisualization,
    ConversationContext
)
from .query_generator import QueryGenerator
from .response_builder import ResponseBuilder

__all__ = [
    'NLPEngine',
    'ConversationalQuery',
    'QueryIntent',
    'ExtractedEntities',
    'QueryResult',
    'SuggestedVisualization',
    'ConversationContext',
    'QueryGenerator',
    'ResponseBuilder',
]
