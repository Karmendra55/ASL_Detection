import streamlit as st 

# -------------------
# --- Page config ---
# -------------------
st.set_page_config(
    page_title="ASL Sign Detector",
    page_icon="🤟",
    layout='wide'
)

from src.config import MODEL_PATH, CLASS_MAP_JSON 
from src.infer import ASLClassifier 
from utils import (
    about,
    history,
    live_camera,
    sample_gestures,
    upload_prediction,
    word_maker
)

# --------------------------
# --- Sidebar Navigation ---
# --------------------------
with st.sidebar:
    st.markdown("### 📌 Navigation")

    menu = st.selectbox(
        "Choose a page",
        [
            "🏠 Home",
            "📩 Upload Prediction",
            "📷 Live Detection",
            "🔤 Word Maker",
            "📑 History",
            "🙌 Sample Gestures"
        ],
        label_visibility="collapsed"
    )
    st.caption("Navigate the Different Features from the Side Bar")
    st.markdown("---")

# --------------
# --- Header ---
# --------------
st.markdown("<br>", unsafe_allow_html=True)
st.title("🤟 American Sign Language (ASL) Detector")
st.caption(
    "<p style='font-size:16px; color:skyblue;'>"
    "Easily recognize ASL signs from images or live camera input, It Supports 29 classes (A–Z, SPACE, DELETE, NOTHING)."
    "</p>",
    unsafe_allow_html=True
)

# --------------------
# --- Model Loader ---
# --------------------
@st.cache_resource
def load_classifier():
    return ASLClassifier(MODEL_PATH, CLASS_MAP_JSON)

clf = load_classifier()

# -------------------
# --- Page Router ---
# -------------------
page_map = {
    "🏠 Home": ("About", about.show),
    "📩 Upload Prediction": ("Upload Prediction", upload_prediction.pred),
    "📷 Live Detection": ("Live Detection", lambda: live_camera.show(clf)),
    "🔤 Word Maker": ("Word Maker", lambda: word_maker.show(clf)),
    "🙌 Sample Gestures": ("Sample Gestures", sample_gestures.show),
    "📑 History": ("History", history.show),
}
st.divider()

page_title, page_func = page_map[menu]
page_func()

# --------------
# --- Footer ---
# --------------
st.markdown("---")

st.markdown(
    "<p style='text-align: center; color: grey; font-size:14px;'>"
    " | Developed by <b>Karmendra Srivastava</b> | "
    "</p>",
    unsafe_allow_html=True
)