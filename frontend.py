import streamlit as st
import requests
from typing import Literal

# Constants
SOURCE_TYPES = Literal["news", "reddit", "both"]
BACKEND_URL = "http://localhost:1234"  # 🔁 Replace with your FastAPI server IP

# ----------------------------------------
def main(): 
    st.set_page_config(page_title="AI Anchor", layout="centered", page_icon="🎥")
    st.title("🎥 AI Anchor")
    st.markdown("##### Your AI-powered news presenter – generating video summaries with real-time Reddit insight.")

    # 🧠 Session states
    if 'topics' not in st.session_state:
        st.session_state.topics = []
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0

    # ----------------------------------------
    # 📊 Sidebar Settings
    with st.sidebar:
        st.header("⚙️ Settings")
        source_type = st.selectbox(
            "Select Content Source",
            options=["both", "news", "reddit"],
            index=0,
            format_func=lambda x: f"🌐 News + Reddit" if x == "both" else f"{'🌐 News' if x == 'news' else '📑 Reddit'}"
        )
        st.markdown("---")
        st.info("Only one topic allowed per video for now.")

    # ----------------------------------------
    # 📝 Topic Management
    st.markdown("### 📝 Choose a Topic")
    col1, col2 = st.columns([4, 1])
    with col1:
        new_topic = st.text_input(
            "Enter a topic (e.g. Artificial Intelligence, Elections, Global Warming)",
            key=f"topic_input_{st.session_state.input_key}"
        )
    with col2:
        add_disabled = len(st.session_state.topics) >= 1 or not new_topic.strip()
        if st.button("➕ Add", disabled=add_disabled):
            st.session_state.topics.append(new_topic.strip())
            st.session_state.input_key += 1
            st.rerun()

    # 🔄 Display selected topic
    if st.session_state.topics:
        st.markdown("#### ✅ Selected Topic")
        for i, topic in enumerate(st.session_state.topics[:3]):
            cols = st.columns([6, 1])
            cols[0].markdown(f"**{i+1}.** {topic}")
            if cols[1].button("❌", key=f"remove_{i}"):
                del st.session_state.topics[i]
                st.rerun()
    else:
        st.warning("Add a topic to continue.")

    st.markdown("---")

    # ----------------------------------------
    # 🎬 Video Generation Section
    st.markdown("### 🎬 Generate AI Video")
    st.markdown("Click the button below to fetch news & Reddit data, generate TTS voiceover, and create an AI video anchor.")

    if st.button("🚀 Generate Video", disabled=len(st.session_state.topics) == 0):
        with st.spinner("🧠 Generating AI summary and creating video..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/generate-news-video",
                    json={
                        "topics": st.session_state.topics,
                        "source_type": source_type
                    },
                    timeout=300
                )
                if response.status_code == 200:
                    data = response.json()
                    video_url = data.get("video_url")

                    if video_url:
                        st.success("✅ Video successfully generated!")
                        st.video(video_url)
                        st.markdown(
                            f"[📥 Download Video]({video_url})",
                            unsafe_allow_html=True
                        )
                        st.markdown("---")
                        st.info("Share this video with your team or community!")
                    else:
                        st.error("❌ No video URL returned by the server.")
                else:
                    handle_api_error(response)
            except requests.exceptions.ConnectionError:
                st.error("🔌 Connection Error: Backend server is unreachable.")
            except Exception as e:
                st.error(f"⚠️ Unexpected Error: {str(e)}")

# ----------------------------------------
def handle_api_error(response):
    try:
        error_detail = response.json().get("detail", "Unknown error")
        st.error(f"API Error ({response.status_code}): {error_detail}")
    except ValueError:
        st.error(f"Unexpected API Response: {response.text}")

# ----------------------------------------
if __name__ == "__main__":
    main()
