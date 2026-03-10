# 🏗️ System Architecture - Agricultural News Backend

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AGRICULTURAL NEWS BACKEND                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Timer     │    │  Manual     │    │   Health    │         │
│  │ (3 hours)   │───▶│  Trigger    │───▶│   Check     │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              SCHEDULER SERVICE                              │ │
│  │  • Background thread management                             │ │
│  │  • Job scheduling (3hr, daily, hourly)                     │ │
│  │  • Error handling & recovery                               │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │               SCRAPER SERVICE                               │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │ │
│  │  │PIB Agri     │  │   eNAM      │  │ MyScheme    │         │ │
│  │  │Scraper      │  │  Scraper    │  │ Scraper     │         │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘         │ │
│  │         │                 │                 │               │ │
│  │         ▼                 ▼                 ▼               │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │            RAW NEWS ITEMS                               │ │ │
│  │  │  • News articles  • Market prices  • Gov schemes       │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                GEMINI AI SERVICE                            │ │
│  │                                                             │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │ │
│  │  │Multilingual │  │  Content    │  │   Image     │         │ │
│  │  │Translation  │  │Enhancement  │  │  Discovery  │         │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘         │ │
│  │         │                 │                 │               │ │
│  │         └─────────────────┼─────────────────┘               │ │
│  │                           ▼                                 │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │           ENHANCED NEWS ITEMS                           │ │ │
│  │  │  • 3-language titles/summaries                          │ │ │
│  │  │  • Relevant images                                      │ │ │
│  │  │  • Structured data                                      │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │              FIRESTORE SERVICE                              │ │
│  │                                                             │ │
│  │  ┌─────────────────────────────────────────────────────────┐ │ │
│  │  │                FIRESTORE DATABASE                       │ │ │
│  │  │                                                         │ │ │
│  │  │  📁 news (unified collection)                           │ │ │
│  │  │  ├── 🏷️ category: "news"                               │ │ │
│  │  │  ├── 🏷️ category: "price"                              │ │ │
│  │  │  └── 🏷️ category: "scheme"                             │ │ │
│  │  │                                                         │ │ │
│  │  │  📁 scraping_status                                     │ │ │
│  │  │  └── 📄 current pipeline status                        │ │ │
│  │  └─────────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                              │                                  │
│                              ▼                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                 FASTAPI ENDPOINTS                           │ │
│  │                                                             │ │
│  │  GET  /           │  Health check                           │ │
│  │  GET  /news       │  Retrieve processed news               │ │
│  │  POST /scrape     │  Manual trigger scraping               │ │
│  │  GET  /scraping-status │ Check pipeline status             │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REACT FRONTEND                               │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    News     │  │   Prices    │  │  Schemes    │             │
│  │     Tab     │  │     Tab     │  │     Tab     │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  • Real-time Firestore listeners                               │
│  • Multilingual content display                                │
│  • Category-based filtering                                    │
│  • Responsive image loading                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Component Responsibilities

### 🕐 Scheduler Service
- **Purpose**: Orchestrates automated data pipeline
- **Key Features**:
  - Background thread management
  - Multiple job scheduling (3hr scraping, daily cleanup)
  - Error recovery and retry logic
  - Status monitoring and reporting

### 🕷️ Scraper Service  
- **Purpose**: Collects raw data from multiple sources
- **Data Sources**:
  - **PIB Agriculture**: Government agricultural news
  - **eNAM**: Market commodity prices
  - **MyScheme**: Government farmer schemes
- **Output**: Structured raw news items

### 🤖 Gemini AI Service
- **Purpose**: Enhances raw content with AI
- **Capabilities**:
  - Multilingual translation (English, Hindi, Telugu)
  - Content improvement and summarization
  - Relevant image discovery via Unsplash
  - Data validation and formatting

### 💾 Firestore Service
- **Purpose**: Manages data persistence and retrieval
- **Collections**:
  - `news`: Unified collection with category filtering
  - `scraping_status`: Pipeline status tracking
- **Features**: Real-time updates, batch operations, cleanup

### 🌐 FastAPI Application
- **Purpose**: Provides REST API interface
- **Endpoints**: Health checks, data retrieval, manual triggers
- **Features**: CORS support, background tasks, error handling

## Data Flow Timing

```
Time: 00:00 ────────────────────────────────────────────────────▶
      │     3hr     │     3hr     │     3hr     │     3hr     │
      ▼             ▼             ▼             ▼             ▼
   Scrape        Scrape        Scrape        Scrape        Scrape
   Process       Process       Process       Process       Process
   Store         Store         Store         Store         Store
   Update        Update        Update        Update        Update
      │             │             │             │             │
      ▼             ▼             ▼             ▼             ▼
   Frontend      Frontend      Frontend      Frontend      Frontend
   Updates       Updates       Updates       Updates       Updates
```

## Error Handling Strategy

```
┌─────────────────┐
│   Error Occurs  │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Log Error      │
│  Update Status  │
└─────────────────┘
         │
         ▼
┌─────────────────┐    Yes    ┌─────────────────┐
│  Retryable?     │──────────▶│  Retry with     │
│                 │           │  Backoff        │
└─────────────────┘           └─────────────────┘
         │ No                          │
         ▼                             ▼
┌─────────────────┐           ┌─────────────────┐
│  Mark as Failed │           │  Success?       │
│  Continue       │           └─────────────────┘
└─────────────────┘                    │ No
                                       ▼
                              ┌─────────────────┐
                              │  Mark as Failed │
                              │  Continue       │
                              └─────────────────┘
```

## Scalability Considerations

### Horizontal Scaling
- Multiple scraper instances for different sources
- Load balancing for API endpoints
- Firestore automatic scaling

### Performance Optimization
- Async/await for concurrent operations
- Batch processing for Firestore operations
- Caching for frequently accessed data
- Background task queuing

### Resource Management
- Connection pooling for HTTP requests
- Memory-efficient data processing
- Graceful shutdown handling
- Health monitoring and alerting

This architecture ensures reliable, scalable, and maintainable agricultural news aggregation with real-time updates to your frontend application.