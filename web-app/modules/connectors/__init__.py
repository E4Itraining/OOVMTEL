"""
ERP/MES Connectors Module
Industrial system integration connectors for SYNAPSIX
"""

from .base import BaseConnector, ConnectorConfig, ConnectionStatus
from .sap import SAPConnector, SAPConfig
from .kepware import KEPWAREConnector, KEPWAREConfig
from .factorytalk import FactoryTalkConnector, FactoryTalkConfig
from .models import (
    ConnectorType,
    DataMapping,
    SyncConfig,
    SyncResult,
    ERPData,
    MESData,
)

__all__ = [
    # Base
    'BaseConnector',
    'ConnectorConfig',
    'ConnectionStatus',
    # SAP
    'SAPConnector',
    'SAPConfig',
    # KEPWARE
    'KEPWAREConnector',
    'KEPWAREConfig',
    # FactoryTalk
    'FactoryTalkConnector',
    'FactoryTalkConfig',
    # Models
    'ConnectorType',
    'DataMapping',
    'SyncConfig',
    'SyncResult',
    'ERPData',
    'MESData',
]
