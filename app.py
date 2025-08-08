import streamlit as st
import speech_recognition as sr
from deep_translator import GoogleTranslator
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import os
import io
import time

# Check if running in Streamlit Cloud environment
MICROPHONE_AVAILABLE = False  # Set to False for Streamlit Cloud deployment

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

# Show info about hosted environment
st.markdown("""
<div class="warning-box">
    ℹ️ <strong>Streamlit Cloud Version:</strong><br>
    This is optimized for file upload transcription and translation.<br>
    For the best experience with audio files, use WAV format when possible.
</div>
""", unsafe_allow_html=True)

# Create main container
with st.container():
    st.markdown('<div class="info-box">Upload an audio file to transcribe and translate it to your selected language.</div>', unsafe_allow_html=True)

# Language selector with colorful container
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    target_language = st.selectbox(
        "🌍 Select Output Language",
        ["en", "hi", "mr", "es", "fr", "de", "ja", "ko", "zh"],
        format_func=lambda x: {
            "en": "🇺🇸 English", 
            "hi": "🇮🇳 Hindi", 
            "mr": "🇮🇳 Marathi",
            "es": "🇪🇸 Spanish",
            "fr": "🇫🇷 French", 
            "de": "🇩🇪 German",
            "ja": "🇯🇵 Japanese",
            "ko": "🇰🇷 Korean",
            "zh": "🇨🇳 Chinese"
        }[x]
    )

# Initialize speech recognizer
@st.cache_resource
def get_recognizer():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8
    recognizer.phrase_threshold = 0.3
    return recognizer

recognizer = get_recognizer()

def transcribe_audio(wav_path):
    """Transcribe audio file to text"""
    try:
        with sr.AudioFile(wav_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "Could not understand the audio. Please try speaking more clearly or check audio quality."
    except sr.RequestError as e:
        return f"Request error from Google Speech Recognition service: {e}"
    except Exception as e:
        return f"An error occurred during transcription: {str(e)}"

def convert_audio_to_wav(temp_audio_path, ext):
    """Convert audio file to WAV format with better error handling"""
    try:
        wav_path = temp_audio_path.replace(f".{ext}", ".wav")
        
        # Load audio based on format
        if ext.lower() == "mp3":
            audio = AudioSegment.from_mp3(temp_audio_path)
        elif ext.lower() == "m4a":
            audio = AudioSegment.from_file(temp_audio_path, format="m4a")
        elif ext.lower() == "flac":
            audio = AudioSegment.from_file(temp_audio_path, format="flac")
        elif ext.lower() == "ogg":
            audio = AudioSegment.from_ogg(temp_audio_path)
        else:
            # Generic file reading for other formats
            audio = AudioSegment.from_file(temp_audio_path)
        
        # Convert to mono and normalize
        audio = audio.set_channels(1)  # Convert to mono
        audio = audio.set_frame_rate(16000)  # Standard sample rate for speech recognition
        
        # Export as WAV
        audio.export(wav_path, format="wav")
        return wav_path, None
        
    except Exception as e:
        error_msg = str(e)
        if "ffmpeg" in error_msg.lower() or "ffprobe" in error_msg.lower():
            return None, "Audio conversion failed. Please try uploading a WAV file directly."
        else:
            return None, f"Audio conversion failed: {error_msg}"

def translate_text(text, lang_code):
    """Translate text to target language"""
    try:
        # Skip translation if it's an error message
        if any(phrase in text for phrase in ["Could not", "Request error", "An error", "Audio conversion failed"]):
            return text
        
        # Map language codes for deep-translator
        lang_map = {
            "en": "english", 
            "hi": "hindi", 
            "mr": "marathi",
            "es": "spanish",
            "fr": "french", 
            "de": "german",
            "ja": "japanese",
            "ko": "korean",
            "zh": "chinese"
        }
        
        target_lang = lang_map.get(lang_code, "english")
        
        # Skip translation if already in target language
        if lang_code == "en":  # Assuming most input is in English
            return text
            
        translator = GoogleTranslator(source='auto', target=target_lang)
        result = translator.translate(text)
        return result if result else text
        
    except Exception as e:
        return f"Translation error: {str(e)}"

# File upload section
st.markdown("---")
st.markdown("### 📁 Audio File Upload & Processing")

# Instructions
st.markdown("""
<div class="info-box">
    <h4>📋 How to use this app:</h4>
    <ul>
        <li>📄 <strong>Supported formats:</strong> WAV, MP3, M4A, FLAC, OGG</li>
        <li>🎯 <strong>Best results:</strong> Clear audio, minimal background noise</li>
        <li>📊 <strong>File size:</strong> Keep under 200MB for optimal performance</li>
        <li>🎤 <strong>Audio quality:</strong> 16kHz sample rate recommended</li>
        <li>🌐 <strong>Languages:</strong> Supports multiple input and output languages</li>
    </ul>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📤 Choose an audio file to transcribe and translate", 
    type=["wav", "mp3", "m4a", "flac", "ogg"],
    help="Select a clear audio file with speech to transcribe"
)

if uploaded_file:
    # Display file information
    file_size_mb = uploaded_file.size / (1024 * 1024)
    st.markdown(f"""
    <div class="success-box">
        📄 <strong>File:</strong> {uploaded_file.name}<br>
        📊 <strong>Size:</strong> {file_size_mb:.2f} MB<br>
        🎵 <strong>Type:</strong> {uploaded_file.type}
    </div>
    """, unsafe_allow_html=True)
    
    # Audio player
    st.audio(uploaded_file, format=f"audio/{uploaded_file.name.split('.')[-1]}")

    # Process button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎯 Transcribe and Translate", type="primary", use_container_width=True):
            try:
                # Get file extension
                ext = uploaded_file.name.split(".")[-1].lower()
                
                # Create temporary file
                with NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_audio:
                    temp_audio.write(uploaded_file.read())
                    temp_audio_path = temp_audio.name

                # Convert to WAV if necessary
                if ext != "wav":
                    with st.spinner(f"🔄 Converting {ext.upper()} to WAV..."):
                        wav_path, error = convert_audio_to_wav(temp_audio_path, ext)
                        if error:
                            st.markdown(f'<div class="error-box">❌ {error}</div>', unsafe_allow_html=True)
                            # Clean up
                            try:
                                os.unlink(temp_audio_path)
                            except:
                                pass
                            st.stop()
                else:
                    wav_path = temp_audio_path

                # Transcribe audio
                with st.spinner("🔍 Transcribing audio... This may take a moment."):
                    text = transcribe_audio(wav_path)
                
                # Display results
                st.markdown("---")
                st.markdown("## 📝 Results")
                
                # Original transcription
                st.markdown("### 🎯 Transcribed Text:")
                st.markdown(f"""
                <div class="custom-container">
                    <h4 style="color: #2c3e50;">📝 Original Transcription:</h4>
                    <p style="font-size: 1.2em; color: #34495e; font-weight: 500; background: rgba(255,255,255,0.8); padding: 1rem; border-radius: 10px; color: #2c3e50;">{text}</p>
                </div>
                """, unsafe_allow_html=True)

                # Translation (if not an error)
                if not any(phrase in text for phrase in ["Could not", "Request error", "An error", "Audio conversion failed"]):
                    with st.spinner("🌐 Translating text..."):
                        translated = translate_text(text, target_language)
                    
                    st.markdown("### 🌐 Translated Text:")
                    lang_names = {
                        "en": "English", "hi": "Hindi", "mr": "Marathi",
                        "es": "Spanish", "fr": "French", "de": "German",
                        "ja": "Japanese", "ko": "Korean", "zh": "Chinese"
                    }
                    
                    st.markdown(f"""
                    <div class="custom-container">
                        <h4 style="color: #2c3e50;">🌍 {lang_names.get(target_language, 'Translation')}:</h4>
                        <p style="font-size: 1.2em; color: #34495e; font-weight: 500; background: rgba(255,255,255,0.8); padding: 1rem; border-radius: 10px; color: #2c3e50;">{translated}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Download option
                    st.markdown("### 💾 Save Results")
                    transcript_data = f"""Audio File: {uploaded_file.name}
File Size: {file_size_mb:.2f} MB
Processing Date: {time.strftime('%Y-%m-%d %H:%M:%S')}

ORIGINAL TRANSCRIPTION:
{text}

TRANSLATION ({lang_names.get(target_language, target_language.upper())}):
{translated}
"""
                    
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.download_button(
                            label="📄 Download Complete Transcript",
                            data=transcript_data,
                            file_name=f"transcript_{uploaded_file.name.split('.')[0]}_{int(time.time())}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

                # Clean up temporary files
                try:
                    os.unlink(temp_audio_path)
                    if wav_path != temp_audio_path and os.path.exists(wav_path):
                        os.unlink(wav_path)
                except:
                    pass
                    
            except Exception as e:
                st.markdown(f'<div class="error-box">❌ Unexpected error: {str(e)}</div>', unsafe_allow_html=True)
                # Clean up on error
                try:
                    if 'temp_audio_path' in locals():
                        os.unlink(temp_audio_path)
                    if 'wav_path' in locals() and wav_path != temp_audio_path:
                        os.unlink(wav_path)
                except:
                    pass

# Sidebar information
with st.sidebar:
    st.markdown("### 🔧 App Information")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: #2c3e50;">🎯 Features:</h4>
        <ul style="color: #34495e; margin: 0;">
            <li>✅ Audio transcription</li>
            <li>🌐 Multi-language translation</li>
            <li>📄 Multiple audio formats</li>
            <li>💾 Downloadable results</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); padding: 1rem; border-radius: 10px; margin: 1rem 0;">
        <h4 style="color: #2c3e50;">💡 Tips for Better Results:</h4>
        <ul style="color: #34495e; margin: 0;">
            <li>🎤 Use clear, high-quality audio</li>
            <li>🔇 Minimize background noise</li>
            <li>🗣️ Speak clearly and at normal pace</li>
            <li>📱 WAV format works best</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1rem; border-radius: 10px;">
        <h4>⚡ Powered By:</h4>
        <p style="margin: 0;">🎙️ Google Speech Recognition<br>🌐 Google Translate API<br>🎵 PyDub Audio Processing</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Usage statistics (mock)
    st.markdown("### 📊 Session Info")
    if 'transcription_count' not in st.session_state:
        st.session_state.transcription_count = 0
    
    st.metric("Files Processed", st.session_state.transcription_count)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: rgba(255,255,255,0.7);'>"
    "🎙️ Speech to Text & Translation App | Built with Streamlit"
    "</div>", 
    unsafe_allow_html=True
)
