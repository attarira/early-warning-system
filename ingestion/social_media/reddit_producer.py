import os
import time
import json
import praw
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()

# Kafka configuration
KAFKA_BROKER = 'localhost:9092'
REDDIT_TOPIC = 'reddit_posts'

# Reddit API configuration
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

def get_reddit_instance():
    """Initializes and returns a Reddit instance."""
    return praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT
    )

def fetch_posts(reddit, subreddit_name='wallstreetbets', limit=10):
    """Fetches posts from a given subreddit."""
    subreddit = reddit.subreddit(subreddit_name)
    # Fetching new posts
    return subreddit.new(limit=limit)

def main():
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    reddit = get_reddit_instance()
    posts = fetch_posts(reddit)
    
    print(f"Fetched posts from r/wallstreetbets")
    
    for post in posts:
        post_data = {
            "id": post.id,
            "title": post.title,
            "score": post.score,
            "url": post.url,
            "created_utc": post.created_utc
        }
        producer.send(REDDIT_TOPIC, post_data)
        print(f"Sent post: {post.title}")
        time.sleep(1)
        
    producer.flush()
    print("All Reddit posts sent.")

if __name__ == "__main__":
    main() 