import streamlit as st
from storage.db import get_recent_alerts, init_db

st.set_page_config(page_title="EWS Alerts Dashboard", layout="wide")
st.title("🚨 Early Warning System - Recent Alerts")

init_db()

REFRESH_INTERVAL = 10  # seconds

@st.cache_data(ttl=REFRESH_INTERVAL)
def fetch_alerts():
    return get_recent_alerts(limit=20)

if st.button("Refresh Alerts"):
    st.cache_data.clear()

alerts = fetch_alerts()

if not alerts:
    st.info("No recent alerts found.")
else:
    data = [{
        "Time": str(a.processed_at),
        "Entity": a.entity,
        "Headline": a.headline,
        "Sentiment": a.sentiment,
        "Score": f"{a.sentiment_score:.2f}",
        "Risk Types": a.risk_types,
        "Alert Message": a.alert_message
    } for a in alerts]
    st.dataframe(data, use_container_width=True)
    st.caption(f"Auto-refreshes every {REFRESH_INTERVAL} seconds. Click 'Refresh Alerts' to update immediately.") 