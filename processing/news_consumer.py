from kafka import KafkaConsumer
import json
from transformers import pipeline
import re

KAFKA_BROKER = 'localhost:9092'
NEWS_TOPIC = 'news'

# Define simple risk type keywords
RISK_KEYWORDS = {
    'Liquidity Risk': [r'liquidity', r'withdrawal', r'insolvency', r'cash crunch'],
    'Credit Risk': [r'default', r'non-performing', r'bad loan', r'credit'],
    'Market Risk': [r'market turmoil', r'volatility', r'price collapse', r'selloff'],
    'Operational Risk': [r'fraud', r'cyber', r'outage', r'error']
}

def detect_risk_type(text):
    detected = []
    for risk, patterns in RISK_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                detected.append(risk)
                break
    return detected if detected else ['Uncategorized']

def main():
    # Load sentiment analysis pipeline (FinBERT or fallback to distilbert)
    try:
        sentiment_analyzer = pipeline('sentiment-analysis', model='yiyanghkust/finbert-tone')
    except Exception:
        print("FinBERT not available, using default sentiment model.")
        sentiment_analyzer = pipeline('sentiment-analysis')

    consumer = KafkaConsumer(
        NEWS_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='ews-news-consumer',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print(f"Listening for messages on topic '{NEWS_TOPIC}'...")
    for message in consumer:
        news = message.value
        text = news['headline']
        sentiment = sentiment_analyzer(text)[0]
        risk_types = detect_risk_type(text)
        print(f"Received news: {text}\n  Source: {news['source']} | Time: {news['timestamp']}\n  Sentiment: {sentiment['label']} (score: {sentiment['score']:.2f})\n  Risk Type(s): {', '.join(risk_types)}\n")

if __name__ == "__main__":
    main() 