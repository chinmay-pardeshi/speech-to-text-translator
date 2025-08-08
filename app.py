import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import os
import io
import time

st.title("🎙️ Speech to Text & Translation App")
st.write("Choose an input method: record via microphone or upload an audio file. Transcribe the audio and translate it to a selected language.")

# Language selector
target_language = st.selectbox(
    "Select Output Language",
    ["en", "hi", "mr"],
    format_func=lambda x: {"en": "English", "hi": "Hindi", "mr": "Marathi"}[x]
)

# Input method choice
input_method = st.radio("Choose Input Method:", ["🎤 Microphone", "📁 Upload Audio File"])

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
            st.info("🎤 Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            st.info("🎤 Listening... Speak now! (You have 15 seconds)")
            
            # Use longer timeout and phrase time limit
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=15)
            return audio
    except sr.WaitTimeoutError:
        st.error("⏰ Listening timed out. No speech detected. Please try again.")
        return None
    except Exception as e:
        st.error(f"❌ Microphone error: {e}")
        st.info("💡 Try these solutions:")
        st.info("• Check if your microphone is connected and working")
        st.info("• Grant microphone permissions to your browser")
        st.info("• Try refreshing the page")
        return None

# Microphone input
if input_method == "🎤 Microphone":
    st.info("📋 **Instructions for Microphone Recording:**")
    st.info("• Make sure your microphone is connected and working")
    st.info("• Grant microphone permissions when prompted by your browser")
    st.info("• Speak clearly and avoid background noise")
    st.info("• You'll have 15 seconds to speak after clicking the button")
    
    if st.button("🎤 Start Recording", type="primary"):
        with st.spinner("Setting up microphone..."):
            audio = record_audio_with_microphone()
        
        if audio is not None:
            with st.spinner("Processing audio..."):
                try:
                    # Transcribe directly from audio object
                    text = recognizer.recognize_google(audio)
                    
                    if text:
                        st.success("✅ Recording processed successfully!")
                        st.subheader("📝 Transcribed Text:")
                        st.write(f"**Original:** {text}")

                        # Translate the text
                        with st.spinner("Translating..."):
                            translated = translate_text(text, target_language)
                        
                        st.subheader("🌐 Translated Text:")
                        st.write(f"**{target_language.upper()}:** {translated}")
                        
                        # Option to save the transcription
                        if st.button("💾 Save Transcription"):
                            transcript_data = f"Original: {text}\nTranslated ({target_language}): {translated}"
                            st.download_button(
                                label="📄 Download Transcript",
                                data=transcript_data,
                                file_name=f"transcript_{int(time.time())}.txt",
                                mime="text/plain"
                            )
                    
                except sr.UnknownValueError:
                    st.error("❌ Could not understand the audio. Please try again with clearer speech.")
                except sr.RequestError as e:
                    st.error(f"❌ Speech recognition service error: {e}")
                except Exception as e:
                    st.error(f"❌ An unexpected error occurred: {e}")

# File upload input
else:
    st.info("📋 **Instructions for File Upload:**")
    st.info("• Supported formats: WAV, MP3")
    st.info("• For best results, use clear audio with minimal background noise")
    
    uploaded_file = st.file_uploader(
        "Upload audio file (WAV or MP3)", 
        type=["wav", "mp3"],
        help="Select an audio file from your device"
    )
    
    if uploaded_file:
        # Display file info
        st.info(f"📄 File: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
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
                st.info("🔄 Converting MP3 to WAV...")
                audio = AudioSegment.from_mp3(temp_audio_path)
                wav_path = temp_audio_path.replace(".mp3", ".wav")
                audio.export(wav_path, format="wav")
            else:
                wav_path = temp_audio_path

            if st.button("🎯 Transcribe and Translate", type="primary"):
                with st.spinner("Transcribing audio..."):
                    text = transcribe_audio(wav_path)
                
                st.subheader("📝 Transcribed Text:")
                st.write(f"**Original:** {text}")

                if not text.startswith("Could not") and not text.startswith("Request error") and not text.startswith("An error"):
                    with st.spinner("Translating text..."):
                        translated = translate_text(text, target_language)
                    
                    st.subheader("🌐 Translated Text:")
                    st.write(f"**{target_language.upper()}:** {translated}")
                    
                    # Option to save the transcription
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
            st.error(f"❌ Error processing file: {e}")

# Sidebar with troubleshooting tips
with st.sidebar:
    st.header("🔧 Troubleshooting")
    st.write("**Microphone Issues:**")
    st.write("• Check browser permissions")
    st.write("• Test microphone in other apps")
    st.write("• Use Chrome/Firefox for best results")
    st.write("• Avoid background noise")
    
    st.write("**File Upload Issues:**")
    st.write("• Use WAV/MP3 formats only")
    st.write("• Keep files under 200MB")
    st.write("• Ensure clear audio quality")
    
    st.write("**Recognition Issues:**")
    st.write("• Speak clearly and slowly")
    st.write("• Use standard pronunciation")
    st.write("• Avoid very short phrases")
    st.write("• Check internet connection")
