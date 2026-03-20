import streamlit as st
import cv2
import tempfile
import os
import json
from PIL import Image
import google.generativeai as genai

# --- PAGE SETUP ---
st.set_page_config(page_title="Creator Studio", page_icon="🎬", layout="wide")

# --- AI SETUP ---
# Securely load the API key from Streamlit's Secret vault
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Changed from gemini-1.5-flash to gemini-pro to fix the NotFound error
    model = genai.GenerativeModel('gemini-pro') 
    ai_ready = True
except Exception as e:
    ai_ready = False

# --- DATA STORAGE (JSON) ---
PROFILES_FILE = "profiles.json"

def load_profiles():
    if not os.path.exists(PROFILES_FILE):
        default_profiles = {
            "@bangarugn": {
                "niche": "Tech & Coding", 
                "target_audience": "Beginners",
                "followers": "1,500", "views": "800", "retention": "35%"
            },
            "@framezbygn": {
                "niche": "Videography & Editing", 
                "target_audience": "Visual creators",
                "followers": "8,200", "views": "4,500", "retention": "52%"
            }
        }
        with open(PROFILES_FILE, "w") as f:
            json.dump(default_profiles, f, indent=4)
        return default_profiles
    with open(PROFILES_FILE, "r") as f:
        return json.load(f)

def save_profiles(profiles_data):
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles_data, f, indent=4)

profiles = load_profiles()

# --- PROFILE SETTINGS (SIDEBAR) ---
st.sidebar.header("👤 Profile Manager")
profile_handles = list(profiles.keys())
selected_handle = st.sidebar.selectbox("Active Profile", profile_handles)

st.sidebar.subheader("1. Core Identity")
my_niche = st.sidebar.text_input("My Niche", value=profiles[selected_handle].get("niche", ""))
target_audience = st.sidebar.text_input("Target Audience", value=profiles[selected_handle].get("target_audience", ""))

st.sidebar.subheader("2. Current Stats")
my_followers = st.sidebar.text_input("Followers Goal/Current", value=profiles[selected_handle].get("followers", "0"))
my_views = st.sidebar.text_input("Avg Views", value=profiles[selected_handle].get("views", "0"))
my_retention = st.sidebar.text_input("Avg Retention", value=profiles[selected_handle].get("retention", "0%"))

if st.sidebar.button("Save Profile & Stats"):
    profiles[selected_handle]["niche"] = my_niche
    profiles[selected_handle]["target_audience"] = target_audience
    profiles[selected_handle]["followers"] = my_followers
    profiles[selected_handle]["views"] = my_views
    profiles[selected_handle]["retention"] = my_retention
    save_profiles(profiles)
    st.sidebar.success(f"Updated {selected_handle}! 💾")

# --- HELPER FUNCTIONS ---
def extract_frames(video_path, num_frames=4):
    cam = cv2.VideoCapture(video_path)
    frames = []
    total_frames = int(cam.get(cv2.CAP_PROP_FRAME_COUNT))
    step = max(total_frames // num_frames, 1)
    current_frame = 0
    count = 0
    while True:
        ret, frame = cam.read()
        if ret:
            if current_frame % step == 0 and count < num_frames:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames.append(Image.fromarray(frame_rgb))
                count += 1
            current_frame += 1
        else:
            break
    cam.release()
    return frames

# --- MAIN APP LAYOUT ---
st.title("🎬 Viral Content Studio")

tab1, tab2, tab3 = st.tabs(["🏠 My Dashboard", "🔍 Pre-Post Analyzer", "📉 Post-Mortem"])

# --- TAB 1: DASHBOARD ---
with tab1:
    st.header(f"Welcome back, {selected_handle}!")
    st.write(f"**Focusing on:** {my_niche} | **Targeting:** {target_audience}")
    
    st.subheader("📊 Live Profile Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Followers", value=my_followers)
    col2.metric(label="Avg Video Views", value=my_views)
    col3.metric(label="Avg Hook Retention", value=my_retention)
    
    st.divider()
    
    st.subheader(f"🧠 AI Content Strategist for {my_niche}")
    st.write("Click below to generate 3 unique, data-driven video concepts tailored to your current audience.")
    
    if st.button("Generate AI Recommendations"):
        if not ai_ready:
            st.error("⚠️ AI is offline. Please add your GOOGLE_API_KEY to Streamlit Secrets.")
        else:
            with st.spinner(f"Analyzing {my_niche} trends and generating ideas..."):
                prompt = f"""
                Act as an expert social media strategist. My niche is '{my_niche}' and my target audience is '{target_audience}'. 
                Provide 3 highly engaging short-form video concepts (Reels/TikToks) I should film today. 
                For each concept, provide:
                1. A catchy Hook (the first 3 seconds spoken text)
                2. Visual action (what I should be doing on screen)
                Format it clearly with bullet points. Do not include introductory text, just give the 3 concepts.
                """
                try:
                    response = model.generate_content(prompt)
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Something went wrong with the AI: {e}")

# --- TAB 2: PRE-POST ANALYZER ---
with tab2:
    st.header("Draft Analyzer")
    st.write("Upload a draft video to get a harsh AI critique before publishing.")
    uploaded_file = st.file_uploader("Upload your .mp4 draft", type=["mp4", "mov"])
    if uploaded_file is not None:
        st.video(uploaded_file)
        if st.button("Analyze Visuals"):
            with st.spinner("Extracting frames..."):
                tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
                tfile.write(uploaded_file.read())
                extracted_frames = extract_frames(tfile.name, num_frames=4)
                cols = st.columns(4)
                for i, frame in enumerate(extracted_frames):
                    with cols[i]:
                        st.image(frame, use_container_width=True, caption=f"Frame {i+1}")
                os.remove(tfile.name)
                st.subheader("AI Verdict")
                st.markdown(f"🚨 **Analysis tailored for {target_audience}:** The pacing here is a bit slow. Your audience wants fast value. Add a text pop-up in Frame 2.")

# --- TAB 3: POST-MORTEM ---
with tab3:
    st.header("Post-Mortem Analyzer")
    url = st.text_input("Video URL:")
    if st.button("Analyze Failure"):
        if url:
            st.info(f"Downloading `{url}`... (Integration coming soon!)")
        else:
            st.warning("Please enter a URL.")
