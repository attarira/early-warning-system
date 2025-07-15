# Early Warning System (EWS) for Financial Risks

## Overview

The Early Warning System (EWS) is a prototype that detects potential systemic financial risks in real-time by monitoring news articles, social media chatter (e.g., Twitter), and market indicators. The system uses Large Language Models (LLMs) to analyze unstructured text data, detect risk signals (e.g., liquidity crunch, defaults, market panic), and provides alerts to risk managers.

## Architecture

- **Data Ingestion:** Collects real-time data from news APIs, Twitter, and simulated market indicators.
- **Stream Processing:** Processes data streams using Kafka and PySpark/Faust.
- **Risk Signal Detection:** Uses LLMs (e.g., FinBERT) for classification, sentiment analysis, and entity recognition.
- **Alerting Engine:** Triggers alerts based on risk thresholds and generates explainable summaries.
- **Visualization:** CLI logs and Streamlit dashboard for real-time monitoring.
- **Storage:** Stores raw and processed data in SQLite/PostgreSQL.

## MVP Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Start Kafka and Zookeeper (see docker/docker-compose.yml).
3. Run data producers in `ingestion/` to simulate or collect data.
4. Start the stream processor in `processing/`.
5. Run the dashboard in `dashboard/` for real-time alerts.

## Directories

- `ingestion/` - Data producers for news, Twitter, and market data
- `processing/` - Stream processing and risk signal detection
- `alerting/` - Alert logic and explainability
- `dashboard/` - Streamlit dashboard
- `models/` - ML/LLM models and utilities
- `storage/` - Database setup and utilities
- `docker/` - Docker and orchestration files

---

For more details, see the product specification.
