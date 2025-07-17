#!/bin/bash
set -e

# Start Kafka and Zookeeper
if ! docker info > /dev/null 2>&1; then
  echo "Docker is not running. Please start Docker Desktop and rerun this script."
  exit 1
fi

echo "Starting Kafka and Zookeeper via Docker Compose..."
docker compose -f docker/docker-compose.yml up -d
sleep 10

echo "Activating virtual environment..."
source venv/bin/activate || source .venv/bin/activate

# Run the news producer
echo "Running news producer to send sample news to Kafka..."
python -m ingestion.news_producer

# Run the news consumer in the background
echo "Starting news consumer (risk scoring, alerting, storage)..."
PYTHONPATH=. nohup python -m processing.news_consumer > consumer.log 2>&1 &
CONSUMER_PID=$!
echo "News consumer running in background (PID $CONSUMER_PID, logs in consumer.log)"

# Launch Streamlit dashboard
echo "Launching Streamlit dashboard..."
PYTHONPATH=. streamlit run dashboard/app.py

# When done, kill the consumer
kill $CONSUMER_PID 