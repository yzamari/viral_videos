# Architecture Documentation with Diagrams
## Viral Video Generator System

**Version:** 1.0  
**Date:** December 2024

---

## 1. System Overview

The Viral Video Generator is a cloud-native, AI-powered system designed for automated social media video creation based on viral pattern analysis.

### 1.1 High-Level Architecture

```mermaid
graph TB
    subgraph "External Services"
        YT[YouTube API]
        TT[TikTok API]
        IG[Instagram API]
        GA[Google AI/Gemini]
        NEWS[News APIs]
    end
    
    subgraph "Application Layer"
        CLI[CLI Interface]
        API[REST API]
        WEB[Web Dashboard]
    end
    
    subgraph "Core Services"
        SCRAPER[Scraping Service]
        ANALYZER[Analysis Engine]
        DIRECTOR[Director AI]
        GENERATOR[Video Generator]
        PUBLISHER[Publishing Service]
    end
    
    subgraph "Data Layer"
        CACHE[Redis Cache]
        FS[Firestore]
        BQ[BigQuery]
        GCS[Cloud Storage]
    end
    
    YT --> SCRAPER
    TT --> SCRAPER
    IG --> SCRAPER
    NEWS --> DIRECTOR
    
    CLI --> API
    WEB --> API
    API --> SCRAPER
    API --> ANALYZER
    API --> GENERATOR
    API --> PUBLISHER
    
    SCRAPER --> CACHE
    SCRAPER --> FS
    
    ANALYZER --> GA
    ANALYZER --> FS
    ANALYZER --> BQ
    
    DIRECTOR --> GA
    DIRECTOR --> NEWS
    
    GENERATOR --> DIRECTOR
    GENERATOR --> GCS
    
    PUBLISHER --> YT
    PUBLISHER --> TT
    PUBLISHER --> IG
    
    style GA fill:#4285f4
    style GCS fill:#4285f4
    style FS fill:#f4b400
    style BQ fill:#ea4335
```

## 2. Component Architecture

### 2.1 Service Components

```mermaid
graph LR
    subgraph "Scraping Service"
        SM[Scraper Manager]
        YTS[YouTube Scraper]
        TTS[TikTok Scraper]
        IGS[Instagram Scraper]
        PS[Platform Scheduler]
    end
    
    subgraph "Analysis Engine"
        AM[Analysis Manager]
        VA[Video Analyzer]
        PA[Pattern Analyzer]
        SA[Sentiment Analyzer]
    end
    
    subgraph "Generation Pipeline"
        GM[Generation Manager]
        DIR[Director]
        SG[Script Generator]
        VE[Video Editor]
        AE[Audio Engine]
    end
    
    PS --> SM
    SM --> YTS
    SM --> TTS
    SM --> IGS
    
    AM --> VA
    AM --> PA
    AM --> SA
    
    GM --> DIR
    DIR --> SG
    GM --> VE
    GM --> AE
```

### 2.2 Data Flow Architecture

```mermaid
flowchart TD
    A[Platform APIs] -->|Raw Data| B[Scrapers]
    B -->|Structured Data| C[Data Validation]
    C -->|Valid Data| D[Storage Layer]
    C -->|Invalid Data| E[Error Queue]
    
    D --> F[Analysis Engine]
    F -->|Patterns| G[Pattern Database]
    F -->|Insights| H[Director AI]
    
    H -->|Scripts| I[Generation Pipeline]
    I -->|Videos| J[Quality Check]
    J -->|Approved| K[Publishing Queue]
    J -->|Rejected| L[Manual Review]
    
    K --> M[Platform Publishers]
    M -->|Metrics| N[Analytics Engine]
    N -->|Learnings| G
```

## 3. Detailed Component Design

### 3.1 Director AI Architecture

```mermaid
classDiagram
    class Director {
        -ai_client: GeminiClient
        -news_aggregator: NewsAggregator
        -pattern_db: PatternDatabase
        +write_script(topic, style, duration)
        +adapt_to_platform(script, platform)
        +incorporate_news(script, news_items)
        +optimize_for_virality(script)
    }
    
    class ScriptWriter {
        -hook_generator: HookGenerator
        -content_structurer: ContentStructurer
        -cta_optimizer: CTAOptimizer
        +generate_hook(topic, style)
        +structure_content(points, duration)
        +create_cta(goal)
    }
    
    class NewsAggregator {
        -sources: List[NewsSource]
        -relevance_scorer: RelevanceScorer
        +fetch_trending_news()
        +score_relevance(news, topic)
        +filter_by_category(news, category)
    }
    
    class PatternDatabase {
        -viral_patterns: Dict
        -success_metrics: Dict
        +get_patterns(category, platform)
        +update_patterns(video_id, metrics)
        +predict_success(script)
    }
    
    Director --> ScriptWriter
    Director --> NewsAggregator
    Director --> PatternDatabase
    ScriptWriter --> HookGenerator
    ScriptWriter --> ContentStructurer
    ScriptWriter --> CTAOptimizer
```

### 3.2 Error Handling Flow

```mermaid
flowchart TD
    A[Operation] --> B{Error?}
    B -->|No| C[Success]
    B -->|Yes| D[Classify Error]
    
    D --> E{Retryable?}
    E -->|Yes| F[Retry Logic]
    E -->|No| G[Log & Alert]
    
    F --> H{Max Retries?}
    H -->|No| I[Exponential Backoff]
    H -->|Yes| J[Fallback Strategy]
    
    I --> A
    
    J --> K{Has Fallback?}
    K -->|Yes| L[Execute Fallback]
    K -->|No| M[Graceful Failure]
    
    G --> N[Error Dashboard]
    M --> N
    L --> O[Degraded Service]
    
    style G fill:#ff6b6b
    style M fill:#ff6b6b
    style O fill:#ffd93d
    style C fill:#6bcf7f
```

## 4. Database Schema

### 4.1 Entity Relationship Diagram

```mermaid
erDiagram
    VIDEO ||--o{ ANALYSIS : has
    VIDEO ||--o{ PERFORMANCE : tracks
    VIDEO {
        string video_id PK
        string platform
        string url
        string title
        text description
        datetime upload_date
        int view_count
        int like_count
    }
    
    ANALYSIS ||--|| PATTERN : generates
    ANALYSIS {
        string analysis_id PK
        string video_id FK
        float viral_score
        float engagement_rate
        json content_themes
        json success_factors
    }
    
    PATTERN ||--o{ GENERATED_VIDEO : inspires
    PATTERN {
        string pattern_id PK
        string category
        json hook_types
        json content_structures
        float success_rate
    }
    
    GENERATED_VIDEO ||--o{ PERFORMANCE : measures
    GENERATED_VIDEO {
        string generated_id PK
        string pattern_id FK
        string script
        string file_path
        float predicted_score
        datetime created_at
    }
    
    PERFORMANCE {
        string perf_id PK
        string video_id FK
        datetime timestamp
        int views
        int likes
        int comments
        float actual_score
    }
```

## 5. Deployment Architecture

### 5.1 Kubernetes Deployment

```mermaid
graph TB
    subgraph "Kubernetes Cluster"
        subgraph "Ingress"
            ING[Nginx Ingress]
        end
        
        subgraph "API Layer"
            API1[API Pod 1]
            API2[API Pod 2]
            API3[API Pod 3]
        end
        
        subgraph "Worker Layer"
            W1[Scraper Worker]
            W2[Analyzer Worker]
            W3[Generator Worker 1]
            W4[Generator Worker 2]
            W5[Publisher Worker]
        end
        
        subgraph "Data Layer"
            REDIS[Redis StatefulSet]
            PV[Persistent Volumes]
        end
        
        subgraph "Monitoring"
            PROM[Prometheus]
            GRAF[Grafana]
            ELK[ELK Stack]
        end
    end
    
    ING --> API1
    ING --> API2
    ING --> API3
    
    API1 --> W1
    API2 --> W2
    API3 --> W3
    API3 --> W4
    API1 --> W5
    
    W1 --> REDIS
    W2 --> REDIS
    W3 --> PV
    W4 --> PV
    
    PROM --> GRAF
    ELK --> GRAF
```

### 5.2 CI/CD Pipeline

```mermaid
flowchart LR
    A[Git Push] --> B[GitHub Actions]
    B --> C{Tests Pass?}
    C -->|No| D[Notify Developer]
    C -->|Yes| E[Build Docker Image]
    E --> F[Push to Registry]
    F --> G[Deploy to Staging]
    G --> H{Integration Tests?}
    H -->|No| I[Rollback]
    H -->|Yes| J[Deploy to Production]
    J --> K[Health Checks]
    K -->|Fail| L[Automatic Rollback]
    K -->|Pass| M[Update Complete]
    
    style D fill:#ff6b6b
    style I fill:#ff6b6b
    style L fill:#ff6b6b
    style M fill:#6bcf7f
```

## 6. Security Architecture

### 6.1 Security Layers

```mermaid
graph TB
    subgraph "External Layer"
        CF[CloudFlare DDoS]
        WAF[Web Application Firewall]
    end
    
    subgraph "Network Layer"
        VPC[Virtual Private Cloud]
        SG[Security Groups]
        NACL[Network ACLs]
    end
    
    subgraph "Application Layer"
        AUTH[Authentication Service]
        AUTHZ[Authorization Service]
        VAULT[Secret Manager]
    end
    
    subgraph "Data Layer"
        ENC[Encryption at Rest]
        TLS[TLS in Transit]
        IAM[IAM Policies]
    end
    
    CF --> WAF
    WAF --> VPC
    VPC --> SG
    SG --> NACL
    
    AUTH --> VAULT
    AUTHZ --> VAULT
    
    ENC --> IAM
    TLS --> IAM
    
    style CF fill:#ff9800
    style WAF fill:#ff9800
    style VAULT fill:#4caf50
    style ENC fill:#2196f3
    style TLS fill:#2196f3
```

## 7. Monitoring Architecture

### 7.1 Observability Stack

```mermaid
graph TB
    subgraph "Applications"
        APP[Application Pods]
        SVC[Services]
    end
    
    subgraph "Metrics Collection"
        PROM[Prometheus]
        NODE[Node Exporter]
        CADV[cAdvisor]
    end
    
    subgraph "Logging"
        FLUENT[Fluentd]
        ES[Elasticsearch]
        KB[Kibana]
    end
    
    subgraph "Tracing"
        JAEGER[Jaeger]
        TRACE[Trace Collector]
    end
    
    subgraph "Visualization"
        GRAF[Grafana]
        ALERT[AlertManager]
    end
    
    APP --> PROM
    APP --> FLUENT
    APP --> TRACE
    
    SVC --> NODE
    SVC --> CADV
    
    FLUENT --> ES
    ES --> KB
    
    TRACE --> JAEGER
    
    PROM --> GRAF
    JAEGER --> GRAF
    KB --> GRAF
    
    GRAF --> ALERT
```

## 8. Performance Architecture

### 8.1 Caching Strategy

```mermaid
flowchart TD
    A[Request] --> B{Cache Hit?}
    B -->|Yes| C[Return Cached]
    B -->|No| D[Fetch from Source]
    
    D --> E[Process Data]
    E --> F[Update Cache]
    F --> G[Set TTL]
    
    G --> H{Data Type?}
    H -->|Trending| I[TTL: 1 hour]
    H -->|Analysis| J[TTL: 24 hours]
    H -->|Static| K[TTL: 7 days]
    
    I --> L[Return Response]
    J --> L
    K --> L
    C --> L
    
    subgraph "Cache Layers"
        L1[Browser Cache]
        L2[CDN Cache]
        L3[Redis Cache]
        L4[Application Cache]
    end
```

### 8.2 Load Balancing

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[HAProxy/Nginx]
    end
    
    subgraph "Health Checks"
        HC[Health Monitor]
    end
    
    subgraph "API Servers"
        API1[Server 1<br/>Weight: 1]
        API2[Server 2<br/>Weight: 1]
        API3[Server 3<br/>Weight: 2]
    end
    
    subgraph "Strategies"
        RR[Round Robin]
        LC[Least Connections]
        IP[IP Hash]
    end
    
    LB --> RR
    LB --> LC
    LB --> IP
    
    HC --> API1
    HC --> API2
    HC --> API3
    
    RR --> API1
    RR --> API2
    RR --> API3
    
    style API1 fill:#6bcf7f
    style API2 fill:#6bcf7f
    style API3 fill:#4caf50
```

## 9. Disaster Recovery

### 9.1 Backup Strategy

```mermaid
flowchart LR
    A[Production Data] --> B[Continuous Replication]
    B --> C[Primary Backup]
    C --> D[Daily Snapshots]
    D --> E[Weekly Archives]
    E --> F[Monthly Archives]
    
    C --> G[Hot Standby]
    D --> H[Warm Storage]
    F --> I[Cold Storage]
    
    subgraph "Recovery Times"
        G -->|RTO: 1hr| J[Failover]
        H -->|RTO: 4hr| K[Restore]
        I -->|RTO: 24hr| L[Archive Restore]
    end
    
    style G fill:#ff5252
    style H fill:#ffb74d
    style I fill:#64b5f6
```

---

**Document Version History:**
- v1.0 - Initial architecture documentation
- Next Review: Q1 2025 