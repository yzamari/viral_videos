# Datasources Feature Design Document

## Overview

The datasources feature will enable ViralAI to create videos based on external data sources, allowing users to generate content about custom subjects with custom knowledge. This feature will support various input formats and integrate seamlessly with the existing AI agent system.

## Use Cases

1. **News Aggregation**: Generate videos from a list of news items with humorous commentary
2. **Research Content**: Create educational videos from research papers or documentation
3. **Event Coverage**: Generate videos about events using event descriptions and data
4. **Product Reviews**: Create review videos using product specifications and user feedback
5. **Historical Content**: Generate videos about historical events using source documents
6. **Custom Knowledge**: Create videos using proprietary or specialized knowledge bases

## Architecture Design

### 1. Datasource Types

```python
class DatasourceType(Enum):
    TEXT_FILE = "text_file"           # Single text file
    TEXT_LIST = "text_list"           # File with list of items
    FOLDER = "folder"                 # Directory of files
    JSON = "json"                     # Structured JSON data
    CSV = "csv"                       # Tabular data
    URL = "url"                       # Web content
    API = "api"                       # API endpoint
```

### 2. Core Components

#### A. DatasourceManager
```python
class DatasourceManager:
    """Manages datasource loading and preprocessing"""
    
    def __init__(self):
        self.loaders = {
            DatasourceType.TEXT_FILE: TextFileLoader(),
            DatasourceType.FOLDER: FolderLoader(),
            DatasourceType.JSON: JsonLoader(),
            DatasourceType.CSV: CsvLoader(),
            DatasourceType.URL: UrlLoader(),
        }
    
    async def load_datasource(self, config: DatasourceConfig) -> DatasourceContent:
        """Load and preprocess datasource based on type"""
        pass
```

#### B. DatasourceConfig
```python
@dataclass
class DatasourceConfig:
    """Configuration for datasource"""
    source_type: DatasourceType
    source_path: str  # File path, folder path, or URL
    
    # Processing options
    item_selector: Optional[str] = None  # For selecting specific items
    content_filter: Optional[str] = None  # Filter criteria
    max_items: Optional[int] = None      # Limit number of items
    
    # Transformation options
    extract_topics: bool = True          # Extract main topics
    summarize: bool = False              # Summarize long content
    chunk_size: Optional[int] = None     # For chunking large content
    
    # Context options
    context_template: Optional[str] = None  # How to format for AI
    include_metadata: bool = True           # Include source metadata
```

#### C. DatasourceContent
```python
@dataclass
class DatasourceContent:
    """Processed datasource content"""
    items: List[ContentItem]
    metadata: Dict[str, Any]
    summary: Optional[str]
    topics: List[str]
    total_tokens: int
```

### 3. Integration Points

#### A. CLI Integration
```bash
# Single file datasource
python main.py generate \
  --datasource news.txt \
  --datasource-type text_list \
  --mission "Create humorous commentary about these news items"

# Folder datasource
python main.py generate \
  --datasource ./research_papers/ \
  --datasource-type folder \
  --mission "Explain these research findings in simple terms"

# JSON datasource with filtering
python main.py generate \
  --datasource products.json \
  --datasource-type json \
  --item-selector "products[?rating > 4]" \
  --mission "Review top-rated products"
```

#### B. AI Agent Integration

The datasource content will be injected into the AI agent context:

```python
class WorkingOrchestrator:
    async def orchestrate_generation(self, config, datasource_content=None):
        if datasource_content:
            # Inject datasource into agent context
            enhanced_mission = self._enhance_mission_with_datasource(
                config.mission, 
                datasource_content
            )
            
            # AI agents will have access to datasource content
            self.agent_context.datasource = datasource_content
```

### 4. Content Processing Pipeline

```
1. Load Raw Data
   ↓
2. Parse & Structure
   ↓
3. Filter & Select
   ↓
4. Extract Topics/Entities
   ↓
5. Summarize if needed
   ↓
6. Format for AI Context
   ↓
7. Inject into Mission
```

### 5. Example Implementations

#### A. News List Processor
```python
class NewsListProcessor:
    async def process(self, file_path: str) -> List[ContentItem]:
        """Process a text file with news items"""
        items = []
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip():
                    items.append(ContentItem(
                        content=line.strip(),
                        type="news_item",
                        metadata={"source": "news_list"}
                    ))
        return items
```

#### B. Research Folder Processor
```python
class ResearchFolderProcessor:
    async def process(self, folder_path: str) -> List[ContentItem]:
        """Process folder of research documents"""
        items = []
        for file in Path(folder_path).glob("*.pdf"):
            content = await self._extract_pdf_content(file)
            summary = await self._summarize_document(content)
            items.append(ContentItem(
                content=summary,
                type="research_paper",
                metadata={
                    "source": str(file),
                    "title": self._extract_title(content)
                }
            ))
        return items
```

### 6. Smart Context Injection

The system will intelligently inject datasource content based on the video type:

```python
class ContextInjector:
    def inject_for_news_commentary(self, mission: str, news_items: List[str]) -> str:
        """Inject news items for commentary"""
        return f"""
        {mission}
        
        NEWS ITEMS TO COMMENT ON:
        {chr(10).join(f"- {item}" for item in news_items)}
        
        Create humorous commentary connecting these items.
        """
    
    def inject_for_educational(self, mission: str, research: List[Dict]) -> str:
        """Inject research for educational content"""
        return f"""
        {mission}
        
        RESEARCH FINDINGS:
        {self._format_research(research)}
        
        Explain these findings in an engaging, accessible way.
        """
```

### 7. Token Management

To handle large datasources efficiently:

```python
class TokenManager:
    def __init__(self, max_tokens: int = 50000):
        self.max_tokens = max_tokens
    
    async def optimize_content(self, content: DatasourceContent) -> DatasourceContent:
        """Optimize content to fit within token limits"""
        if content.total_tokens > self.max_tokens:
            # Summarize or chunk content
            return await self._smart_reduction(content)
        return content
```

### 8. Security Considerations

1. **File Access**: Validate file paths and permissions
2. **URL Fetching**: Implement rate limiting and domain whitelisting
3. **Content Sanitization**: Clean potentially harmful content
4. **Size Limits**: Enforce maximum file/folder sizes
5. **Format Validation**: Validate file formats before processing

### 9. Error Handling

```python
class DatasourceError(Exception):
    """Base exception for datasource errors"""
    pass

class DatasourceNotFoundError(DatasourceError):
    """Datasource file/folder not found"""
    pass

class DatasourceFormatError(DatasourceError):
    """Invalid datasource format"""
    pass

class DatasourceSizeError(DatasourceError):
    """Datasource exceeds size limits"""
    pass
```

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
- [ ] Create DatasourceManager and basic loaders
- [ ] Implement DatasourceConfig and validation
- [ ] Add CLI argument parsing
- [ ] Create unit tests for loaders

### Phase 2: Content Processors (Week 2)
- [ ] Implement text file processor
- [ ] Implement folder processor
- [ ] Implement JSON/CSV processors
- [ ] Add content filtering and selection

### Phase 3: AI Integration (Week 3)
- [ ] Integrate with WorkingOrchestrator
- [ ] Implement context injection strategies
- [ ] Add token management
- [ ] Test with AI agents

### Phase 4: Advanced Features (Week 4)
- [ ] Add URL/web content support
- [ ] Implement smart summarization
- [ ] Add topic extraction
- [ ] Create example scripts

## Usage Examples

### Example 1: News Commentary
```bash
# news.txt contains:
# Tech company announces AI breakthrough
# Local man finds potato that looks like celebrity
# Scientists discover new species of bacteria

python main.py generate \
  --datasource news.txt \
  --datasource-type text_list \
  --mission "Create Family Guy style commentary connecting these news items" \
  --platform youtube \
  --duration 60
```

### Example 2: Research Summary
```bash
python main.py generate \
  --datasource ./papers/ \
  --datasource-type folder \
  --mission "Explain the key findings from these research papers" \
  --visual-style "educational" \
  --platform youtube \
  --duration 120
```

### Example 3: Product Reviews
```bash
python main.py generate \
  --datasource products.json \
  --datasource-type json \
  --item-selector ".products[:5]" \
  --mission "Review these products with brutal honesty" \
  --tone "sarcastic" \
  --platform tiktok
```

## Benefits

1. **Flexibility**: Support for multiple data formats and sources
2. **Scalability**: Can handle large datasets with smart chunking
3. **Integration**: Seamless integration with existing AI agent system
4. **Customization**: Flexible filtering and transformation options
5. **Context-Aware**: Smart injection based on content type
6. **Security**: Built-in validation and sanitization

## Future Enhancements

1. **Live Data**: Support for real-time data streams
2. **Multi-Source**: Combine multiple datasources
3. **AI Preprocessing**: Use AI to clean and structure data
4. **Template Library**: Pre-built templates for common use cases
5. **Visual Data**: Support for image/video datasources
6. **Knowledge Graphs**: Build relationships between data points

## Conclusion

The datasources feature will transform ViralAI into a powerful content generation platform that can create videos from any knowledge source. By providing flexible input options and intelligent processing, users can generate highly customized, data-driven content while maintaining the creative capabilities of the AI agent system.