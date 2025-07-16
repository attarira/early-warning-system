from kafka import KafkaConsumer
import json
from models.risk_scoring import get_sentiment, detect_risk_type, extract_entity
from alerting.alert_engine import AlertEngine
from storage.db import init_db, insert_news_event
import datetime

KAFKA_BROKER = 'localhost:9092'
NEWS_TOPIC = 'news'

def main():
    init_db()
    consumer = KafkaConsumer(
        NEWS_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='ews-news-consumer',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print(f"Listening for messages on topic '{NEWS_TOPIC}'...")

    alert_engine = AlertEngine()

    for message in consumer:
        news = message.value
        text = news['headline']
        entity = extract_entity(text)
        sentiment = get_sentiment(text)
        risk_types = detect_risk_type(text)

        alerts = alert_engine.process(entity, sentiment['label'])
        alert_flag = bool(alerts)
        alert_message = '\n'.join(alerts) if alerts else None

        # Store in DB
        insert_news_event(
            headline=text,
            source=news['source'],
            timestamp=news['timestamp'],
            entity=entity,
            sentiment=sentiment['label'],
            sentiment_score=sentiment['score'],
            risk_types=risk_types,
            alert=alert_flag,
            alert_message=alert_message
        )

        for alert in alerts:
            print(alert)

        print(f"Received news: {text}\n  Source: {news['source']} | Time: {news['timestamp']}\n  Sentiment: {sentiment['label']} (score: {sentiment['score']:.2f})\n  Risk Type(s): {', '.join(risk_types)}\n  Entity: {entity}\n")

if __name__ == "__main__":
    main() 