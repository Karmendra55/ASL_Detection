import os
import cv2
import time
import numpy as np
import av
import streamlit as st

from PIL import Image
from pathlib import Path
from datetime import datetime
from streamlit_webrtc import webrtc_streamer, VideoProcessorBase
from utils.history import save_to_history

# ---------------------------
# --- Pathing and Loading ---
# ---------------------------
CAPTURE_DIR = Path("captures/live")
CAPTURE_DIR.mkdir(parents=True, exist_ok=True)
os.makedirs(CAPTURE_DIR, exist_ok=True)

class ASLProcessor(VideoProcessorBase):
    """
    Video processor for Streamlit WebRTC.
    Handles live ASL predictions.
    """
    def __init__(self, clf, cooldown=2.0):
        self.clf = clf
        self.cooldown = cooldown
        self.last_prediction = None
        self.pred_label = "Waiting..."
        self.last_pred_time = 0
        self.last_frame = None

    def recv(self, frame):
        """
        Receive frame from WebRTC, run prediction every `cooldown` seconds,
        overlay label, and return processed frame.
        """
        img = frame.to_ndarray(format="bgr24")
        self.last_frame = img
        now = time.time()

        if now - self.last_pred_time > self.cooldown:
            try:
                # Always pass raw frame to classifier
                x = preprocess_frame(img)           
                probs = self.clf.model.predict(x)[0]
                idx = int(np.argmax(probs))
                self.pred_label = self.clf.class_names[idx]
                self.last_prediction = {
                    "label": self.pred_label,
                    "index": idx,
                    "confidence": float(probs[idx]),
                    "probs": {self.clf.class_names[i]: float(p) for i, p in enumerate(probs)}
                }
                self.last_pred_time = now
            except Exception as e:
                self.pred_label = f"Prediction failed: {e}"
                self.last_prediction = None

        cv2.putText(
            img,
            f"Prediction: {self.pred_label}",
            (10, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

        return av.VideoFrame.from_ndarray(img, format="bgr24")

def preprocess_frame(frame):
    """
    frame: np.ndarray (BGR)
    returns: np.ndarray, shape (1, 160, 160, 3), normalized
    """
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (160, 160)) 
    img = img.astype(np.float32) / 255.0
    return np.expand_dims(img, axis=0)

def save_snapshot(clf, frame, top_k=5):
    """
    Save a snapshot and return top_k predictions.
    """
    img = frame if isinstance(frame, np.ndarray) else frame.to_ndarray(format="bgr24")
    result = clf.predict(img)
    probs = result["probs"]
    results = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return results

def show_letter_capture(clf):
    """
    Opens a short camera session to capture a single ASL letter.
    Returns (predicted_letter, frame) or (None, None) if failed.
    """
    st.info("📸 Position your hand for letter detection and click 'Capture Letter'")

    camera_container = st.empty()
    captured_letter = None
    frame = None

    with camera_container:
        ctx = webrtc_streamer(
            key="asl-letter-capture",
            video_processor_factory=lambda: ASLProcessor(clf, cooldown=0.0),
            media_stream_constraints={"video": True, "audio": False},
        )

    if ctx and ctx.video_processor and st.button("📸 Capture Letter"):
        frame = ctx.video_processor.last_frame
        if frame is not None:
            camera_container.empty()

            x = preprocess_frame(frame)
            probs = clf.model.predict(x)[0]
            idx = int(np.argmax(probs))
            captured_letter = clf.class_names[idx]

            col_img, col_info = st.columns([1, 2])
            with col_img:
                st.subheader("📷 Captured Image")
                st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_container_width=True)

            with col_info:
                st.subheader("🔮 Prediction Result")
                st.success(f"Prediction: **{captured_letter}**")
        else:
            st.warning("⚠️ No frame captured yet.")

    return captured_letter, frame

def _render_top_predictions(top5):
    st.subheader("📊 Top Predictions")
    for item in top5:
        label, conf = item["label"], item["confidence"]
        st.progress(int(conf * 100))
        st.write(f"**{label}** — {conf:.2%}")

def show(clf):
    st.sidebar.success("🤟 Press Start and Select the Device to Get Live Predictions.")
    
    st.subheader("📷 ASL Live Camera Detection")
    st.markdown("Real-time ASL letter recognition using your webcam.")
    st.divider()

    if "camera_mode" not in st.session_state:
        st.session_state.camera_mode = "live"
        st.session_state.last_frame = None
        st.session_state.last_preds = None

    container = st.empty()

    if st.session_state.camera_mode == "live":
        st.info("🎥 Start the camera and show your ASL gesture.")
        ctx = webrtc_streamer(
            key="asl-live",
            video_processor_factory=lambda: ASLProcessor(clf, cooldown=1.5),
            media_stream_constraints={"video": True, "audio": False},
        )
        


        if ctx and ctx.video_processor and st.button("📸 Capture Snapshot", use_container_width=True):
            frame = ctx.video_processor.last_frame
            if frame is not None:
                with st.spinner("⚙️ Processing snapshot..."):
                    img_filename = CAPTURE_DIR / f"asl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                    cv2.imwrite(str(img_filename), frame)

                    x = preprocess_frame(frame)
                    probs = clf.model.predict(x, verbose=0)[0]
                    pred_idx = int(np.argmax(probs))
                    pred_label = clf.class_names[pred_idx]
                    pred_conf = float(probs[pred_idx])

                    top5 = sorted(
                        [{"label": clf.class_names[i], "confidence": float(p)} for i, p in enumerate(probs)],
                        key=lambda x: x["confidence"], reverse=True,
                    )[:5]

                    st.session_state.last_frame = frame
                    st.session_state.last_preds = (pred_label, pred_conf, top5, img_filename)
                    st.session_state.camera_mode = "result"
                    st.rerun()
            else:
                st.warning("⚠️ No frame captured yet.")

    elif st.session_state.camera_mode == "result":
        st.success("✅ Snapshot Captured Successfully!")
        st.markdown("### Results")
        frame = st.session_state.last_frame
        pred_label, pred_conf, top5, img_filename = st.session_state.last_preds

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="📷 Captured Frame", use_container_width=True)
        with col2:
            st.success(f"**Predicted Letter:** {pred_label}")
            st.caption(f"Confidence: {pred_conf:.2%}")
            _render_top_predictions(top5)

        save_to_history("live", {
            "file": str(img_filename.resolve()),
            "image": str(img_filename.resolve()),
            "prediction": pred_label,
            "confidence": pred_conf,
            "top5": top5
        })
        st.caption("📌 Saved to history for later reference.")
        
        st.markdown("---")
        if st.button("🔄 Retake"):
            st.session_state.camera_mode = "live"
            st.rerun()
        st.caption("Tip : The Image is Saved, Press Retake to Take Another Capture Picture.")