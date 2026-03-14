import streamlit as st
import requests
import pandas as pd
from datetime import datetime

API_URL = "http://127.0.0.1:8000/metrics"

st.set_page_config(
    page_title="Inbound Carrier Sales Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .main-title {
            font-size: 2.2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }
        .subtitle {
            color: #6b7280;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }
        .section-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-top: 1rem;
            margin-bottom: 0.75rem;
        }
        .footer-note {
            color: #6b7280;
            font-size: 0.85rem;
            margin-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

header_left, header_right = st.columns([4, 1])

with header_left:
    st.markdown('<div class="main-title">Inbound Carrier Sales Dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">Operational overview for carrier negotiations, outcomes, and sentiment</div>',
        unsafe_allow_html=True
    )

with header_right:
    refresh = st.button("Refresh")

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

    booking_rate = round((booked_calls / total_calls) * 100, 1) if total_calls else 0
    failure_rate = round((failed_negotiations / total_calls) * 100, 1) if total_calls else 0
    ineligible_rate = round((ineligible_carriers / total_calls) * 100, 1) if total_calls else 0

    st.markdown('<div class="section-title">Key Metrics</div>', unsafe_allow_html=True)

    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Total Calls", total_calls)
    kpi2.metric("Booked Calls", booked_calls, f"{booking_rate}% of calls")
    kpi3.metric("Failed Negotiations", failed_negotiations, f"{failure_rate}% of calls")
    kpi4.metric("Ineligible Carriers", ineligible_carriers, f"{ineligible_rate}% of calls")
    kpi5.metric("Avg Final Rate", f"${avg_final_rate:,.2f}")

    st.divider()

    outcomes_df = pd.DataFrame(
        [
            {"outcome": "Booked", "count": booked_calls},
            {"outcome": "Failed Negotiations", "count": failed_negotiations},
            {"outcome": "Ineligible Carriers", "count": ineligible_carriers},
        ]
    )

    sentiment_df = pd.DataFrame(
        [
            {"sentiment": sentiment, "count": count}
            for sentiment, count in sentiment_breakdown.items()
        ]
    ) if sentiment_breakdown else pd.DataFrame(columns=["sentiment", "count"])

    left_col, right_col = st.columns([1.15, 1])

    with left_col:
        st.markdown('<div class="section-title">Call Outcomes</div>', unsafe_allow_html=True)
        st.bar_chart(outcomes_df.set_index("outcome"))

        with st.expander("View outcomes table"):
            st.dataframe(outcomes_df, use_container_width=True, hide_index=True)

    with right_col:
        st.markdown('<div class="section-title">Sentiment Breakdown</div>', unsafe_allow_html=True)

        if not sentiment_df.empty:
            st.bar_chart(sentiment_df.set_index("sentiment"))

            with st.expander("View sentiment table"):
                st.dataframe(sentiment_df, use_container_width=True, hide_index=True)
        else:
            st.info("No sentiment data available yet.")

    st.divider()

    lower_left, lower_right = st.columns([1, 1])

    with lower_left:
        st.markdown('<div class="section-title">Performance Snapshot</div>', unsafe_allow_html=True)

        snapshot_df = pd.DataFrame(
            [
                {"metric": "Booking Rate", "value": f"{booking_rate}%"},
                {"metric": "Negotiation Failure Rate", "value": f"{failure_rate}%"},
                {"metric": "Ineligible Carrier Rate", "value": f"{ineligible_rate}%"},
            ]
        )
        st.dataframe(snapshot_df, use_container_width=True, hide_index=True)

    with lower_right:
        st.markdown('<div class="section-title">System Status</div>', unsafe_allow_html=True)
        st.success("API connection successful")
        st.markdown(
            f'<div class="footer-note">Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>',
            unsafe_allow_html=True
        )

    with st.expander("View raw metrics response"):
        st.json(metrics)

except requests.exceptions.RequestException as e:
    st.error(f"Could not connect to the FastAPI backend: {e}")
    st.info("Make sure the API is running on http://127.0.0.1:8000")