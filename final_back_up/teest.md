flowchart TD
    subgraph Web Tier
        A[User Browser] -->|1. HTTP Request| B[Flask App]
        B -->|2. Lookup user/product| C[Redis Cache]
        C -- cache miss -->|3. Query| D[MySQL]
        D -->|4. Return data| C
        C -->|5. Return data| B
        B -->|6. Render page| A
        A -->|7. Click Event| B
        B -->|8. Publish click| E[Kafka Topic: click_events]
    end

    subgraph Ingestion & Storage
        E -->|9. Consume events| F[Kafka Consumer]
        F -->|10. Write logs| G[Cassandra: click_logs]
    end

    subgraph Analytics & Recommendation
        H[PySpark Job] -->|11. Read clicks| G
        H -->|12. Read user/product| D
        H -->|13. Compute recommendations| I[Recommendation Store]
    end

    subgraph Serving
        B -->|14. Fetch recs| I
