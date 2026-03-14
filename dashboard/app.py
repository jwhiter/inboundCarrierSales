import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/metrics"

st.set_page_config(
    page_title="Inbound Carrier Sales Dashboard",
    layout="wide"
)

st.title("Inbound Carrier Sales Dashboard")
st.caption("Operational overview for carrier negotiations, outcomes, and sentiment")

try:
    response = requests.get(API_URL, timeout=5)
    response.raise_for_status()
    metrics = response.json()

    total_calls = metrics.get("total_calls", 0)
    booked_calls = metrics.get("booked_calls", 0)
    failed_negotiations = metrics.get("failed_negotiations", 0)
    ineligible_carriers = metrics.get("ineligible_carriers", 0)
    avg_final_rate = metrics.get("avg_final_rate", 0)
    sentiment_breakdown = metrics.get("sentiment_breakdown", {})

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Calls", total_calls)
    col2.metric("Booked Calls", booked_calls)
    col3.metric("Failed Negotiations", failed_negotiations)
    col4.metric("Ineligible Carriers", ineligible_carriers)
    col5.metric("Avg Final Rate", f"${avg_final_rate}")

    st.divider()

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.subheader("Call Outcomes")

        outcomes_df = pd.DataFrame(
            [
                {"outcome": "Booked", "count": booked_calls},
                {"outcome": "Failed Negotiations", "count": failed_negotiations},
                {"outcome": "Ineligible Carriers", "count": ineligible_carriers},
            ]
        )

        st.dataframe(outcomes_df, use_container_width=True)
        st.bar_chart(outcomes_df.set_index("outcome"))

    with right_col:
        st.subheader("Sentiment Breakdown")

        if sentiment_breakdown:
            sentiment_df = pd.DataFrame(
                [
                    {"sentiment": sentiment, "count": count}
                    for sentiment, count in sentiment_breakdown.items()
                ]
            )

            st.dataframe(sentiment_df, use_container_width=True)
            st.bar_chart(sentiment_df.set_index("sentiment"))
        else:
            st.info("No sentiment data available yet.")

    st.divider()

    st.subheader("Raw Metrics Response")
    st.json(metrics)

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the FastAPI backend: {e}")
    st.info("Make sure the API is running on http://127.0.0.1:8000")