#!/bin/bash
set -e
set -m # Enable Job Control

# Function to clean up background processes
cleanup() {
    echo "Cleaning up background processes..."
    if [ -n "$NEWS_PRODUCER_PID" ]; then kill "$NEWS_PRODUCER_PID"; fi
    if [ -n "$REDDIT_PRODUCER_PID" ]; then kill "$REDDIT_PRODUCER_PID"; fi
    if [ -n "$CONSUMER_PID" ]; then kill "$CONSUMER_PID"; fi
}

# Trap EXIT signal to run cleanup function
trap cleanup EXIT

# Start Kafka and Zookeeper
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker Desktop and rerun this script."
  exit 1
fi

echo "Starting Kafka and Zookeeper via Docker Compose..."
docker compose -f docker/docker-compose.yml up -d
sleep 10

echo "Activating virtual environment..."
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
    PYTHON_BIN="$(pwd)/.venv/bin/python"
else
    echo "No virtual environment found!"
    exit 1
fi

# Run producers in the background
echo "Running newsapi producer in the background..."
PYTHONPATH=. nohup "$PYTHON_BIN" -m ingestion.newsapi_producer > news_producer.log 2>&1 &
NEWS_PRODUCER_PID=$!
echo "News producer running in background (PID $NEWS_PRODUCER_PID, logs in news_producer.log)"

echo "Running reddit producer in the background..."
PYTHONPATH=. nohup "$PYTHON_BIN" -m ingestion.reddit_producer > reddit_producer.log 2>&1 &
REDDIT_PRODUCER_PID=$!
echo "Reddit producer running in background (PID $REDDIT_PRODUCER_PID, logs in reddit_producer.log)"

# Run the news consumer in the background
echo "Starting news consumer (risk scoring, alerting, storage)..."
PYTHONPATH=. nohup "$PYTHON_BIN" -m processing.news_consumer > consumer.log 2>&1 &
CONSUMER_PID=$!
echo "News consumer running in background (PID $CONSUMER_PID, logs in consumer.log)"

# Launch Streamlit dashboard
echo "Launching Streamlit dashboard..."
PYTHONPATH=. streamlit run dashboard/app.py

# When done, the trap will kill the background processes 