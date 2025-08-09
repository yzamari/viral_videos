"""
Interfaces module for the News Aggregator system.

This module contains all interface definitions that enforce SOLID principles
through dependency inversion and interface segregation.
"""

from .aggregator_interfaces import (
    IContentCollector,
    IContentProcessor,
    IMediaHandler,
    IVideoComposer,
    ISessionReporter,
    IAggregatorOrchestrator,
    IContentConverter
)

__all__ = [
    'IContentCollector',
    'IContentProcessor', 
    'IMediaHandler',
    'IVideoComposer',
    'ISessionReporter',
    'IAggregatorOrchestrator',
    'IContentConverter'
]