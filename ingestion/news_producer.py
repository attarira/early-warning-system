import json
import time
from kafka import KafkaProducer

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'
NEWS_TOPIC = 'news'

# Example news data
news_samples = [
    {
        "headline": "Bank XYZ faces liquidity crunch amid market turmoil",
        "source": "Reuters",
        "timestamp": "2024-07-29T10:00:00Z"
    },
    {
        "headline": "Central bank intervenes to stabilize currency",
        "source": "Bloomberg",
        "timestamp": "2024-07-29T10:01:00Z"
    },
    {
        "headline": "Major hedge fund reports significant losses",
        "source": "Financial Times",
        "timestamp": "2024-07-29T10:02:00Z"
    }
]

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    for news in news_samples:
        producer.send(NEWS_TOPIC, news)
        print(f"Sent news: {news['headline']}")
        time.sleep(1)
    producer.flush()
    print("All news messages sent.")

if __name__ == "__main__":
    main() 