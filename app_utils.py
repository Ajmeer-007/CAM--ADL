import hashlib
import io
import time
from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter, ImageOps


LABELS = ["COVID-19", "Pneumonia", "Tuberculosis", "Normal"]
CLASS_COLORS = {
    "COVID-19": "#ef4444",
    "Pneumonia": "#f97316",
    "Tuberculosis": "#facc15",
    "Normal": "#10b981",
}

CLINICAL_NOTES = {
    "COVID-19": "Ground-glass opacities detected in bilateral lung fields consistent with COVID-19 patterns.",
    "Pneumonia": "Lobar consolidation detected in lower lung regions consistent with Pneumonia.",
    "Tuberculosis": "Upper lobe infiltrates and cavitation patterns consistent with Tuberculosis.",
    "Normal": "No significant abnormalities detected. Lung fields appear clear.",
}


def set_page() -> None:
    st.set_page_config(page_title="CM-ADAL", page_icon="C", layout="wide")


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(34, 211, 238, 0.14), transparent 26%),
                radial-gradient(circle at top right, rgba(20, 184, 166, 0.12), transparent 24%),
                linear-gradient(165deg, #06111f 0%, #091624 38%, #0b1220 100%);
            color: #f8fafc;
        }
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 2rem;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(7, 18, 31, 0.98), rgba(8, 25, 40, 0.96));
            border-right: 1px solid rgba(148, 163, 184, 0.14);
        }
        .app-hero, .app-card, .login-shell, .metric-card, .glass-card {
            border: 1px solid rgba(148, 163, 184, 0.16);
            box-shadow: 0 16px 40px rgba(2, 8, 23, 0.34);
        }
        .app-hero {
            background: linear-gradient(135deg, rgba(12, 20, 36, 0.95), rgba(9, 32, 52, 0.92));
            border-radius: 28px;
            padding: 1.5rem 1.7rem;
            margin-bottom: 1rem;
        }
        .app-hero h1 {
            margin: 0;
            font-size: 2.2rem;
            color: #f8fafc;
        }
        .app-hero p {
            margin: 0.4rem 0 0 0;
            color: #cbd5e1;
            font-size: 1rem;
        }
        .app-card {
            background: rgba(8, 15, 28, 0.88);
            border-radius: 24px;
            padding: 1.2rem;
            margin-bottom: 1rem;
        }
        .metric-card {
            background: linear-gradient(145deg, rgba(10, 23, 39, 0.98), rgba(14, 34, 53, 0.94));
            border-radius: 22px;
            padding: 1rem 1.1rem;
            min-height: 118px;
        }
        .metric-label {
            color: #94a3b8;
            font-size: 0.9rem;
            margin-bottom: 0.35rem;
        }
        .metric-value {
            color: #f8fafc;
            font-size: 1.72rem;
            font-weight: 700;
        }
        .metric-subtext {
            color: #cbd5e1;
            font-size: 0.92rem;
            margin-top: 0.35rem;
        }
        .login-container {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 70vh;
        }
        .login-card {
            background: rgba(15, 23, 42, 0.4);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 30px;
            width: 100%;
            max-width: 320px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
        }
        .login-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 30px 60px -12px rgba(34, 211, 238, 0.2);
            border-color: rgba(34, 211, 238, 0.35);
        }
        .login-header {
            margin-bottom: 2rem;
        }
        .login-header h2 {
            margin: 0 0 8px 0;
            font-size: 1.8rem;
            font-weight: 700;
            text-align: center;
            background: linear-gradient(135deg, #06b6d4, #14b8a6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .login-header p {
            margin: 0;
            color: #94a3b8;
            text-align: center;
            font-size: 0.95rem;
        }


        .status-banner {
            background: linear-gradient(135deg, rgba(8, 53, 66, 0.95), rgba(17, 94, 89, 0.92));
            border: 1px solid rgba(45, 212, 191, 0.28);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            color: #ecfeff;
            margin-bottom: 1rem;
        }
        .result-badge {
            display: inline-block;
            padding: 0.55rem 1rem;
            border-radius: 999px;
            font-weight: 700;
            color: white;
            font-size: 1.05rem;
            margin-bottom: 0.8rem;
        }
        .glass-card {
            background: rgba(15, 23, 42, 0.62);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            margin-bottom: 1rem;
        }
        .section-title {
            color: #f8fafc;
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }
        .soft-text {
            color: #cbd5e1;
            line-height: 1.55;
        }
        .pipeline-box {
            background: linear-gradient(145deg, rgba(8, 29, 46, 0.92), rgba(10, 40, 62, 0.9));
            border: 1px solid rgba(34, 211, 238, 0.18);
            border-radius: 20px;
            padding: 1rem;
            text-align: center;
            color: #f8fafc;
            font-weight: 700;
        }
        .history-chip {
            padding: 0.24rem 0.7rem;
            border-radius: 999px;
            color: #0f172a;
            font-weight: 700;
            font-size: 0.82rem;
            display: inline-block;
        }
        .nav-title {
            color: #f8fafc;
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.75rem;
        }
        .nav-current {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(20, 184, 166, 0.14));
            border: 1px solid rgba(34, 211, 238, 0.22);
            border-radius: 14px;
            padding: 0.7rem 0.85rem;
            margin-bottom: 0.9rem;
            color: #ecfeff;
            font-weight: 700;
        }
        .history-table {
            width: 100%;
            border-collapse: collapse;
        }
        .history-table th {
            color: #94a3b8;
            text-align: left;
            font-size: 0.9rem;
            font-weight: 600;
            padding: 0.7rem 0.55rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.16);
        }
        .history-table td {
            padding: 0.8rem 0.55rem;
            border-bottom: 1px solid rgba(148, 163, 184, 0.10);
            color: #e2e8f0;
            font-size: 0.94rem;
        }
        .history-disease {
            display: inline-block;
            padding: 0.28rem 0.65rem;
            border-radius: 999px;
            font-weight: 700;
            color: #ffffff;
            font-size: 0.83rem;
        }
        .stButton > button {
            background: linear-gradient(135deg, #06b6d4, #14b8a6);
            color: #f8fafc;
            border: none;
            border-radius: 14px;
            padding: 0.68rem 1rem;
            font-weight: 700;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 24px rgba(20, 184, 166, 0.28);
        }
        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stDateInput > div > div,
        .stFileUploader section,
        .stRadio > div {
            background: rgba(15, 23, 42, 0.82) !important;
            border-radius: 14px !important;
        }
        .stMarkdown, .stSubheader, label, p, h1, h2, h3, h4, h5, h6 {
            color: #f8fafc !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_plotly(fig):
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.35)",
        font=dict(color="#e2e8f0"),
        margin=dict(l=24, r=24, t=36, b=24),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig.update_xaxes(showgrid=False, linecolor="rgba(148,163,184,0.2)")
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.14)", zerolinecolor="rgba(148,163,184,0.14)")
    return fig


def render_metric(label: str, value: str, subtext: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    if "history" not in st.session_state:
        st.session_state.history = build_seed_history()
    if "current_result" not in st.session_state:
        st.session_state.current_result = None
    if "last_scan_hash" not in st.session_state:
        st.session_state.last_scan_hash = None


def build_seed_history() -> List[Dict[str, object]]:
    base_time = datetime.now() - timedelta(days=6)
    samples = [
        ("SCAN-2401", "CT Scan", "COVID-19", 86.2),
        ("SCAN-2402", "Chest X-Ray", "Pneumonia", 79.8),
        ("SCAN-2403", "CT Scan", "Normal", 81.1),
        ("SCAN-2404", "Chest X-Ray", "Tuberculosis", 74.6),
        ("SCAN-2405", "Chest X-Ray", "Pneumonia", 83.5),
        ("SCAN-2406", "CT Scan", "COVID-19", 88.4),
        ("SCAN-2407", "Chest X-Ray", "Normal", 77.9),
    ]
    history = []
    for idx, (scan_id, modality, disease, confidence) in enumerate(samples):
        history.append(
            {
                "scan_id": scan_id,
                "scan_name": f"study_{scan_id.lower()}.png",
                "modality": modality,
                "predicted_disease": disease,
                "confidence": confidence,
                "timestamp": (base_time + timedelta(days=idx, hours=idx + 8)).strftime("%Y-%m-%d %H:%M"),
            }
        )
    return history


def image_to_seed(image_bytes: bytes, modality: str) -> int:
    digest = hashlib.sha256(image_bytes + modality.encode("utf-8")).hexdigest()
    return int(digest[:16], 16)


def infer_modality(uploaded_file) -> str:
    name = uploaded_file.name.lower()
    if "ct" in name or "scan" in name:
        return "CT Scan"
    if "xray" in name or "cxr" in name or "chest" in name:
        return "Chest X-Ray"
    digest = hashlib.sha256(uploaded_file.getvalue()).hexdigest()
    return "CT Scan" if int(digest[:2], 16) % 2 == 0 else "Chest X-Ray"


def fake_prediction(seed: int, modality: str) -> Dict[str, object]:
    rng = np.random.default_rng(seed)
    winner_idx = int(rng.integers(0, len(LABELS)))
    winner_score = float(rng.uniform(0.62, 0.89))
    remaining = 1.0 - winner_score
    base = np.zeros(len(LABELS), dtype=float)
    base[winner_idx] = winner_score
    others = [idx for idx in range(len(LABELS)) if idx != winner_idx]
    other_scores = rng.dirichlet(np.array([2.5, 2.0, 1.6])) * remaining
    for idx, score in zip(others, other_scores):
        base[idx] = score
    probabilities = {label: round(float(score) * 100, 2) for label, score in zip(LABELS, base)}
    predicted = max(probabilities, key=probabilities.get)
    return {
        "predicted_disease": predicted,
        "probabilities": probabilities,
        "confidence": probabilities[predicted],
        "modality": modality,
        "clinical_note": CLINICAL_NOTES[predicted],
    }


def generate_heatmap(image: Image.Image, disease: str) -> Image.Image:
    base = image.convert("RGB").resize((420, 420))
    arr = np.asarray(base).astype(np.float32)
    h, w, _ = arr.shape
    y = np.linspace(0, h - 1, h)
def generate_heatmap(image: Image.Image, disease: str) -> Image.Image:
    base = image.convert("RGB").resize((420, 420))
    arr = np.asarray(base).astype(np.float32) / 255.0
    
    h, w, _ = arr.shape
    y = np.linspace(0, h - 1, h)
    x = np.linspace(0, w - 1, w)
    xx, yy = np.meshgrid(x, y)
    
    spatial_mask = np.zeros((h, w), dtype=np.float32)
    if disease == "COVID-19":
        cx1, cy1 = w * 0.30, h * 0.60
        cx2, cy2 = w * 0.70, h * 0.60
        sigma = w * 0.25
        blob1 = np.exp(-(((xx - cx1) ** 2) + ((yy - cy1) ** 2)) / (2 * sigma ** 2))
        blob2 = np.exp(-(((xx - cx2) ** 2) + ((yy - cy2) ** 2)) / (2 * sigma ** 2))
        spatial_mask = np.maximum(blob1, blob2)
    elif disease == "Pneumonia":
        cx, cy = w * 0.65, h * 0.75
        sigma = w * 0.28
        spatial_mask = np.exp(-(((xx - cx) ** 2) + ((yy - cy) ** 2)) / (2 * sigma ** 2))
    elif disease == "Tuberculosis":
        cx, cy = w * 0.35, h * 0.35
        sigma = w * 0.22
        spatial_mask = np.exp(-(((xx - cx) ** 2) + ((yy - cy) ** 2)) / (2 * sigma ** 2))
    else:
        spatial_mask = np.ones((h, w), dtype=np.float32) * 0.1
        
    gray = np.mean(arr, axis=-1)
    
    # Introduce structural features + raw randomness
    noise = np.random.rand(h, w).astype(np.float32)
    blob = spatial_mask * (gray ** 0.5) * 0.65 + noise * 0.35 * spatial_mask
    
    # Smooth heavily to mock a spatially continuous CNN feature map
    blob_uint8 = np.uint8(np.clip(blob * 255, 0, 255))
    blob_img = Image.fromarray(blob_uint8).filter(ImageFilter.GaussianBlur(16))
    blob = np.asarray(blob_img).astype(np.float32) / 255.0
    
    # Scale exactly to [0..1] range so highest activation is RED
    if blob.max() > blob.min():
        blob = (blob - blob.min()) / (blob.max() - blob.min() + 1e-8)
        
    if disease == "Normal":
        blob = blob * 0.1

    # Jet Colormap computation
    r = np.clip(1.5 - np.abs(4.0 * blob - 3.0), 0.0, 1.0)
    g = np.clip(1.5 - np.abs(4.0 * blob - 2.0), 0.0, 1.0)
    b = np.clip(1.5 - np.abs(4.0 * blob - 1.0), 0.0, 1.0)
    heatmap = np.stack([r, g, b], axis=-1)
    
    # Overlay with image
    cam = heatmap * 0.45 + arr * 0.55
    cam = np.clip(cam, 0, 1)
    
    return Image.fromarray(np.uint8(cam * 255))


def prepare_preview(image: Image.Image) -> Image.Image:
    preview = ImageOps.grayscale(image).convert("RGB")
    preview = ImageEnhance.Contrast(preview).enhance(1.28)
    return preview.resize((420, 420))


def generate_scan_id() -> str:
    serial = len(st.session_state.history) + 1
    return f"SCAN-{2400 + serial}"


def save_prediction(uploaded_file, modality: str, result: Dict[str, object], image: Image.Image, heatmap: Image.Image) -> None:
    scan_hash = hashlib.md5(uploaded_file.getvalue() + modality.encode("utf-8")).hexdigest()
    current = {
        "scan_id": generate_scan_id(),
        "scan_name": uploaded_file.name,
        "modality": modality,
        "predicted_disease": result["predicted_disease"],
        "confidence": result["confidence"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "probabilities": result["probabilities"],
        "clinical_note": result["clinical_note"],
        "image": image,
        "heatmap": heatmap,
        "scan_hash": scan_hash,
    }
    st.session_state.current_result = current
    if st.session_state.last_scan_hash != scan_hash:
        st.session_state.history.insert(
            0,
            {
                "scan_id": current["scan_id"],
                "scan_name": current["scan_name"],
                "modality": current["modality"],
                "predicted_disease": current["predicted_disease"],
                "confidence": current["confidence"],
                "timestamp": current["timestamp"],
            },
        )
        st.session_state.last_scan_hash = scan_hash


def history_frame() -> pd.DataFrame:
    if not st.session_state.history:
        return pd.DataFrame(columns=["Scan ID", "Modality", "Predicted Disease", "Confidence Score", "Timestamp"])
    return pd.DataFrame(st.session_state.history).rename(
        columns={
            "scan_id": "Scan ID",
            "modality": "Modality",
            "predicted_disease": "Predicted Disease",
            "confidence": "Confidence Score",
            "timestamp": "Timestamp",
        }
    )[["Scan ID", "Modality", "Predicted Disease", "Confidence Score", "Timestamp"]]


def dashboard_metrics_from_history():
    history = st.session_state.history
    total = len(history)
    ct = sum(1 for item in history if item["modality"] == "CT Scan")
    cxr = sum(1 for item in history if item["modality"] == "Chest X-Ray")
    avg_conf = np.mean([item["confidence"] for item in history]) if history else 0
    return total, ct, cxr, avg_conf


def disease_distribution_chart():
    df = pd.DataFrame(st.session_state.history)
    counts = df["predicted_disease"].value_counts().reindex(LABELS, fill_value=0).reset_index()
    counts.columns = ["Disease", "Count"]
    fig = px.bar(
        counts,
        x="Disease",
        y="Count",
        color="Disease",
        color_discrete_map=CLASS_COLORS,
        text="Count",
    )
    fig.update_traces(marker_line_width=0, opacity=0.92)
    fig.update_layout(showlegend=False)
    return style_plotly(fig)


def scans_per_day_chart():
    df = pd.DataFrame(st.session_state.history)
    parsed = pd.to_datetime(df["timestamp"])
    grouped = parsed.dt.date.value_counts().sort_index().reset_index()
    grouped.columns = ["Date", "Scans"]
    fig = px.line(grouped, x="Date", y="Scans", markers=True)
    fig.update_traces(line_color="#22d3ee", marker_color="#14b8a6", line_width=3)
    return style_plotly(fig)


def history_pie_chart():
    df = pd.DataFrame(st.session_state.history)
    counts = df["predicted_disease"].value_counts().reindex(LABELS, fill_value=0).reset_index()
    counts.columns = ["Disease", "Count"]
    fig = px.pie(counts, values="Count", names="Disease", color="Disease", color_discrete_map=CLASS_COLORS, hole=0.45)
    return style_plotly(fig)


def confidence_trend_chart():
    df = pd.DataFrame(st.session_state.history).copy()
    df["Timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("Timestamp")
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["Timestamp"],
            y=df["confidence"],
            mode="lines+markers",
            line=dict(color="#22d3ee", width=3),
            marker=dict(color="#f8fafc", size=8),
            fill="tozeroy",
            fillcolor="rgba(34,211,238,0.12)",
        )
    )
    fig.update_layout(yaxis_title="Confidence Score")
    return style_plotly(fig)


def disease_color(label: str) -> str:
    return CLASS_COLORS.get(label, "#94a3b8")


def clear_session_and_logout() -> None:
    st.session_state.logged_in = False
    st.session_state.page = "Dashboard"
    st.session_state.current_result = None
    st.session_state.last_scan_hash = None
    st.session_state.history = build_seed_history()
