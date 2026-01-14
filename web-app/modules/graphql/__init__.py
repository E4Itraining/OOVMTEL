"""
GraphQL Module for OOVMTEL Unified View
Flexible querying API with Strawberry GraphQL
"""

from .schema import schema, get_graphql_router

__all__ = ["schema", "get_graphql_router"]
