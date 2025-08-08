

import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import os
import io
import time

# Page configuration with custom styling
st.set_page_config(
    page_title="Speech to Text & Translation",
    page_icon="🎙️",
    layout="wide"
)

# Custom CSS for colorful UI
st.markdown("""
<style>
    /* Main app background gradient */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Title styling */
    .main-title {
        background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem !important;
        font-weight: bold !important;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Card-like containers */
    .custom-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    /* Success messages */
    .success-box {
        background: linear-gradient(135deg, #56ccf2, #2f80ed);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
    }
    
    /* Info messages */
    .info-box {
        background: linear-gradient(135deg, #a8e6cf, #7fcdcd);
        color: #2c3e50;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    /* Warning messages */
    .warning-box {
        background: linear-gradient(135deg, #ffd89b, #19547b);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
    }
    
    /* Error messages */
    .error-box {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        font-weight: bold;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: rgba(25, 25, 205, 0.9);
        border-radius: 10px;
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        border: 2px dashed rgba(255, 255, 255, 0.5);
    }
</style>
""", unsafe_allow_html=True)

# Main title with gradient effect
st.markdown('<h1 class="main-title">🎙️ Speech to Text & Translation App</h1>', unsafe_allow_html=True)

# Create main container
with st.container():
    st.markdown('<div class="info-box">Choose an input method: record via microphone or upload an audio file. Transcribe the audio and translate it to a selected language.</div>', unsafe_allow_html=True)

# Language selector with colorful container
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    target_language = st.selectbox(
        "🌍 Select Output Language",
        ["en", "hi", "mr"],
        format_func=lambda x: {"en": "🇺🇸 English", "hi": "🇮🇳 Hindi", "mr": "🇮🇳 Marathi"}[x]
    )

# Input method choice
st.markdown("---")
input_method = st.radio("🎯 Choose Input Method:", ["🎤 Microphone", "📁 Upload Audio File"])

recognizer = sr.Recognizer()

# Adjust recognizer settings for better performance
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8
recognizer.phrase_threshold = 0.3

def transcribe_audio(wav_path):
    """Transcribe audio file to text"""
    try:
        with sr.AudioFile(wav_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "Could not understand the audio. Please try speaking more clearly."
    except sr.RequestError as e:
        return f"Request error from Google Speech Recognition service: {e}"
    except Exception as e:
        return f"An error occurred during transcription: {e}"

def translate_text(text, lang_code):
    """Translate text to target language"""
    try:
        if text.startswith("Could not") or text.startswith("Request error") or text.startswith("An error"):
            return text
        translator = Translator()
        result = translator.translate(text, dest=lang_code)
        return result.text
    except Exception as e:
        return f"Translation error: {e}"

def record_audio_with_microphone():
    """Record audio from microphone"""
    try:
        with sr.Microphone() as source:
            st.markdown('<div class="info-box">🎤 Adjusting for ambient noise... Please wait.</div>', unsafe_allow_html=True)
            recognizer.adjust_for_ambient_noise(source, duration=1)
            st.markdown('<div class="info-box">🎤 Listening... Speak now! (You have 15 seconds)</div>', unsafe_allow_html=True)
            
            # Use longer timeout and phrase time limit
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=15)
            return audio
    except sr.WaitTimeoutError:
        st.markdown('<div class="error-box">⏰ Listening timed out. No speech detected. Please try again.</div>', unsafe_allow_html=True)
        return None
    except Exception as e:
        st.markdown(f'<div class="error-box">❌ Microphone error: {e}</div>', unsafe_allow_html=True)
        st.markdown('<div class="info-box">💡 Try these solutions:<br>• Check if your microphone is connected and working<br>• Grant microphone permissions to your browser<br>• Try refreshing the page</div>', unsafe_allow_html=True)
        return None

# Microphone input
if input_method == "🎤 Microphone":
    st.markdown("---")
    st.markdown("### 🎤 Microphone Recording")
    
    # Instructions in a colorful box
    st.markdown("""
    <div class="info-box">
        <h4>📋 Instructions for Microphone Recording:</h4>
        <ul>
            <li>🔌 Make sure your microphone is connected and working</li>
            <li>🔐 Grant microphone permissions when prompted by your browser</li>
            <li>🗣️ Speak clearly and avoid background noise</li>
            <li>⏱️ You'll have 15 seconds to speak after clicking the button</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎤 Start Recording", type="primary"):
            with st.spinner("🔧 Setting up microphone..."):
                audio = record_audio_with_microphone()
            
            if audio is not None:
                with st.spinner("🔄 Processing audio..."):
                    try:
                        # Transcribe directly from audio object
                        text = recognizer.recognize_google(audio)
                        
                        if text:
                            st.markdown('<div class="success-box">✅ Recording processed successfully!</div>', unsafe_allow_html=True)
                            
                            # Display transcribed text
                            st.markdown("### 📝 Transcribed Text:")
                            st.markdown(f"""
                            <div class="custom-container">
                                <h4 style="color: #2c3e50;">🎯 Original Text:</h4>
                                <p style="font-size: 1.2em; color: #34495e; font-weight: 500;">{text}</p>
                            </div>
                            """, unsafe_allow_html=True)

                            # Translate the text
                            with st.spinner("🌐 Translating..."):
                                translated = translate_text(text, target_language)
                            
                            # Display translated text
                            st.markdown("### 🌐 Translated Text:")
                            lang_names = {"en": "English", "hi": "Hindi", "mr": "Marathi"}
                            st.markdown(f"""
                            <div class="custom-container">
                                <h4 style="color: #2c3e50;">🌍 {lang_names[target_language]} Translation:</h4>
                                <p style="font-size: 1.2em; color: #34495e; font-weight: 500;">{translated}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Option to save the transcription
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                if st.button("💾 Save Transcription"):
                                    transcript_data = f"Original: {text}\nTranslated ({target_language}): {translated}"
                                    st.download_button(
                                        label="📄 Download Transcript",
                                        data=transcript_data,
                                        file_name=f"transcript_{int(time.time())}.txt",
                                        mime="text/plain"
                                    )
                        
                    except sr.UnknownValueError:
                        st.markdown('<div class="error-box">❌ Could not understand the audio. Please try again with clearer speech.</div>', unsafe_allow_html=True)
                    except sr.RequestError as e:
                        st.markdown(f'<div class="error-box">❌ Speech recognition service error: {e}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        st.markdown(f'<div class="error-box">❌ An unexpected error occurred: {e}</div>', unsafe_allow_html=True)

# File upload input
else:
    st.markdown("---")
    st.markdown("### 📁 File Upload")
    
    # Instructions in a colorful box
    st.markdown("""
    <div class="info-box">
        <h4>📋 Instructions for File Upload:</h4>
        <ul>
            <li>📄 Supported formats: WAV, MP3</li>
            <li>🎯 For best results, use clear audio with minimal background noise</li>
            <li>📊 Keep files under 200MB for optimal performance</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "📤 Upload audio file (WAV or MP3)", 
        type=["wav", "mp3"],
        help="Select an audio file from your device"
    )
    
    if uploaded_file:
        # Display file info in colorful box
        st.markdown(f"""
        <div class="success-box">
            📄 File: {uploaded_file.name}<br>
            📊 Size: {uploaded_file.size} bytes
        </div>
        """, unsafe_allow_html=True)
        
        # Play audio file
        st.audio(uploaded_file, format="audio/wav")

        # Process the uploaded file
        try:
            ext = uploaded_file.name.split(".")[-1].lower()
            
            # Create temporary file
            with NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_audio:
                temp_audio.write(uploaded_file.read())
                temp_audio_path = temp_audio.name

            # Convert to WAV if MP3
            if ext == "mp3":
                st.markdown('<div class="info-box">🔄 Converting MP3 to WAV...</div>', unsafe_allow_html=True)
                audio = AudioSegment.from_mp3(temp_audio_path)
                wav_path = temp_audio_path.replace(".mp3", ".wav")
                audio.export(wav_path, format="wav")
            else:
                wav_path = temp_audio_path

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🎯 Transcribe and Translate", type="primary"):
                    with st.spinner("🔍 Transcribing audio..."):
                        text = transcribe_audio(wav_path)
                    
                    # Display transcribed text
                    st.markdown("### 📝 Transcribed Text:")
                    st.markdown(f"""
                    <div class="custom-container">
                        <h4 style="color: #2c3e50;">🎯 Original Text:</h4>
                        <p style="font-size: 1.2em; color: #34495e; font-weight: 500;">{text}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    if not text.startswith("Could not") and not text.startswith("Request error") and not text.startswith("An error"):
                        with st.spinner("🌐 Translating text..."):
                            translated = translate_text(text, target_language)
                        
                        # Display translated text
                        st.markdown("### 🌐 Translated Text:")
                        lang_names = {"en": "English", "hi": "Hindi", "mr": "Marathi"}
                        st.markdown(f"""
                        <div class="custom-container">
                            <h4 style="color: #2c3e50;">🌍 {lang_names[target_language]} Translation:</h4>
                            <p style="font-size: 1.2em; color: #34495e; font-weight: 500;">{translated}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Option to save the transcription
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button("💾 Save Transcription"):
                                transcript_data = f"File: {uploaded_file.name}\nOriginal: {text}\nTranslated ({target_language}): {translated}"
                                st.download_button(
                                    label="📄 Download Transcript",
                                    data=transcript_data,
                                    file_name=f"transcript_{uploaded_file.name}_{int(time.time())}.txt",
                                    mime="text/plain"
                                )

            # Clean up temporary files
            try:
                os.unlink(temp_audio_path)
                if ext == "mp3" and os.path.exists(wav_path):
                    os.unlink(wav_path)
            except:
                pass
                
        except Exception as e:
            st.markdown(f'<div class="error-box">❌ Error processing file: {e}</div>', unsafe_allow_html=True)

# Sidebar with troubleshooting tips
with st.sidebar:
    st.markdown("### 🔧 Troubleshooting Guide")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: #2c3e50;">🎤 Microphone Issues:</h4>
        <ul style="color: #34495e;">
            <li>✅ Check browser permissions</li>
            <li>🧪 Test microphone in other apps</li>
            <li>🌐 Use Chrome/Firefox for best results</li>
            <li>🔇 Avoid background noise</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: #2c3e50;">📁 File Upload Issues:</h4>
        <ul style="color: #34495e;">
            <li>📄 Use WAV/MP3 formats only</li>
            <li>📊 Keep files under 200MB</li>
            <li>🎵 Ensure clear audio quality</li>
            <li>🔊 Check audio file integrity</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: #2c3e50;">🎯 Recognition Issues:</h4>
        <ul style="color: #34495e;">
            <li>🗣️ Speak clearly and slowly</li>
            <li>📢 Use standard pronunciation</li>
            <li>⏱️ Avoid very short phrases</li>
            <li>🌐 Check internet connection</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
