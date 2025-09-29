import streamlit as st
import requests
import cv2

from datetime import datetime
from PIL import Image
from pathlib import Path
from utils.live_camera import show_letter_capture
from utils.history import save_to_history

# ---------------------------
# --- Pathing and Loading ---
# ---------------------------
CAPTURE_DIR = Path("captures/word_maker")
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------
# --- Saving Records ---
# ----------------------
def save_word_record():
    final_word = "".join(st.session_state.letters)
    meaning = lookup_word(final_word.lower())

    image_files = []
    for i, img in enumerate(st.session_state.images, start=1):
        filename = CAPTURE_DIR / f"{final_word}_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        if hasattr(img, "shape"):
            img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        else:
            img_pil = img
        img_pil.save(filename, format="JPEG")
        image_files.append(str(filename))

    record = {
        "word": final_word,
        "meaning": meaning,
        "letters": [{"label": l} for l in st.session_state.letters],
        "images": image_files,
        "file": f"{final_word}.jpg",
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with st.spinner("💾 Saving to history..."):
        save_to_history("word", record)

# -------------------------
# --- Dictionary Lookup ---
# -------------------------
def lookup_word(word: str) -> str:
    """
    Fetch word meaning from Free Dictionary API.
    """
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    try:
        with st.spinner("📖 Looking up meaning..."):
            response = requests.get(url, timeout=5).json()
        if isinstance(response, list) and "meanings" in response[0]:
            return response[0]["meanings"][0]["definitions"][0]["definition"]
        return "No valid meaning found (possibly gibberish)."
    except Exception:
        return "⚠️ Error while fetching meaning."

# ------------------------------
# --- Letter Capture Display ---
# ------------------------------
def display_captures():
    """Show all captured letters with images + predictions."""
    st.subheader("📷 Captured Letters")

    for i, (letter, img) in enumerate(zip(st.session_state.letters, st.session_state.images)):
        label = ["First", "Second", "Third", "Fourth", "Fifth"][i] if i < 5 else f"{i+1}th"

        with st.container():
            st.markdown(f"### {label} Letter")
            col1, col2 = st.columns([1, 2])

            with col1:
                if img is not None:
                    st.image(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), use_container_width=True)
                else:
                    st.warning("⚠️ No image captured for this letter.")

            with col2:
                st.success(f"Prediction: **{letter}**")

def show(clf):
    """
    Streamlit UI for ASL Word Maker.
    """

    st.sidebar.success("🤟 Select Number of Letters and Start the Device to Make a word with Signs.")
    
    st.title("📝 ASL Word Maker")
    st.caption("Spell words in ASL and get instant definitions!")

    if "letters" not in st.session_state:
        st.session_state.letters = []
    if "images" not in st.session_state:
        st.session_state.images = []
    if "current_capture" not in st.session_state:
        st.session_state.current_capture = None 

    st.subheader("⚙️ Settings")
    num_letters = st.number_input("Word length (Max. 18 Characters)", min_value=1, max_value=18, step=1)

    if st.button("🔄 Reset"):
        st.session_state.letters.clear()
        st.session_state.images.clear()
        st.session_state.current_capture = None
        st.success("✅ Word builder reset!")
        st.rerun()
        
    if len(st.session_state.letters) < num_letters:
        st.info(f"👉 Capture letter **{len(st.session_state.letters) + 1} of {num_letters}**")
        
        with st.spinner("📸 Waiting for capture..."):
            captured = show_letter_capture(clf) 

        if captured:
            letter, frame = captured
            if letter and frame is not None:
                st.session_state.letters.append(letter)
                st.session_state.images.append(frame)
                st.success(f"✅ Captured: {letter}")
    else:
        st.success("🎉 All letters captured!")

    if st.session_state.letters:
        display_captures()

    if len(st.session_state.letters) == num_letters:
        final_word = "".join(st.session_state.letters)
        
        st.markdown("---")
        st.subheader("✨ Final Result")
        
        st.success(f"📝 Word: **{final_word}**")
        meaning = lookup_word(final_word.lower())
        st.info(f"📖 Meaning: {meaning}")

        image_paths = []
        for i, (letter, img) in enumerate(zip(st.session_state.letters, st.session_state.images), start=1):
            img_filename = f"{final_word}_{i}_{letter}.jpg"  
            img_path = CAPTURE_DIR / img_filename

            if hasattr(img, "shape"):
                img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            else:
                img_pil = img

            img_pil.save(img_path, format="JPEG")
            image_paths.append(str(img_path))

        word_record = {
            "word": final_word,
            "meaning": meaning,
            "letters": [{"label": l} for l in st.session_state.letters],
            "images": image_paths,
            "file": f"{final_word}.jpg",
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_to_history("word", word_record)