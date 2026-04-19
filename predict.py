import time

import pandas as pd
import streamlit as st
from PIL import Image

from app_utils import (
    CLASS_COLORS,
    fake_prediction,
    generate_heatmap,
    image_to_seed,
    infer_modality,
    prepare_preview,
    save_prediction,
)


def render() -> None:
    st.markdown(
        """
        <div class="app-hero">
            <h1>Prediction Workspace</h1>
            <p>Upload a CT scan or chest X-ray, run analysis, and review the simulated CM-ADAL output.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([0.95, 1.35], gap="large")
    with left:
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload image", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
        run_analysis = st.button("Run Analysis", use_container_width=True)

        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Uploaded Scan", use_container_width=True)
        else:
            image = None
            st.info("Upload a CT or chest X-ray image to begin analysis.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="app-card">', unsafe_allow_html=True)
        if uploaded_file is None:
            st.markdown('<div class="soft-text">Awaiting uploaded scan for analysis.</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            return

        if run_analysis:
            steps = [
                "Extracting features via ResNet18 backbone...",
                "Applying CBAM attention module...",
                "Running adversarial domain alignment...",
                "Generating prediction...",
            ]
            step_box = st.empty()
            for step in steps:
                with step_box.container():
                    with st.spinner(step):
                        time.sleep(0.6)

            modality = infer_modality(uploaded_file)
            seed = image_to_seed(uploaded_file.getvalue(), modality)
            result = fake_prediction(seed, modality)
            heatmap = generate_heatmap(image, result["predicted_disease"])
            save_prediction(uploaded_file, modality, result, image, heatmap)

        current = st.session_state.current_result
        if current is None:
            st.markdown('<div class="soft-text">Click "Run Analysis" to generate a prediction.</div>', unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            return

        show_prediction_result(current)
        st.markdown("</div>", unsafe_allow_html=True)


def show_prediction_result(current) -> None:
    left_col, right_col = st.columns([1.05, 0.95], gap="large")
    with left_col:
        img1, img2 = st.columns(2)
        with img1:
            st.markdown('<div class="section-title">Original Scan</div>', unsafe_allow_html=True)
            st.image(prepare_preview(current["image"]), use_container_width=True)
        with img2:
            st.markdown('<div class="section-title">Attention Map — Regions influencing prediction</div>', unsafe_allow_html=True)
            st.image(current["heatmap"], use_container_width=True)

    with right_col:
        label = current["predicted_disease"]
        color = CLASS_COLORS[label]
        st.markdown(
            f"""
            <div class="status-banner">
                Analysis complete. Simulated prediction pipeline finished successfully.
            </div>
            <div class="result-badge" style="background:{color};">{label}</div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="section-title">Clinical Note</div>
                <div class="soft-text">{current["clinical_note"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="glass-card">
                <div class="section-title">Modality Detected</div>
                <div class="soft-text">{current["modality"]}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="section-title">Likelihood Scores</div>', unsafe_allow_html=True)
        probs = pd.DataFrame(
            {"Disease": list(current["probabilities"].keys()), "Probability": list(current["probabilities"].values())}
        ).sort_values("Probability", ascending=False)
        for _, row in probs.iterrows():
            st.progress(float(row["Probability"]) / 100.0, text=f"{row['Disease']}: {row['Probability']:.2f}%")
