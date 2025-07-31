"""News Aggregator Models"""

from .content_models import (
    SourceType,
    AssetType,
    ContentStatus,
    NewsSource,
    MediaAsset,
    TimeSegment,
    ContentItem,
    ContentCollection,
    ScrapingConfig
)

from .composition_models import (
    LayerType,
    TransitionType,
    PresenterStyle,
    VideoLayer,
    TransitionEffect,
    ThemeConfig,
    NewsTemplate,
    CompositionProject
)

from .aggregation_models import (
    AggregationRule,
    ContentFilter,
    ChannelConfig,
    AggregationSession
)

__all__ = [
    # Content Models
    'SourceType',
    'AssetType',
    'ContentStatus',
    'NewsSource',
    'MediaAsset',
    'TimeSegment',
    'ContentItem',
    'ContentCollection',
    'ScrapingConfig',
    
    # Composition Models
    'LayerType',
    'TransitionType',
    'PresenterStyle',
    'VideoLayer',
    'TransitionEffect',
    'ThemeConfig',
    'NewsTemplate',
    'CompositionProject',
    
    # Aggregation Models
    'AggregationRule',
    'ContentFilter',
    'ChannelConfig',
    'AggregationSession'
]