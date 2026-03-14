import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/metrics"

st.title("Inbound Carrier Sales Dashboard")

try:
    response = requests.get(API_URL)
    metrics = response.json()

    st.metric("Total Calls", metrics["total_calls"])
    st.metric("Booked Calls", metrics["booked_calls"])
    st.metric("Failed Negotiations", metrics["failed_negotiations"])
    st.metric("Ineligible Carriers", metrics["ineligible_carriers"])
    st.metric("Average Final Rate", metrics["avg_final_rate"])

    st.write("### Sentiment Breakdown")
    st.write(metrics["sentiment_breakdown"])

except Exception as e:
    st.error("Could not connect to API")
    st.write(e)