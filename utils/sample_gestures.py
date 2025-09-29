import os
import random
from pathlib import Path
from PIL import Image
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from fpdf import FPDF
import io
import time

# ----------------------------
# PATHS
# ----------------------------
GESTURE_PATH = "gestures"
DATA_ROOT = Path("data")       
DATASET_PATH = DATA_ROOT / "asl_alphabet_train"

# ----------------------------
# CHARACTER GROUPS
# ----------------------------
CHARACTERS = [chr(i) for i in range(65, 91)] + ["space", "del", "nothing"]

VARIANTS = ["_test.jpg", "_test1.jpg", "_test2.jpg"]

CHAR_GROUPS = [
    ("A-D", ["A", "B", "C", "D"]),
    ("E-H", ["E", "F", "G", "H"]),
    ("I-L", ["I", "J", "K", "L"]),
    ("M-P", ["M", "N", "O", "P"]),
    ("Q-T", ["Q", "R", "S", "T"]),
    ("U-X", ["U", "V", "W", "X"]),
    ("Y, Z", ["Y", "Z"]),
    ("Specials", ["space", "del", "nothing"]),
]

# ----------------------------
# INFO TEXTS
# ----------------------------
INFO = {
    "A": "✊ Make a fist with your thumb resting along the side of your closed fingers (next to the index finger).",
    "B": "✋ Hold your hand upright, fingers straight and together, palm facing forward. Tuck your thumb across your palm.",
    "C": "👌 Curve your hand into the shape of the letter C, fingers curved and thumb opposite.",
    "D": "☝️ Hold up your index finger while touching your thumb to the tips of your middle, ring, and pinky fingers.",
    "E": "🤏 Curl your fingers downward to touch your thumb, forming a small rounded shape (like squeezing).",
    "F": "👌 Touch the tip of your thumb to the tip of your index finger to form a circle. Extend the other three fingers upward.",
    "G": "👉 Hold your hand flat, palm facing sideways. Extend your thumb and index finger parallel (like showing ‘a little bit’).",
    "H": "✌️ Extend your index and middle fingers forward together, palm sideways. Tuck the other fingers down with thumb against them.",
    "I": "🤙 Make a fist and extend only your pinky finger upward.",
    "J": "〰️ Start with the ‘I’ handshape, then trace the letter ‘J’ in the air using your pinky finger.",
    "K": "🖖 Extend your index and middle fingers upward in a V-shape. Place your thumb in between them. Keep ring and pinky tucked.",
    "L": "📐 Extend your thumb and index finger at a right angle (like an ‘L’ shape). Tuck in the other three fingers.",
    "M": "✋ Tuck your thumb under your index, middle, and ring fingers, leaving your pinky extended.",
    "N": "✌️ Tuck your thumb under your index and middle fingers, leaving ring and pinky extended.",
    "O": "⭕ Curve all your fingers and thumb together to touch, forming a round ‘O’ shape.",
    "P": "📌 Form the ‘K’ shape (index and middle extended, thumb in between) and tilt it downward (palm facing ground).",
    "Q": "🔻 Form the ‘G’ shape (thumb and index finger pointing forward) and tilt it downward (like holding something).",
    "R": "🤞 Cross your index and middle fingers, keeping the other fingers curled and thumb against them.",
    "S": "✊ Make a tight fist with the thumb wrapped across the front of your fingers.",
    "T": "✊ Make a fist and tuck your thumb between your index and middle fingers (peeking out slightly).",
    "U": "✌️ Extend your index and middle fingers straight together, palm forward. Keep thumb holding the other fingers down.",
    "V": "✌️ Extend your index and middle fingers in a V-shape, palm forward. Keep thumb holding the other fingers down.",
    "W": "🖖 Extend your index, middle, and ring fingers apart to form a ‘W’. Keep pinky and thumb tucked in.",
    "X": "⚡ Curl your index finger downward (like a hook) while keeping other fingers in a fist. Thumb rests on the fist.",
    "Y": "🤙 Extend your thumb and pinky finger out to the sides. Keep the other three fingers tucked in.",
    "Z": "〽️ Extend your index finger and draw the shape of the letter ‘Z’ in the air.",
    "space": "␣ Use this gesture to indicate a space between words (separating them while spelling).",
    "del": "⌫ This gesture is used to delete or remove the last signed letter.",
    "nothing": "🚫 Represents no input — hand relaxed or neutral when not signing."
}

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def load_gesture_images(char):
    """Load up to 3 images for a given character if they exist."""
    images = []
    for variant in VARIANTS:
        img_path = os.path.join(GESTURE_PATH, f"{char}{variant}")
        if os.path.exists(img_path):
            images.append(img_path)
    return images

def show_gesture_page(group_name, chars):
    """Show gestures for a group of characters in two columns (A,C | B,D)."""
    st.subheader(f"Gestures: {group_name}")
    col1, col2 = st.columns(2)

    for i, char in enumerate(chars):
        target_col = col1 if i % 2 == 0 else col2
        with target_col:
            st.markdown(f"### {char}")
            with st.spinner(f"📷 Loading examples for {char}..."):
                images = load_gesture_images(char)
            if images:
                img_cols = st.columns(len(images))  # show them side by side
                for idx, (img_path, c) in enumerate(zip(images, img_cols)):
                    with c:
                        st.image(
                            Image.open(img_path),
                            caption=f"{char} - Example {idx+1}",
                            use_container_width=True,
                        )
            else:
                st.warning(f"No images found for {char}")
            
            with st.expander(f"ℹ️ More about {char}"):
                st.write(INFO.get(char, "No description available yet."))

def pick_random_gesture():
    """Pick a random image from dataset."""
    with st.spinner("🎲 Picking a random gesture..."):
        gesture = random.choice([f.name for f in DATASET_PATH.iterdir() if f.is_dir()])
        folder = DATASET_PATH / gesture
        image_file = random.choice(os.listdir(folder))
        return folder / image_file, gesture

# ----------------------------
# DIFFICULTY
# ----------------------------
def easy_mode(correct_answer, options):
    # Initialize session state for selection
    if "easy_selected" not in st.session_state:
        st.session_state.easy_selected = None
    if "easy_submitted" not in st.session_state:
        st.session_state.easy_submitted = False

    st.write("### Easy Mode: Choose the correct option")

    # Show options as buttons
    for opt in options:
        if st.button(opt, key=f"easy_{opt}"):
            st.session_state.easy_selected = opt

    if st.session_state.easy_selected:
        st.write(f"✅ You selected: **{st.session_state.easy_selected}**")

    if st.button("Submit Guess"):
        st.session_state.easy_submitted = True

    if st.session_state.easy_submitted:
        if st.session_state.easy_selected == correct_answer:
            st.success("Correct! 🎉")
        else:
            st.error(f"Wrong ❌, correct answer is **{correct_answer}**")
        # Reset for next question
        st.session_state.easy_selected = None
        st.session_state.easy_submitted = False
        
def medium_mode(correct_answer, all_labels):
    import random
    # Always define options before using
    options = random.sample(all_labels, 3)  # 3 random wrongs
    if correct_answer not in options:
        options.append(correct_answer)
    random.shuffle(options)

    st.write("### Medium Mode: Pick from dropdown")
    guess = st.selectbox("Choose your answer:", options)

    if st.button("Submit Guess (Medium)"):
        if guess == correct_answer:
            st.success("Correct! 🎉")
        else:
            st.error(f"Wrong ❌, correct answer: {correct_answer}")

def hard_mode(correct_answer, all_labels):
    import random
    # Create options for hard mode
    options = random.sample(all_labels, 5)  # more confusion
    if correct_answer not in options:
        options.append(correct_answer)
    random.shuffle(options)

    st.write("### Hard Mode: Type your guess")
    guess = st.text_input("Enter your guess:")

    if st.button("Submit Guess (Hard)"):
        if guess.strip().lower() == correct_answer.lower():
            st.success("Correct! 🎉")
        else:
            st.error(f"Wrong ❌, correct answer: {correct_answer}")

# ----------------------------
# MAIN APP
# ----------------------------
def show():
    # ---------- Sidebar ----------
    st.sidebar.success("🎮 The CheatSheet of Symbols and A quiz game to have fun learning.")
    tab1, tab2 = st.tabs(["📖 Gesture Reference", "🎮 Quiz Game"])
    
    # --------------------------
    # TAB 1: Reference
    # --------------------------
    with tab1:
        st.title("📖 ASL Gesture Reference")
        st.caption("Browse through the American Sign Language alphabet with visual examples and instructions.")

        try:
            if not os.path.exists(GESTURE_PATH):
                raise FileNotFoundError("Gesture Folder is missing.")
            
            group_names = [name for name, _ in CHAR_GROUPS]
            selected_group = st.selectbox("🔎 Jump to Group:", group_names)
            for name, chars in CHAR_GROUPS:
                if name == selected_group:
                    show_gesture_page(name, chars)
                    break
        
        except FileNotFoundError as e:
            st.error("⚠️ Gesture Folder not found! Please download it and place inside the `gestures/` folder.")
            st.stop()

        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {e}")
            st.stop()

    # --------------------------
    # TAB 2: Quiz Game
    # --------------------------
    with tab2:
        st.title("🎮 ASL Gesture Quiz")
        st.caption("Test your ASL knowledge — guess the sign from the image! You have **10 rounds**.")

        try:
            if not os.path.exists(DATASET_PATH):
                raise FileNotFoundError("Dataset folders not found")
            # --------------------------
            # Difficulty Selector
            # --------------------------
            if "difficulty" not in st.session_state:
                st.session_state.difficulty = None  # not chosen yet

            if st.session_state.difficulty is None:
                st.markdown("## 🎚️ Choose Your Difficulty")
                st.caption("Pick how challenging you want the quiz to be:")

                col1, col2, col3 = st.columns(3)

                def difficulty_card(icon, title, desc, color, difficulty):
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="border:2px solid {color}; border-radius:12px; padding:20px; text-align:center;">
                                <h3 style="margin:0;">{icon} {title}</h3>
                                <p style="color:gray; margin-top:5px;">{desc}</p>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button(f"▶️ Start {title}", use_container_width=True, key=f"btn_{difficulty}"):
                            st.session_state.difficulty = difficulty
                            st.rerun()
                
                with col1:
                    difficulty_card("🟢", "Easy", "Multiple choice with 4 options.", "#2ecc71", "Easy")

                with col2:
                    difficulty_card("🟡", "Medium", "Pick from dropdown (all letters).", "#f1c40f", "Medium")

                with col3:
                    difficulty_card("🔴", "Hard", "Blurred image + type your guess (15s).", "#e74c3c", "Hard")

                st.stop()
            
            # --------------------------
            # Initialize Session State
            # --------------------------
            if "score" not in st.session_state:
                st.session_state.score = 0
            if "rounds" not in st.session_state:
                st.session_state.rounds = 0
            if "quiz_results" not in st.session_state:
                st.session_state.quiz_results = []  # Store results for PDF
            if "current_image" not in st.session_state:
                st.session_state.current_image, st.session_state.correct_label = pick_random_gesture()
            if "awaiting_next" not in st.session_state:
                st.session_state.awaiting_next = False

            # --------------------------
            # Game Finished
            # --------------------------
            if st.session_state.rounds >= 10:
                st.balloons()
                st.success(f"🎉 Game Over! Final Score: **{st.session_state.score} / {st.session_state.rounds}**")

                st.subheader("📊 Results Summary")
                for idx, entry in enumerate(st.session_state.quiz_results, start=1):
                    col1, col2, col3, col4 = st.columns([1,1.5,1.5,1])
                    with col1:
                        st.image(Image.open(entry["image"]), width=70)
                    with col2:
                        st.markdown(f"**Prediction:** {entry['guess']}")
                    with col3:
                        st.markdown(f"**Actual:** {entry['correct']}")
                    with col4:
                        st.markdown("✅ **Correct**" if entry["result"] else "❌ **Wrong**")
                        
                st.divider()

                # --------------------------
                # Generate PDF Button
                # --------------------------
                with st.spinner("📝 Generating quiz report PDF..."):
                    pdf = FPDF()
                    pdf.set_auto_page_break(auto=True, margin=15)
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 16)
                    pdf.cell(0, 10, f"ASL Quiz Results - Score: {st.session_state.score}/10", ln=True, align='C')
                    pdf.ln(10)

                    for idx, entry in enumerate(st.session_state.quiz_results, start=1):
                        pdf.set_font("Arial", 'B', 12)
                        pdf.cell(0, 10, f"Round {idx}:", ln=True)
                        pdf.set_font("Arial", '', 12)
                        pdf.cell(0, 8, f"Prediction: {entry['guess']}", ln=True)
                        pdf.cell(0, 8, f"Actual: {entry['correct']}", ln=True)
                        pdf.cell(0, 8, f"Result: {'Correct' if entry['result'] else 'Wrong'}", ln=True)
                        # Add image
                        pdf.image(str(entry["image"]), w=50)
                        pdf.ln(15)

                    pdf_buffer = io.BytesIO()
                    pdf.output(pdf_buffer)
                    pdf_buffer.seek(0)
                    st.success("The PDF is ready to be Downloaded!")
                    st.download_button("📥 Download PDF Results", data=pdf_buffer, file_name="asl_quiz_results.pdf")

                if st.button("🔄 Play Again"):
                    with st.spinner("♻️ Resetting game..."):
                        st.session_state.score = 0
                        st.session_state.rounds = 0
                        st.session_state.quiz_results = []
                        st.session_state.current_image, st.session_state.correct_label = pick_random_gesture()
                        st.session_state.awaiting_next = False
                        st.session_state.difficulty = None
                        st.rerun()
                st.stop()

            # --------------------------
            # Current Round
            # --------------------------
            st.markdown(f"### 🖼️ Round {st.session_state.rounds + 1} of 10")
            
            # Use a center column for image + inputs
            _, c, _ = st.columns([2.5, 2, 2.5])
            with c:
                if st.session_state.difficulty in ["Easy", "Medium"]:
                    st.image(Image.open(st.session_state.current_image), width=300, caption="What ASL sign is this?")

            # --------------------------
            # User Guess
            # --------------------------
            if not st.session_state.awaiting_next:
                user_guess = None

                _, c, _ = st.columns([2, 2.5, 2])
                with c:
                    # ---------------- EASY MODE ----------------
                    if st.session_state.difficulty == "Easy":
                        if "easy_options" not in st.session_state or st.session_state.rounds != st.session_state.get("easy_round", -1):
                            incorrect_options = random.sample(
                                [c for c in CHARACTERS if c != st.session_state.correct_label], 3
                            )
                            st.session_state.easy_options = incorrect_options + [st.session_state.correct_label]
                            random.shuffle(st.session_state.easy_options)
                            st.session_state.easy_round = st.session_state.rounds
                            st.session_state.easy_selected = None 

                        st.write("### Easy Mode: Choose the correct option")

                        # Display option buttons
                        cols = st.columns(2)
                        for i, opt in enumerate(st.session_state.easy_options):
                            if cols[i % 2].button(
                                opt,
                                key=f"easy_{opt}_{st.session_state.rounds}"
                            ):
                                st.session_state.easy_selected = opt

                        if st.session_state.easy_selected:
                            st.info(f"✅ Selected: **{st.session_state.easy_selected}**")

                        user_guess = st.session_state.easy_selected

                    # ---------------- MEDIUM MODE ----------------
                    elif st.session_state.difficulty == "Medium":
                        options = CHARACTERS  # full list
                        user_guess = st.selectbox(
                            "✋ Choose your answer:",
                            options,
                            key=f"guess_{st.session_state.rounds}"
                        )

                    # ---------------- HARD MODE ----------------
                    elif st.session_state.difficulty == "Hard":
                        # ---- Safe initialisation (only create keys if missing) ----
                        if "hard_round" not in st.session_state:
                            st.session_state.hard_round = -1
                        if "hard_revealed" not in st.session_state:
                            st.session_state.hard_revealed = False
                        if "hard_locked" not in st.session_state:
                            st.session_state.hard_locked = False
                        if "hard_start_time" not in st.session_state:
                            st.session_state.hard_start_time = None
                        if "hard_guess" not in st.session_state:
                            st.session_state.hard_guess = ""

                        # Reset per-round state only when the round number actually changes
                        if st.session_state.hard_round != st.session_state.rounds:
                            st.session_state.hard_revealed = False
                            st.session_state.hard_locked = False
                            st.session_state.hard_start_time = None
                            st.session_state.hard_guess = ""
                            st.session_state.hard_round = st.session_state.rounds

                        img = Image.open(st.session_state.current_image).convert("RGB")

                        # ---- BLURRED STATE ----
                        if not st.session_state.hard_revealed:
                            blurred = img.resize((max(1, img.width // 10), max(1, img.height // 10))).resize(img.size)
                            st.image(blurred, caption="🔒 Blurred! Click below to reveal...")

                            if st.button("👀 Reveal Image", use_container_width=True, key=f"reveal_{st.session_state.rounds}"):
                                st.session_state.hard_revealed = True
                                st.session_state.hard_start_time = time.time()
                                st.session_state.hard_locked = False
                                st.session_state.hard_guess = ""
                                st.rerun()

                            st.stop()

                        # ---- REVEALED STATE ----
                        st.image(img, caption="⏳ Guess quickly!")
                        timer_placeholder = st.empty()

                        if st.session_state.hard_start_time is None:
                            st.session_state.hard_start_time = time.time()

                        elapsed = int(time.time() - st.session_state.hard_start_time)
                        remaining = max(0, 15 - elapsed)

                        timer_placeholder.warning(f"⏳ Time left: {remaining} seconds")

                        if remaining > 0 and not st.session_state.hard_locked:
                            st.session_state.hard_guess = st.text_input(
                                "⌨️ Type your answer:",
                                value=st.session_state.hard_guess,
                                key=f"guess_{st.session_state.rounds}"
                            ).strip()
                        else:
                            st.session_state.hard_locked = True
                            timer_placeholder.info("⏳ Time is up! Please submit or skip to next round.")

                        raw_guess = st.session_state.hard_guess
                        if raw_guess:
                            if raw_guess.lower() in ["space", "del", "nothing"]:
                                user_guess = raw_guess.lower()
                            else:
                                user_guess = raw_guess.upper()
                        else:
                            user_guess = None

                        # ---- Submit button ----
                        if st.button("✅ Submit Guess", use_container_width=True, key=f"hard_submit_{st.session_state.rounds}"):
                            st.session_state.rounds += 1
                            final_guess = user_guess if user_guess else "⏳ No Answer"
                            result = (final_guess == st.session_state.correct_label)

                            if result:
                                st.session_state.score += 1

                            st.session_state.quiz_results.append({
                                "image": st.session_state.current_image,
                                "guess": final_guess,
                                "correct": st.session_state.correct_label,
                                "result": result
                            })

                            st.session_state.last_guess = st.session_state.quiz_results[-1]
                            st.session_state.awaiting_next = True
                            st.session_state.hard_revealed = False
                            st.session_state.hard_locked = False
                            st.session_state.hard_start_time = None
                            st.session_state.hard_guess = ""
                            st.session_state.hard_round = st.session_state.rounds

                            st.rerun()

                        if remaining > 0:
                            time.sleep(1)
                            st.rerun()

                    # ---------------- SUBMIT ----------------
                    if st.session_state.difficulty in ["Easy", "Medium"]:
                        if st.button("✅ Submit Guess", use_container_width=True):
                            if user_guess:
                                st.session_state.rounds += 1
                                result = (user_guess == st.session_state.correct_label)

                                if result:
                                    st.session_state.score += 1

                                st.session_state.quiz_results.append({
                                    "image": st.session_state.current_image,
                                    "guess": user_guess,
                                    "correct": st.session_state.correct_label,
                                    "result": result
                                })

                                st.session_state.last_guess = st.session_state.quiz_results[-1]
                                st.session_state.awaiting_next = True

                                st.rerun()

            # --------------------------
            # Feedback
            # --------------------------
            else:
                last_entry = st.session_state.last_guess
                st.markdown("### 📝 Last Round Feedback")
                col1, col2 = st.columns(2)

                with col1:
                    st.write(f"**Your Guess:** {last_entry['guess']}")
                    st.write(f"**Correct Answer:** {last_entry['correct']}")

                with col2:
                    if last_entry["result"]:
                        st.success("🎉 Correct!")
                    else:
                        st.error("❌ Oops, Wrong!")

                st.divider()
                if st.button("➡️ Next Round", use_container_width=True):
                    st.session_state.current_image, st.session_state.correct_label = pick_random_gesture()
                    st.session_state.awaiting_next = False
                    if st.session_state.difficulty == "Hard":
                        st.session_state.timer = 10  # reset timer
                    st.rerun()

            # --------------------------
            # Score Tracker
            # --------------------------
            progress = st.session_state.rounds / 10
            st.progress(progress)
            st.info(f"📊 Score: **{st.session_state.score} / {st.session_state.rounds}**")
        
        except FileNotFoundError as e:
            st.error("⚠️ Dataset not found! Please download it and place inside the `data/asl_alphabet_test and data/asl_alphabet_train` folders.")
            with st.expander("Download"):
                st.link_button("📥 Kaggle Dataset", "https://www.kaggle.com/datasets/grassknoted/asl-alphabet")
            st.stop()

        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {e}")
            with st.expander("Donwload the Dataset"):
                st.link_button("📥 Kaggle Dataset", "https://www.kaggle.com/datasets/grassknoted/asl-alphabet")
            st.stop()