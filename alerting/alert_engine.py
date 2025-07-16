import time
from collections import defaultdict, deque

NEGATIVE_SENTIMENT_THRESHOLD = 0.7
VOLUME_SPIKE_FACTOR = 3
WINDOW_SECONDS = 60

class AlertEngine:
    def __init__(self):
        self.entity_msgs = defaultdict(deque)  # entity: deque of (timestamp, sentiment_label)
        self.entity_baseline = defaultdict(lambda: 1)  # entity: baseline volume

    def process(self, entity, sentiment_label):
        timestamp = time.time()
        self.entity_msgs[entity].append((timestamp, sentiment_label))
        # Remove old messages outside window
        while self.entity_msgs[entity] and timestamp - self.entity_msgs[entity][0][0] > WINDOW_SECONDS:
            self.entity_msgs[entity].popleft()
        # Calculate stats
        window_msgs = list(self.entity_msgs[entity])
        total = len(window_msgs)
        negative = sum(1 for t, s in window_msgs if s.lower() == 'negative')
        neg_ratio = negative / total if total else 0
        alerts = []
        # Volume spike detection
        if total > VOLUME_SPIKE_FACTOR * self.entity_baseline[entity]:
            alerts.append(f"[ALERT] Volume spike for {entity}: {total} messages in last {WINDOW_SECONDS}s (baseline: {self.entity_baseline[entity]})")
            self.entity_baseline[entity] = total
        # Negative sentiment detection
        if neg_ratio > NEGATIVE_SENTIMENT_THRESHOLD:
            alerts.append(f"[ALERT] Negative sentiment for {entity}: {neg_ratio*100:.1f}% negative in last {WINDOW_SECONDS}s")
        return alerts 