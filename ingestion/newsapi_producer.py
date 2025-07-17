import os
import time
import json
import requests
from kafka import KafkaProducer
from dotenv import load_dotenv
load_dotenv()

KAFKA_BROKER = 'localhost:9092'
NEWS_TOPIC = 'news'
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY')  # Store your key in an .env file or export as env var

def fetch_news(query="bank OR finance OR liquidity", language="en", page_size=5):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": query,
        "language": language,
        "pageSize": page_size,
        "apiKey": NEWSAPI_KEY
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json().get("articles", [])

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    articles = fetch_news()
    print("Fetched articles:", len(articles))
    for article in articles:
        news = {
            "headline": article["title"],
            "source": article["source"]["name"],
            "timestamp": article["publishedAt"]
        }
        producer.send(NEWS_TOPIC, news)
        print(f"Sent news: {news['headline']}")
        time.sleep(1)
    producer.flush()
    print("All news messages sent.")

if __name__ == "__main__":
    main()