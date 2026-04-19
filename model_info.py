import streamlit as st

def render() -> None:
    st.markdown(
        """
        <div class="app-hero">
            <h1>Model Information</h1>
            <p>Overview of the CM-ADAL framework and its cross-modality analysis pipeline.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="app-card">
            <div class="section-title">About the Model</div>
            <div class="soft-text">
                CM-ADAL is a cross-modality lung disease classification framework designed to align CT and chest
                X-ray feature spaces while preserving disease-sensitive attention. The prototype simulates a
                production medical AI interface for diagnosis support and model explainability.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Architecture</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="pipeline-box">ResNet18</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="pipeline-box">CBAM</div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="pipeline-box">GRL</div>', unsafe_allow_html=True)
    with c4:
        st.markdown('<div class="pipeline-box">Disease Classifier</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">How It Works</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="soft-text">
            CM-ADAL begins by extracting visual representations from CT scans and chest X-rays with a ResNet18
            backbone. CBAM then focuses attention on the most informative lung regions. A gradient reversal layer
            encourages shared modality-invariant features so that CT and chest X-ray inputs can be aligned into a
            common representation space. Finally, the disease classifier predicts one of four categories:
            COVID-19, Pneumonia, Tuberculosis, or Normal.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
