import streamlit as st
import cv2
import tempfile
import os
import json
from PIL import Image

# --- PAGE SETUP ---
st.set_page_config(page_title="Creator Studio", page_icon="🎬", layout="wide")

# --- DATA STORAGE (JSON) ---
PROFILES_FILE = "profiles.json"

def load_profiles():
    """Loads profiles from a local JSON file. Creates defaults if missing."""
    if not os.path.exists(PROFILES_FILE):
        # Default profiles for your two accounts
        default_profiles = {
            "@bangarugn": {
                "niche": "Tech & Coding", 
                "target_audience": "Beginners learning programming"
            },
            "@framezbygn": {
                "niche": "Videography & Editing", 
                "target_audience": "Visual creators and editors"
            }
        }
        with open(PROFILES_FILE, "w") as f:
            json.dump(default_profiles, f, indent=4)
        return default_profiles
    
    with open(PROFILES_FILE, "r") as f:
        return json.load(f)

def save_profiles(profiles_data):
    """Saves the updated profiles back to the JSON file."""
    with open(PROFILES_FILE, "w") as f:
        json.dump(profiles_data, f, indent=4)

# Load your profiles into the app
profiles = load_profiles()

# --- PROFILE SETTINGS (SIDEBAR) ---
st.sidebar.header("👤 Profile Manager")
st.sidebar.write("Switch between your creator accounts.")

# Dropdown to select the active profile
profile_handles = list(profiles.keys())
selected_handle = st.sidebar.selectbox("Active Profile", profile_handles)

# Display inputs loaded with the selected profile's data
st.sidebar.subheader("Edit Profile Info")
my_niche = st.sidebar.text_input("My Niche", value=profiles[selected_handle]["niche"])
target_audience = st.sidebar.text_input("Target Audience", value=profiles[selected_handle]["target_audience"])

# Save button to update the JSON file if you change the niche/audience
if st.sidebar.button("Save Changes"):
    profiles[selected_handle]["niche"] = my_niche
    profiles[selected_handle]["target_audience"] = target_audience
    save_profiles(profiles)
    st.sidebar.success(f"Updated {selected_handle}! 💾")

st.sidebar.divider()
st.sidebar.success(f"Currently analyzing for: {selected_handle} 🟢")

# --- HELPER FUNCTIONS ---
def extract_frames(video_path, num_frames=4):
    """Extracts evenly spaced frames from a video."""
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

# Create the tabs
tab1, tab2, tab3 = st.tabs(["🏠 My Dashboard", "🔍 Pre-Post Analyzer", "📉 Post-Mortem"])

# --- TAB 1: THE PERSONALIZED DASHBOARD ---
with tab1:
    st.header(f"Welcome back, {selected_handle}!")
    st.write(f"**Focusing on:** {my_niche} | **Targeting:** {target_audience}")
    
    # Dashboard Metrics
    st.subheader("📊 Quick Stats (Simulated)")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Followers Goal", value="10,000", delta="In Progress")
    col2.metric(label="Last Video Views", value="1,240", delta="-15% from avg", delta_color="inverse")
    col3.metric(label="Avg Hook Retention", value="42%", delta="Needs Work", delta_color="off")
    
    st.divider()
    
    # Personalized Recommendations
    st.subheader(f"💡 Today's Recommendations for {selected_handle}")
    st.write("Based on current platform trends, here are 3 concepts to film today:")
    
    st.info(f"""**Concept 1: The Common Mistake**
'Stop doing [Mistake] if you want to be a better {target_audience}. Do this instead...'""")
    
    st.success(f"""**Concept 2: The Fast Tutorial**
'Here is exactly how I learned {my_niche} in just 30 days.'""")
    
    st.warning(f"""**Concept 3: The Tool Reveal**
'This free tool feels illegal to know for {target_audience}.'""")