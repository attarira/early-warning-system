import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

data_dir = 'data'
os.makedirs(data_dir, exist_ok=True)
DB_PATH = os.path.join(data_dir, 'ews.db')
Base = declarative_base()

class NewsEvent(Base):
    __tablename__ = 'news_events'
    id = Column(Integer, primary_key=True)
    headline = Column(Text)
    source = Column(String(128))
    timestamp = Column(String(64))
    entity = Column(String(128))
    sentiment = Column(String(32))
    sentiment_score = Column(Float)
    risk_types = Column(Text)
    alert = Column(Boolean, default=False)
    alert_message = Column(Text, nullable=True)
    processed_at = Column(DateTime, default=datetime.datetime.utcnow)

def get_engine():
    return create_engine(f'sqlite:///{DB_PATH}')

Session = sessionmaker(bind=get_engine())

def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)

def insert_news_event(headline, source, timestamp, entity, sentiment, sentiment_score, risk_types, alert, alert_message=None):
    session = Session()
    event = NewsEvent(
        headline=headline,
        source=source,
        timestamp=timestamp,
        entity=entity,
        sentiment=sentiment,
        sentiment_score=sentiment_score,
        risk_types=','.join(risk_types),
        alert=alert,
        alert_message=alert_message
    )
    session.add(event)
    session.commit()
    session.close()

def get_recent_alerts(limit=10):
    session = Session()
    alerts = session.query(NewsEvent).filter(NewsEvent.alert == True).order_by(NewsEvent.processed_at.desc()).limit(limit).all()
    session.close()
    return alerts

def print_recent_alerts(limit=10):
    alerts = get_recent_alerts(limit)
    if not alerts:
        print("No recent alerts found.")
        return
    print(f"\nRecent Alerts (limit {limit}):\n" + "-"*40)
    for event in alerts:
        print(f"[{event.processed_at}] {event.entity}: {event.headline}\n  Source: {event.source} | Time: {event.timestamp}\n  Sentiment: {event.sentiment} (score: {event.sentiment_score:.2f})\n  Risk Type(s): {event.risk_types}\n  Alert Message: {event.alert_message}\n") 