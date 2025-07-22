from kafka import KafkaConsumer
import json
from models.risk_scoring import get_sentiment, detect_risk_type, extract_entities
from alerting.alert_engine import AlertEngine
from storage.db import init_db, insert_news_event
import datetime
import spacy

_nlp = None
def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

def extract_entities(text):
    nlp = get_nlp()
    doc = nlp(text)
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    return orgs if orgs else ["Unknown"]

KAFKA_BROKER = 'localhost:9092'
NEWS_TOPIC = 'news'

def main():
    init_db()
    consumer = KafkaConsumer(
        NEWS_TOPIC,
        'reddit_posts',
        bootstrap_servers=KAFKA_BROKER,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='ews-news-consumer',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    print(f"Listening for messages on topics: '{NEWS_TOPIC}', 'reddit_posts'...")

    alert_engine = AlertEngine()

    for message in consumer:
        data = message.value
        if message.topic == NEWS_TOPIC:
            text = data['headline']
            source = data.get('source', 'Unknown')
            timestamp = data.get('timestamp', str(datetime.datetime.utcnow()))
        elif message.topic == 'reddit_posts':
            text = data['title']
            source = 'Reddit'
            timestamp = str(datetime.datetime.fromtimestamp(data.get('created_utc', time.time())))
        else:
            continue

        entities = extract_entities(text)
        sentiment = get_sentiment(text)
        risk_types = detect_risk_type(text)

        for entity in entities:
            alerts = alert_engine.process(entity, sentiment['label'])
            # New logic: trigger alert for any negative sentiment
            if sentiment['label'].lower() == 'negative':
                alert_flag = True
                alert_message = f"[ALERT] Negative sentiment detected for {entity}: {text}"
            else:
                alert_flag = bool(alerts)
                alert_message = '\n'.join(alerts) if alerts else None

            # Store in DB
            insert_news_event(
                headline=text,
                source=source,
                timestamp=timestamp,
                entity=entity,
                sentiment=sentiment['label'],
                sentiment_score=sentiment['score'],
                risk_types=risk_types,
                alert=alert_flag,
                alert_message=alert_message
            )

            if alert_flag and alert_message:
                print(alert_message)
            for alert in alerts:
                print(alert)

            print(f"Received news: {text}\n  Source: {source} | Time: {timestamp}\n  Sentiment: {sentiment['label']} (score: {sentiment['score']:.2f})\n  Risk Type(s): {', '.join(risk_types)}\n  Entity: {entity}\n")

if __name__ == "__main__":
    main() 