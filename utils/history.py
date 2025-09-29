import streamlit as st
import pandas as pd
import json
import base64
from io import BytesIO
from PIL import Image
from pathlib import Path
from datetime import datetime
from fpdf import FPDF
from pathlib import Path
import cv2

# ----------------------------
# Pathing
# ----------------------------

HISTORY_FILE = Path("history.json")
CAPTURE_FOLDERS = {
    "upload": Path("captures/upload"),
    "live": Path("captures/live"),
    "word": Path("captures/word_maker"),
    "quiz": Path("captures/quiz")
}

QUIZ_DIR = Path("captures/quiz")
QUIZ_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------
# Loading Image
# ----------------------------
def _load_image(img_path, tab=None):
    """Return valid image path or None if missing."""
    p = Path(img_path)
    if p.exists():
        return str(p)
    if tab in CAPTURE_FOLDERS:
        alt_path = CAPTURE_FOLDERS[tab] / p.name
        if alt_path.exists():
            return str(alt_path)
    return None

# -------------------------
# Initialize history
# -------------------------
def _init_history():
    """Load history from file if exists, else initialize empty dict with all tabs."""
    with st.spinner("📂 Loading history..."):
        if "history" not in st.session_state or not isinstance(st.session_state.history, dict):
            HISTORY_FILE = Path("history.json")
            if HISTORY_FILE.exists():
                try:
                    with open(HISTORY_FILE, "r") as f:
                        st.session_state.history = json.load(f)
                    if "quiz" not in st.session_state.history:
                        st.session_state.history["quiz"] = []
                except Exception:
                    st.session_state.history = {"upload": [], "live": [], "word": [], "quiz": []}
            else:
                st.session_state.history = {"upload": [], "live": [], "word": [], "quiz": []}

_init_history()

# -------------------------
# PDF download helper
# -------------------------
def download_pdf(records, base_filename):
    with st.spinner("📝 Generating PDF..."):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "ASL Upload Prediction History", ln=True, align="C")
        pdf.ln(5)

        for idx, record in enumerate(records, start=1):
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"Record {idx}", ln=True)
            pdf.set_font("Arial", "", 12)

            # File Name
            pdf.cell(0, 7, f"File Name: {record.get('file','-')}", ln=True)
            # Timestamp
            pdf.cell(0, 7, f"Timestamp: {record.get('timestamp','-')}", ln=True)

            # Image
            if "image" in record and record["image"]:
                img_path = record["image"]
                if Path(img_path).exists():
                    try:
                        pdf.image(str(img_path), w=100)
                    except Exception:
                        pdf.cell(0, 7, "<Image could not be rendered>", ln=True)
                else:
                    pdf.cell(0, 7, "<Image not found>", ln=True)

            # Prediction & Confidence
            pdf.cell(0, 7, f"Prediction: {record.get('prediction','-')}", ln=True)
            pdf.cell(0, 7, f"Confidence: {record.get('confidence',0):.2%}", ln=True)

            # Predictions
            if "top5" in record:
                pdf.set_font("Arial", "B", 12)
                pdf.cell(0, 7, "Top-5 Predictions:", ln=True)
                pdf.set_font("Arial", "", 11)
                for feat in record["top5"]:
                    lbl = str(feat.get("label","-")).replace("—","-")
                    conf = feat.get("confidence",0)
                    pdf.cell(0, 6, f"  {lbl} - {conf:.2%}", ln=True)

            pdf.ln(5) 

        pdf_output = BytesIO()
        pdf.output(pdf_output)
        pdf_output.seek(0)

    st.success("✅ PDF ready for download!")
    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_output,
        file_name=f"{base_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

# -------------------------
# PDF generation
# -------------------------
def download_word_pdf(records, base_filename="word_history"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "ASL Word Maker History", ln=True, align="C")
    pdf.ln(5)

    for idx, record in enumerate(records, start=1):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Record {idx}", ln=True)
        pdf.set_font("Arial", "", 12)

        pdf.cell(0, 7, f"Word: {record.get('word','-')}", ln=True)
        pdf.cell(0, 7, f"Meaning: {record.get('meaning','-')}", ln=True)
        pdf.cell(0, 7, f"No. of Letters: {len(record.get('letters',[]))}", ln=True)

        for i, img_path in enumerate(record.get("images", []), start=1):
            pdf.cell(0, 7, f"Letter {i}: {record['letters'][i-1]}", ln=True)
            try:
                pdf.image(img_path, w=50)
            except Exception:
                pdf.cell(0, 7, "<Image could not be rendered>", ln=True)

        pdf.ln(5)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)

    st.download_button(
        label="⬇️ Download Word Maker PDF",
        data=pdf_output,
        file_name=f"{base_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

# -------------------------
# Preview Word Maker Record
# -------------------------
def preview_word_maker_records(records, selected_indices):
    """
    Preview Word Maker records in a clean format:
    - Each letter with its image
    - Final word
    - Meaning
    - Timestamp
    - Image paths
    """
    st.markdown("### 📄 Word Maker Preview")
    
    for idx in selected_indices:
        record = records[idx]
        st.markdown(f"**Record {idx+1}**")
        
        # Datetime
        st.write(f"**Datetime:** {record.get('timestamp','-')}")
        
        # Word
        st.write(f"**Word:** {record.get('word','-')}")
        
        # Meaning
        st.write(f"**Meaning:** {record.get('meaning','-')}")
        
        # Display letters with their images
        letters = record.get("letters", [])
        images = record.get("images", [])
        for i, (letter, img_path) in enumerate(zip(letters, images), start=1):
            st.markdown(f"**Letter {i}: {letter}**")
            img_file = _load_image(img_path, tab="word")
            if img_file:
                st.image(img_file, width=150)
            else:
                st.warning(f"⚠️ Image {img_path} not found.")
        
        # Show all image paths
        st.write("**Image Paths:**")
        for img_path in images:
            st.write(img_path)
        
        st.divider()

# -------------------------
# Save record to history
# -------------------------
def save_to_history(tab: str, record: dict):
    """Save a record to session_state and persist to disk, adding timestamp."""
    with st.spinner("💾 Saving record to history..."):
        _init_history()
        if tab not in st.session_state.history:
            st.session_state.history[tab] = []

        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        record["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save image(s) as .jpg
        if "image" in record and record["image"] is not None:
            img_path = record["image"]
            img_filename = QUIZ_DIR / f"quiz_{timestamp}.jpg"
            
            # Load image from dataset folder if it's a path
            img = Image.open(img_path) if isinstance(img_path, (str, Path)) else img_path
            
            # Save to quiz folder
            img.save(img_filename)
            record["image"] = str(img_filename)

        # For Word Maker: multiple letter images
        if tab == "word" and "images" in record:
            word_dir = CAPTURE_FOLDERS["word"] / timestamp
            word_dir.mkdir(parents=True, exist_ok=True)
            new_image_paths = []
            for i, img in enumerate(record["images"], start=1):
                img_path = word_dir / f"{i}_{record['letters'][i-1]['label']}_{timestamp}.jpg"
                if hasattr(img, "shape"):
                    cv2.imwrite(str(img_path), img)
                elif isinstance(img, Image.Image):
                    img.save(img_path)
                new_image_paths.append(img_path)
            record["images"] = [str(p) for p in new_image_paths]

        st.session_state.history[tab].append(record)

        # Persist to JSON
        with open(HISTORY_FILE, "w") as f:
            json.dump(st.session_state.history, f, indent=2)
    
    st.success("✅ Record saved to History")

# -------------------------
# Download helper
# -------------------------
def download_file(data, base_filename, fmt):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{base_filename}_{timestamp}.{fmt}"
    mime = "text/csv" if fmt == "csv" else "application/json"
    st.download_button(label=f"⬇️ Download {fmt.upper()}", data=data, file_name=filename, mime=mime)

# -------------------------
# Show history
# -------------------------
def show():
    _init_history()
    
    st.sidebar.success("🤟 To Check your activities or Download them Select Different Tabs.")
    
    st.title("📜 Prediction History")

    tabs = st.tabs(["📂 Upload", "🎥 Live Camera", "📝 Word Maker"])
    tab_keys = ["upload", "live", "word"]

    for i, key in enumerate(tab_keys):
        with tabs[i]:
            records = st.session_state.history.get(key, [])
            if not records:
                st.info(f"No {key} history yet.")
                continue
            
            def safe_val(val):
                if isinstance(val, list) or isinstance(val, dict):
                    return str(val)
                return val

            df = pd.DataFrame([
                {k: ("<Image>" if k == "image" else safe_val(v)) for k, v in r.items() if k not in ("top5",)}
                for r in records
            ])
            st.dataframe(df, use_container_width=True)

            select_all = st.checkbox("Select All Records", key=f"select_all_{key}")

            selected_indices = []
            if select_all:
                selected_indices = list(range(len(records)))
            else:
                selected_indices = st.multiselect(
                    "Select records to preview/download:",
                    options=list(range(len(records))),
                    format_func=lambda x: f"{x+1}: {records[x].get('timestamp','No Timestamp')}",
                    key=f"select_records_{key}"
                )
            
            if selected_indices:
                st.markdown("### 💾 Download Options")
                chosen_formats = st.multiselect(
                    "Select format(s) to download:",
                    options=["CSV","JSON","PDF"],
                    default=[],
                    key=f"download_formats_{key}"
                )
                with st.spinner("🔍 Preparing preview..."):
                    selected_records = [records[i] for i in selected_indices]
                    for fmt in chosen_formats:
                        if fmt == "CSV":
                            download_file(pd.DataFrame(selected_records).to_csv(index=False), f"{key}_history", "csv")
                        elif fmt == "JSON":
                            download_file(json.dumps(selected_records, indent=2), f"{key}_history", "json")
                        elif fmt == "PDF":
                            if key == "word":
                                download_word_pdf(selected_records)
                            else:
                                download_pdf(selected_records, f"{key}_history")
                
                    st.markdown("---")
                    
                    st.markdown("### 📄 Preview Selected Records")
                    for idx in selected_indices:
                        record = records[idx]
                        
                        if key == "word":
                            st.markdown(f"**Record {idx+1}**")
                            st.write(f"**Word:** {record.get('word','-')}")
                            st.write(f"**Meaning:** {record.get('meaning','-')}")
                            st.write(f"**File Name:** {record.get('file','-')}")
                            st.write(f"**Captured At:** {record.get('datetime','-')}")

                            letters = record.get("letters", [])
                            images = record.get("images", [])
                            if letters and images:
                                st.write("#### Letters & Images")
                                cols = st.columns(len(letters))
                                for i, (letter, img_path) in enumerate(zip(letters, images)):
                                    with cols[i]:
                                        st.write(f"Letter: {letter['label']}")
                                        img_file = _load_image(img_path, tab="word")
                                        if img_file:
                                            st.image(img_file, use_container_width=True)
                                        else:
                                            st.warning(f"⚠️ Image not found: {img_path}")
                            st.divider()
                        else:
                            st.markdown(f"**Record {idx+1}**")
                            st.write(f"**File:** {record.get('file','-')}")
                            st.write(f"**Prediction:** {record.get('prediction','-')}")
                            st.write(f"**Confidence:** {record.get('confidence',0):.2%}")
                            st.write(f"**Timestamp:** {record.get('timestamp','-')}")

                            if "top5" in record:
                                st.write("#### 🔝 Top-5 Predictions")
                                for feat in record["top5"]:
                                    st.progress(min(1.0, feat["confidence"]))
                                    st.write(f"**{feat['label']}** — {feat['confidence']:.2%}")

                            if "image" in record and record["image"]:
                                img_path = record["image"]
                                if Path(img_path).exists():
                                    st.image(img_path)
                                else:
                                    try:
                                        img_data = base64.b64decode(img_path)
                                        st.image(Image.open(BytesIO(img_data)))
                                    except Exception:
                                        st.warning("⚠️ Image could not be loaded.")

                            st.divider()

