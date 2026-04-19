import streamlit as st

from app_utils import CLASS_COLORS, confidence_trend_chart, disease_color, history_frame, history_pie_chart


def render() -> None:
    st.markdown(
        """
        <div class="app-hero">
            <h1>Prediction History</h1>
            <p>Review stored scans, prediction confidence, and disease distribution across the current session.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    frame = history_frame()
    if frame.empty:
        st.info("No prediction history available.")
        return

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    rows = []
    for _, row in frame.iterrows():
        disease = row["Predicted Disease"]
        rows.append(
            f'<tr><td>{row["Scan ID"]}</td><td>{row["Modality"]}</td>'
            f'<td><span class="history-disease" style="background:{disease_color(disease)};">{disease}</span></td>'
            f'<td>{row["Confidence Score"]:.1f}%</td><td>{row["Timestamp"]}</td></tr>'
        )
    html_table = f"""<table class="history-table" style="width: 100%;">
<thead><tr>
<th style="text-align: left;">Scan ID</th>
<th style="text-align: left;">Modality</th>
<th style="text-align: left;">Predicted Disease</th>
<th style="text-align: left;">Confidence Score</th>
<th style="text-align: left;">Timestamp</th>
</tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>"""
    st.markdown(html_table, unsafe_allow_html=True)
    if st.button("Clear History"):
        st.session_state.history = []
        st.session_state.current_result = None
        st.session_state.last_scan_hash = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    left, right = st.columns(2, gap="large")
    with left:
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Disease Distribution</div>', unsafe_allow_html=True)
        st.plotly_chart(history_pie_chart(), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Confidence Trend</div>', unsafe_allow_html=True)
        st.plotly_chart(confidence_trend_chart(), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
