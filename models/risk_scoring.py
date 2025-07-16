import re
from transformers import pipeline

RISK_KEYWORDS = {
    'Liquidity Risk': [r'liquidity', r'withdrawal', r'insolvency', r'cash crunch'],
    'Credit Risk': [r'default', r'non-performing', r'bad loan', r'credit'],
    'Market Risk': [r'market turmoil', r'volatility', r'price collapse', r'selloff'],
    'Operational Risk': [r'fraud', r'cyber', r'outage', r'error']
}

_sentiment_analyzer = None

def get_sentiment_analyzer():
    global _sentiment_analyzer
    if _sentiment_analyzer is None:
        try:
            _sentiment_analyzer = pipeline('sentiment-analysis', model='yiyanghkust/finbert-tone')
        except Exception:
            print("FinBERT not available, using default sentiment model.")
            _sentiment_analyzer = pipeline('sentiment-analysis')
    return _sentiment_analyzer

def get_sentiment(text):
    analyzer = get_sentiment_analyzer()
    return analyzer(text)[0]

def detect_risk_type(text):
    detected = []
    for risk, patterns in RISK_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                detected.append(risk)
                break
    return detected if detected else ['Uncategorized']

def extract_entity(text):
    match = re.search(r'([A-Z][a-zA-Z0-9]+)', text)
    return match.group(1) if match else 'Unknown' 