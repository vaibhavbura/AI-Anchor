import streamlit as st
import requests
import time
from typing import Literal
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:1234")

# Constants
SOURCE_TYPES = Literal["news", "reddit", "both"]

# Custom CSS for professional styling
st.markdown("""
<style>
    .header { 
        color: #2c3e50; 
        font-weight: 700; 
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    .section-title { 
        border-bottom: 2px solid #e5e7eb; 
        padding-bottom: 0.5rem; 
        margin-top: 1.5rem;
        color: #1e3a8a;
        font-weight: 600;
    }
    .highlight-box { 
        border-radius: 0.5rem; 
        padding: 1.5rem; 
        background-color: #f8f9fa; 
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }
    .success-box { 
        background-color: #f0fdf4; 
        color: #166534; 
        padding: 1rem; 
        border-radius: 0.5rem;
        border: 1px solid #bbf7d0;
        margin: 1rem 0;
    }
    .error-box { 
        background-color: #fef2f2; 
        color: #b91c1c; 
        padding: 1rem; 
        border-radius: 0.5rem;
        border: 1px solid #fecaca;
        margin: 1rem 0;
    }
    .stButton>button {
        background-color: #2563eb;
        color: white;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        border: none;
    }
    .stButton>button:hover {
        background-color: #1d4ed8;
        color: white;
    }
    .secondary-button>button {
        background-color: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
    }
    .secondary-button>button:hover {
        background-color: #e2e8f0;
        color: #334155;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------
def main(): 
    st.set_page_config(
        page_title="AI News Anchor", 
        layout="centered", 
        page_icon="▶️",
        initial_sidebar_state="expanded"
    )
    
    st.title("AI News Anchor")
    st.markdown("<p class='header'>Generate professional audio news summaries from multiple sources</p>", unsafe_allow_html=True)

    # Session states
    if 'topics' not in st.session_state:
        st.session_state.topics = []
    if 'input_key' not in st.session_state:
        st.session_state.input_key = 0
    if 'last_generated' not in st.session_state:
        st.session_state.last_generated = None
    if 'generation_status' not in st.session_state:
        st.session_state.generation_status = None

    # ----------------------------------------
    # Sidebar Configuration
    with st.sidebar:
        st.header("Configuration")
        source_type = st.selectbox(
            "Content Sources",
            options=["both", "news", "reddit"],
            index=0,
            format_func=lambda x: "News + Social Media" if x == "both" else ("News" if x == "news" else "Social Media")
        )
        
        st.markdown("---")
        st.caption("Add a topic below to generate your audio news summary")

    # ----------------------------------------
    # Topic Management
    st.markdown("<div class='section-title'>Topic Selection</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([4, 1])
    with col1:
        new_topic = st.text_input(
            "Enter news topic",
            key=f"topic_input_{st.session_state.input_key}",
            placeholder="e.g., Artificial Intelligence, Global Markets, Climate Policy"
        )
    with col2:
        st.write("")  # Vertical alignment
        st.write("")
        add_disabled = len(st.session_state.topics) >= 1 or not new_topic.strip()
        if st.button("Add Topic", disabled=add_disabled, use_container_width=True):
            st.session_state.topics.append(new_topic.strip())
            st.session_state.input_key += 1
            st.rerun()

    # Display selected topic
    if st.session_state.topics:
        st.markdown("<div class='highlight-box'>", unsafe_allow_html=True)
        st.markdown("**Selected Topic**")
        for i, topic in enumerate(st.session_state.topics[:3]):
            cols = st.columns([6, 1])
            cols[0].markdown(f"{topic}")
            if cols[1].button("Remove", key=f"remove_{i}"):
                del st.session_state.topics[i]
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("Please add a topic to generate an audio summary")

    # ----------------------------------------
    # Audio Generation Section
    st.markdown("<div class='section-title'>Audio Production</div>", unsafe_allow_html=True)
    st.markdown("Generate a professional news audio summary using the selected topic.")
    
    # Status containers
    status_container = st.container()
    result_container = st.container()
    error_container = st.container()
    
    # Generate button
    if st.button("Generate Audio Summary", 
                 disabled=len(st.session_state.topics) == 0,
                 type="primary",
                 use_container_width=True,
                 key="generate_button"):
        
        st.session_state.generation_status = "processing"
        st.session_state.last_generated = None
        
        with status_container:
            with st.status("Starting audio production process...", expanded=True) as status:
                # Processing steps
                steps = [
                    ("Collecting latest sources", 15),
                    ("Analyzing content trends", 30),
                    ("Generating news script", 50),
                    ("Creating professional narration", 70),
                    ("Finalizing audio output", 100)
                ]
                
                progress_bar = st.progress(0, text="Initializing production pipeline...")
                
                # Simulated progress
                for step_text, progress_value in steps:
                    time.sleep(0.8)
                    progress_bar.progress(progress_value, text=step_text)
                
                try:
                    # Actual API call
                    response = requests.post(
                        f"{BACKEND_URL}/generate-news-audio",
                        json={
                            "topics": st.session_state.topics,
                            "source_type": source_type
                        },
                        timeout=300
                    )
                    
                    if response.status_code == 200:
                        # Save the audio file
                        audio_filename = "news-summary.mp3"
                        with open(audio_filename, "wb") as f:
                            f.write(response.content)
                            
                        status.update(label="Audio production completed", state="complete")
                        st.session_state.generation_status = "success"
                        st.session_state.last_generated = audio_filename
                    else:
                        status.update(label=f"API Error ({response.status_code})", state="error")
                        st.session_state.generation_status = "error"
                        handle_api_error(response, error_container)
                        
                except requests.exceptions.ConnectionError:
                    status.update(label="Backend connection failed", state="error")
                    st.session_state.generation_status = "error"
                    error_container.markdown("<div class='error-box'>", unsafe_allow_html=True)
                    error_container.error("Unable to connect to processing server. Please check your connection.")
                    error_container.markdown("</div>", unsafe_allow_html=True)
                except requests.exceptions.Timeout:
                    status.update(label="Request timed out", state="error")
                    st.session_state.generation_status = "error"
                    error_container.markdown("<div class='error-box'>", unsafe_allow_html=True)
                    error_container.error("Processing took too long. Please try again with a different topic.")
                    error_container.markdown("</div>", unsafe_allow_html=True)
                except Exception as e:
                    status.update(label="Unexpected error", state="error")
                    st.session_state.generation_status = "error"
                    error_container.markdown("<div class='error-box'>", unsafe_allow_html=True)
                    error_container.error(f"System error: {str(e)}")
                    error_container.markdown("</div>", unsafe_allow_html=True)
    
    # Display results
    with result_container:
        if st.session_state.generation_status == "success" and st.session_state.last_generated:
            st.markdown("<div class='success-box'>", unsafe_allow_html=True)
            st.markdown("**Audio Production Complete**")
            
            # Audio player
            st.audio(st.session_state.last_generated, format="audio/mp3")
            
            # Download button
            with open(st.session_state.last_generated, "rb") as f:
                audio_data = f.read()
                
            st.download_button(
                label="Download Audio",
                data=audio_data,
                file_name="ai_news_summary.mp3",
                mime="audio/mpeg",
                use_container_width=True
            )
            st.caption("This professional news summary is ready for distribution")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Reset option
            st.markdown("<div class='secondary-button'>", unsafe_allow_html=True)
            if st.button("Create Another Summary", use_container_width=True):
                st.session_state.last_generated = None
                st.session_state.generation_status = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
def handle_api_error(response, container):
    try:
        error_detail = response.json().get("detail", "Unknown error")
        if isinstance(error_detail, list):
            error_detail = ", ".join([err['msg'] for err in error_detail if 'msg' in err])
        container.markdown("<div class='error-box'>", unsafe_allow_html=True)
        container.error(f"**Processing Error ({response.status_code}):** {error_detail}")
        container.markdown("</div>", unsafe_allow_html=True)
    except ValueError:
        container.markdown("<div class='error-box'>", unsafe_allow_html=True)
        container.error(f"**Unexpected Response:** {response.text[:500]}")
        container.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------
if __name__ == "__main__":
    main()