# Mermaid Diagram Demo - 15 Diagram Types with Examples

Complete reference for all Mermaid diagram types following proper syntax.

---

## 1. Module Graph (LR)

### Example 1.1: Simple Module Dependencies

```mermaid
graph LR
    A["Core Module"] --> B["Utils Module"]
    A --> C["Config Module"]
    D["API Layer"] --> A
    D --> E["Middleware"]
    E --> C
    F["Tests"] --> A
```

### Example 1.2: Layered Architecture

```mermaid
graph LR
    subgraph "Frontend"
        A["React App"]
        B["Vue App"]
    end

    A --> C["API Gateway"]
    B --> C
    C --> D["Service A"]
    C --> E["Service B"]
```

---

## 2. Graph (TD) - Dependency Diagram

### Example 2.1: Application Dependencies

```mermaid
graph TD
    A["Application"] --> B["Core Library 1"]
    A --> C["Core Library 2"]
    B --> D["Utility Library"]
    C --> D
    B --> E["Third-party API"]
    C --> F["Database Driver"]

    style A fill:#f9f,stroke:#333
    style B fill:#bbf,stroke:#333
    style C fill:#bbf,stroke:#333
```

### Example 2.2: Tech Stack Layers

```mermaid
graph TD
    A["Web App"] --> B["Frontend Framework"]
    A --> C["Backend API"]
    B --> D["UI Components"]
    C --> E["Business Logic"]
    C --> F["Data Access"]
    F --> G["Database"]
```

---

## 3. Sequence Diagram

### Example 3.1: User Request Flow

```mermaid
sequenceDiagram
    participant User as User
    participant Frontend as Frontend
    participant Backend as Backend
    participant DB as Database

    User->>Frontend: Initiate request
    Frontend->>Backend: API call
    Backend->>DB: Query data
    DB-->>Backend: Return result
    Backend-->>Frontend: Response data
    Frontend-->>User: Display result
```

### Example 3.2: Authentication Flow

```mermaid
sequenceDiagram
    participant Client as Client App
    participant Auth as Auth Server
    participant API as API Server
    participant DB as User Database

    Client->>Auth: Login request
    Auth->>DB: Verify credentials
    DB-->>Auth: User data
    Auth-->>Client: JWT token
    Client->>API: Request with token
    API-->>Client: Protected resource
```

---

## 4. Architecture with Subgraphs

### Example 4.1: Three-Tier Architecture

```mermaid
graph TB
    subgraph "Presentation Layer"
        A["Web UI"]
        B["Mobile App"]
    end

    subgraph "Business Layer"
        C["Service A"]
        D["Service B"]
    end

    subgraph "Data Layer"
        E[("Database")]
        F[("Cache")]
    end

    A --> C
    B --> C
    A --> D
    B --> D
    C --> E
    C --> F
    D --> E
```

### Example 4.2: Microservices Architecture

```mermaid
graph TB
    subgraph "Gateway Layer"
        A["API Gateway"]
    end

    subgraph "Service Layer"
        B["User Service"]
        C["Order Service"]
        D["Payment Service"]
    end

    subgraph "Infrastructure"
        E[("User DB")]
        F[("Order DB")]
        G[("Payment DB")]
    end

    A --> B
    A --> C
    A --> D
    B --> E
    C --> F
    D --> G
    B --> F
```

---

## 5. Data Flow Diagram

### Example 5.1: Request Processing Flow

```mermaid
flowchart LR
    A["User Request"] --> B["Gateway/Router"]
    B --> C["Business Logic Processing"]
    C --> D{"Data Processing"}
    D -->|"Query"| E["Query Database"]
    D -->|"External"| F["Call External Services"]
    E --> G["Assemble Response"]
    F --> G
    G --> H["Return to User"]
```

### Example 5.2: ETL Pipeline Flow

```mermaid
flowchart TD
    A["Data Source"] --> B["Extract"]
    B --> C["Validate"]
    C --> D{"Is Valid?"}
    D -->|"Yes"| E["Transform"]
    D -->|"No"| F["Log Error"]
    E --> G["Load"]
    G --> H["Data Warehouse"]
```

---

## 6. Flowchart with Decision

### Example 6.1: Implementation Process

```mermaid
flowchart TD
    A["Start"] --> B["Step 1"]
    B --> C{"Condition Check"}
    C -->|"Condition Met"| D["Step 2A"]
    C -->|"Condition Not Met"| E["Step 2B"]
    D --> F["Step 3"]
    E --> F
    F --> G["End"]
```

### Example 6.2: Error Handling Flow

```mermaid
flowchart TD
    A["Receive Request"] --> B["Validate Input"]
    B --> C{"Valid?"}
    C -->|"Yes"| D["Process Request"]
    C -->|"No"| E["Return Error"]
    D --> F{"Success?"}
    F -->|"Yes"| G["Return Result"]
    F -->|"No"| H["Log Exception"]
    H --> I["Return Error"]
```

---

## 7. Component Architecture

### Example 7.1: System Components

```mermaid
graph TB
    subgraph "Interface Layer"
        A["API/Interface"]
    end

    subgraph "Component Layer"
        B["Component 1"]
        C["Component 2"]
        D["Component 3"]
    end

    subgraph "Service Layer"
        E["Storage"]
        F["Network"]
        G["Configuration"]
    end

    A --> B
    A --> C
    B --> E
    B --> F
    C --> E
    C --> G
    D --> F
    D --> G
```

### Example 7.2: Plugin Architecture

```mermaid
graph TB
    subgraph "Core System"
        A["Plugin Manager"]
        B["Core Services"]
    end

    subgraph "Plugins"
        C["Plugin A"]
        D["Plugin B"]
        E["Plugin C"]
    end

    A --> C
    A --> D
    A --> E
    C --> B
    D --> B
    E --> B
```

---

## 8. Communication Protocol

### Example 8.1: Client-Server Protocol

```mermaid
sequenceDiagram
    participant Client as Client
    participant Server as Server

    Client->>Server: Request message
    Note over Client,Server: Protocol format description
    Server-->>Client: Response message
```

### Example 8.2: Event-Driven Communication

```mermaid
sequenceDiagram
    participant Emitter as Event Emitter
    participant Broker as Message Broker
    participant Consumer1 as Consumer A
    participant Consumer2 as Consumer B

    Emitter->>Broker: Publish event
    Broker->>Consumer1: Dispatch event
    Broker->>Consumer2: Dispatch event
    Consumer1-->>Broker: Acknowledge
    Consumer2-->>Broker: Acknowledge
```

---

## 9. Workflow Tracing

### Example 9.1: End-to-End User Flow

```mermaid
flowchart LR
    A["User Action"] --> B["Frontend Processing"]
    B --> C["API Call"]
    C --> D["Business Logic"]
    D --> E["Data Operation"]
    E --> F["Result Return"]
    F --> G["User Response"]

    style A fill:#e1f5ff
    style G fill:#e1f5ff
    style D fill:#fff4e1
```

### Example 9.2: Order Processing Flow

```mermaid
flowchart LR
    A["Place Order"] --> B["Validate Inventory"]
    B --> C{"In Stock?"}
    C -->|"Yes"| D["Reserve Items"]
    C -->|"No"| E["Notify Customer"]
    D --> F["Process Payment"]
    F --> G{"Paid?"}
    G -->|"Yes"| H["Confirm Order"]
    G -->|"No"| I["Cancel Reservation"]
```

---

## 10. Performance Optimization

### Example 10.1: Optimization Strategies

```mermaid
graph LR
    A["Performance Optimization"] --> B["Caching"]
    A --> C["Connection Pool"]
    A --> D["Async Processing"]
    A --> E["Data Sharding"]

    B --> F["Improve Speed"]
    C --> F
    D --> G["Increase Throughput"]
    E --> G
```

### Example 10.2: Caching Strategy

```mermaid
graph TD
    A["Client Request"] --> B{"Cache Hit?"}
    B -->|"Hit"| C["Return Cached"]
    B -->|"Miss"| D["Query Database"]
    D --> E["Update Cache"]
    E --> F["Return Data"]
    C --> G["Response"]
    F --> G
```

---

## 11. Testing Architecture

### Example 11.1: Test Pyramid

```mermaid
graph TB
    subgraph "Test Levels"
        A["Unit Tests"]
        B["Integration Tests"]
        C["System Tests"]
    end

    subgraph "Test Support"
        D["Mock Tools"]
        E["Test Data"]
        F["Test Environment"]
    end

    A --> D
    B --> D
    B --> E
    C --> F
```

### Example 11.2: CI/CD Pipeline

```mermaid
graph LR
    A["Code Push"] --> B["Build"]
    B --> C["Unit Tests"]
    C --> D{"Passed?"}
    D -->|"Yes"| E["Integration Tests"]
    D -->|"No"| F["Notify Developer"]
    E --> G{"Passed?"}
    G -->|"Yes"| H["Deploy"]
    G -->|"No"| F
```

---

## 12. Deployment Architecture

### Example 12.1: Production Environment

```mermaid
graph TB
    subgraph "Production"
        A["Load Balancer"]
        B["App Instance 1"]
        C["App Instance 2"]
        D[("Database")]
    end

    A --> B
    A --> C
    B --> D
    C --> D
```

### Example 12.2: Multi-Environment Deployment

```mermaid
graph LR
    A["Developer"] --> B["Dev Environment"]
    B --> C["Staging Environment"]
    C --> D["Production Environment"]

    D --> E["CDN"]
    D --> F["Database Cluster"]
```

---

## 13. State Diagram

### Example 13.1: Application States

```mermaid
stateDiagram-v2
    [*] --> Initialization
    Initialization --> Running
    Running --> Paused: User pause
    Running --> Error: Exception
    Paused --> Running: User resume
    Error --> Running: Retry successful
    Error --> [*]: Give up
    Running --> [*]: Completed
```

### Example 13.2: Order States

```mermaid
stateDiagram-v2
    [*] --> Created
    Created --> Paid: Payment received
    Created --> Cancelled: User cancelled
    Paid --> Processing: Start processing
    Processing --> Shipped: Ship order
    Processing --> Refunded: Refund requested
    Shipped --> Delivered: Delivery confirmed
    Delivered --> [*]
    Refunded --> [*]
    Cancelled --> [*]
```

---

## 14. ER Diagram

### Example 14.1: E-Commerce Schema

```mermaid
erDiagram
    USER ||--o{ ORDER : places
    ORDER ||--|{ LINE_ITEM : contains
    PRODUCT ||--o{ LINE_ITEM : "is in"

    USER {
        uuid id PK
        string name
        string email
    }

    ORDER {
        uuid id PK
        uuid user_id FK
        datetime created_at
    }

    PRODUCT {
        uuid id PK
        string name
        decimal price
    }

    LINE_ITEM {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        int quantity
    }
```

### Example 14.2: Blog Schema

```mermaid
erDiagram
    AUTHOR ||--o{ POST : writes
    POST ||--|{ COMMENT : has
    POST }o--|| CATEGORY : belongs_to

    AUTHOR {
        int id PK
        string name
        string email
    }

    POST {
        int id PK
        string title
        text content
        int author_id FK
        int category_id FK
    }

    COMMENT {
        int id PK
        text body
        int post_id FK
    }

    CATEGORY {
        int id PK
        string name
    }
```

---

## 15. Git Branching (Use Flowchart, Not gitGraph)

> **Note**: Avoid `gitGraph` — it is fragile. Use flowchart instead.

### Example 15.1: Feature Branch Workflow

```mermaid
graph LR
    A["main"] --> B["develop"]
    B --> C["feature-A"]
    B --> D["feature-B"]
    C --> E["merge to develop"]
    D --> E
    E --> F["merge to main"]
```

### Example 15.2: Git Flow Model

```mermaid
graph LR
    A["main"] --> B["develop"]
    B --> C["feature branch"]
    B --> D["release branch"]
    D --> E["hotfix branch"]
    C --> B
    D --> A
    E --> A
```

---

## Syntax Rules Reference

All diagrams follow these rules:

1. ✅ All node labels use double quotes: `["Label"]`
2. ✅ All edge labels use double quotes: `-->|"label"|`
3. ✅ No spaces in node IDs: `MyNode` not `My Node`
4. ✅ No reserved keywords as IDs: `LoopNode` not `loop`
5. ✅ Matched brackets: `["Label"]` not `{Label]`
6. ✅ Comments use `%%` not `#`
7. ✅ sequenceDiagram uses declared IDs, not aliases
8. ✅ No `style` in sequenceDiagram or stateDiagram
9. ✅ Long chains (8+ nodes) use `TD` not `LR`
10. ✅ Subgraph labels quoted if containing spaces
