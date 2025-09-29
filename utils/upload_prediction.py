import streamlit as st
from PIL import Image
import math
from pathlib import Path
from datetime import datetime

from src.config import MODEL_PATH, CLASS_MAP_JSON 
from src.infer import ASLClassifier 
from utils.history import save_to_history

# ---------------------------
# --- Pathing and Loading ---
# ---------------------------
CAPTURE_DIR = Path("captures/upload")
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

def load_classifier(): 
    with st.spinner("⚙️ Loading ASL Classifier... Please wait"):
        return ASLClassifier(MODEL_PATH, CLASS_MAP_JSON)  

# ------------------------
# --- Prediction Logic ---
# ------------------------
def pred():
    clf = None 
    try: 
        clf = load_classifier() 
    except Exception as e: 
        st.warning("⚠️ Model not found. Train the model first (see README).") 
        st.exception(e) 
        return  

    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = 0
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []

    st.sidebar.success("🤟 Upload the Image to get the Prediction of that Hand Made Sign Symbol.")

    st.subheader("🖖 ASL Alphabet Static Image Recognition")
    st.markdown(
        "Upload one or more **images of American Sign Language gestures** "
        "to get real-time predictions with confidence scores."
    )

    multi_upload = st.checkbox("Upload multiple images", value=False)

    # ---------------------
    # --- File Uploader ---
    # ---------------------
    uploaded_files = st.file_uploader(
        "Upload ASL image(s)", 
        type=["jpg", "jpeg", "png"], 
        accept_multiple_files=multi_upload,
        key=f"file_uploader_{st.session_state.file_uploader_key}"
    )

    if uploaded_files:
        st.session_state.uploaded_files = uploaded_files

    # --------------------
    # --- Clear Button ---
    # --------------------
    if st.session_state.uploaded_files:
        st.markdown("### 📂 Uploaded Images")
        if st.button("🗑️ Clear All Images", type="secondary"):
            st.session_state.uploaded_files = []
            st.session_state.file_uploader_key += 1 
            st.rerun()

    uploaded_files = st.session_state.uploaded_files

    # ---------------------------
    # --- If no file Selected ---
    # ---------------------------
    if not uploaded_files:
        st.info("📥 Upload one or more images above to see predictions.")
        st.caption("💡 Tip: Check the box above to allow multiple uploads.")
        return

    st.markdown("---")
    if uploaded_files and clf:
        if not multi_upload:
            uploaded_files = [uploaded_files]  

        per_page = 5
        total_pages = math.ceil(len(uploaded_files) / per_page)

        page_num = 0
        if total_pages > 1:
            page_num = st.selectbox(
                "📑 Select page", 
                options=list(range(total_pages)), 
                format_func=lambda x: f"Page {x+1} of {total_pages}"
            )

        start = page_num * per_page
        end = start + per_page
        page_files = uploaded_files[start:end]

        for uploaded in page_files:
            image = Image.open(uploaded)

            img_filename = CAPTURE_DIR / f"{uploaded.name.split('.')[0]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            image.save(img_filename)

            with st.container():
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(image, caption=uploaded.name, use_container_width=True)
                with col2:
                    with st.spinner("🔍 Running Predicting..."): 
                        pred_result = clf.predict(image) 

                    st.success(f"### ✅ Prediction: {pred_result['label']}")
                    st.write(f"**Confidence:** {pred_result['confidence']:.2%}") 

                    st.markdown("#### 🔝 Top-5 Predictions")
                    probs = sorted(pred_result['probs'].items(), key=lambda x: x[1], reverse=True)[:5] 
                    for k, v in probs:
                        pc1, pc2 = st.columns([3, 7])
                        with pc1:
                            st.write(f"**{k}**")
                        with pc2:
                            st.progress(float(v))
                            st.caption(f"{v:.2%}")
                            
            record = {
                "file": uploaded.name,
                "prediction": pred_result['label'],
                "confidence": pred_result['confidence'],
                "top5": [{"label": k, "confidence": v} for k,v in probs],
                "image": str(img_filename)
            }
            save_to_history("upload", record)
            st.caption("All results are saved in history for later reference.")
            st.markdown("---")

    st.caption("💡 Tip: Check the box above to upload multiple images together.")
