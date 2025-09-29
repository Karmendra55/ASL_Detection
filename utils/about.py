import streamlit as st

# ----------------------
# --- Cached Content ---
# ----------------------
@st.cache_data
def _get_app_info():
    return {
        "title": "🤟 ASL Detection & Word Maker",
        "intro": """

            Welcome to the **🤟 ASL Detection & Word Maker Web Application**!
            
            This project is designed to help learners, enthusiasts, and practitioners of **American Sign Language (ASL)** engage with technology to learn, practice, and recognize gestures effectively.
        """,
        "objective": """
            ### 🎯 Our Goal
            The main goal of this project is to create an **AI-driven ASL recognition system** that:   
            - Empowers ASL learners with interactive tools   
            - Enhances communication through gesture recognition   
            - Makes ASL practice engaging, fun, and accessible   
        """,
        "asl_features": [
            ("🏠", "**Home** → Introduction and overview of the application and the functionality of how ASL Works"),
            ("📤", "**Upload Prediction** → Upload an image and the system predicts the ASL letter and saves it to history"),
            ("📷", "**Live Camera Prediction** → Use webcam for real-time gesture predictions, Capture results into history"),
            ("🔡", "**Word Maker** → Capture multiple letter in sequence to form a word; app displays the word with meaning"),
            ("✋", "**Sample Gestures** → Learn how to make ASL letters with reference images and descriptions"),
            ("🎮", "**Quiz Game** → An interactive game with 10 random gesture images where user guess the correct letter"),
        ],
    }

def show():
    info = _get_app_info()
    st.sidebar.success("👋 Hey, To navigate the features use the sidebar to explore.")

    with st.container():
        st.markdown(info["intro"])
        st.info("AI-powered tool to learn and practice American Sign Language (ASL).")

    st.divider()

    # -----------------
    # --- Objective ---
    # -----------------
    st.markdown(info["objective"])
    st.divider()

    st.subheader("✨ Key Features")
    col1, col2 = st.columns(2, gap="large")
    for i, (emoji, text) in enumerate(info["asl_features"]):
        with [col1, col2][i % 2]:
            st.markdown(f"**{emoji}** {text}")

    st.divider()

    # ---------------------
    # --- About Section ---
    # ---------------------
    st.header("ℹ️ About This App")

    def expander(title: str, content: str, expanded=False):
        with st.expander(title, expanded=expanded):
            st.markdown(content)

    expander("📘 What is this app?", """
        The **ASL Detection & Word Maker** helps users learn and practice 
        American Sign Language by recognizing hand gestures.  

        ✨ Capture individual letters → Combine into words → Get instant meanings!
    """)

    expander("🤖 How does it predict?", """
        - The camera or uploaded image captures your hand gesture  
        - The image is preprocessed (resized to 160×160, normalized)  
        - A **deep learning CNN model** predicts probabilities for all letters  
        - The **most likely letter** is displayed instantly  
        - The result can be saved in history for **later reference or downloads**   
    """)

    expander("🧠 Model Details", """
        - **Architecture**: Convolutional Neural Network (CNN)  
        - **Training Data**: Publicly available ASL gesture dataset  
        - **Preprocessing**: Image resizing, normalization, and batching  
        - **Output Classes**: 26 letters (A–Z), plus `Del`, `Space`, `Nothing`  
        - **Training**: Conducted on **PowerShell + Jupyter**  
        - **Accuracy**: Achieved ~**98%** accuracy after **5–6 hours** of training   
    """)

    expander("📄 Outputs & Interaction", """
        - Real-time **letter recognition** via webcam  
        - **Upload-based predictions** with saved history  
        - Interactive **word construction** with dictionary lookup  
        - Fun **quiz mode** to test knowledge of ASL symbols  
        - Flexible **history export** options: JPG, CSV, JSON    
    """)

    expander("📬 Feedback & Credits", """
        👨‍💻 Developed by **Karmendra Bahadur Srivastava**  
        🎓 Built as part of the **Unified Mentor ASL Project**  
        ⚙️ Dataset provided by **Kaggle & Grasskonoted**  
        📖 Special Thanks to provide the meanings: **DictionaryAPI**
        
        ✉️ Contact: [karmendra5902@gmail.com](mailto:karmendra5902@gmail.com) 
    """)

    # ----------------
    # --- End Card ---
    # ----------------
    st.divider()
    st.info("💡 Tip: Use the sidebar to try **Live Detection** and **Word Maker** features.")
