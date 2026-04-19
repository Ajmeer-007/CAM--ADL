from datetime import datetime

import streamlit as st

from app_utils import (
    dashboard_metrics_from_history,
    disease_distribution_chart,
    render_metric,
    scans_per_day_chart,
)


def render() -> None:
    current_dt = datetime.now().strftime("%A, %d %B %Y · %I:%M %p")
    st.markdown(
        f"""
        <div class="app-hero">
            <h1>Dashboard</h1>
            <p>Welcome back. Current system time: {current_dt}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    total, ct, cxr, avg_conf = dashboard_metrics_from_history()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric("Total Scans Analyzed", str(total), "All stored session predictions")
    with c2:
        render_metric("CT Scans", str(ct), "Cross-modality CT studies")
    with c3:
        render_metric("X-Ray Scans", str(cxr), "Chest radiography studies")
    with c4:
        render_metric("Average Confidence Score", f"{avg_conf:.1f}%", "Across historical predictions")

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Disease Distribution</div>', unsafe_allow_html=True)
        st.plotly_chart(disease_distribution_chart(), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Scans Analyzed Over Last 7 Days</div>', unsafe_allow_html=True)
        st.plotly_chart(scans_per_day_chart(), use_container_width=True)
        if st.button("New Analysis", use_container_width=True):
            st.session_state.page = "Predict"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
