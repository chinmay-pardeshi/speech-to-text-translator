import streamlit as st
import speech_recognition as sr
from googletrans import Translator
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import os

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

def transcribe_audio(wav_path):
    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return "Could not understand the audio."
    except sr.RequestError as e:
        return f"Request error from Google Speech Recognition service: {e}"

def translate_text(text, lang_code):
    translator = Translator()
    return translator.translate(text, dest=lang_code).text

# Microphone input
if input_method == "🎤 Microphone":
    st.info("Click the button to start recording via microphone.")
    if st.button("Start Recording"):
        with sr.Microphone() as source:
            st.info("Listening... Speak now!")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
                st.success("Recording complete. Processing...")
                text = recognizer.recognize_google(audio)
                st.subheader("📝 Transcribed Text:")
                st.write(text)

                translated = translate_text(text, target_language)
                st.subheader("🌐 Translated Text:")
                st.write(translated)
            except sr.WaitTimeoutError:
                st.error("Listening timed out while waiting for phrase to start.")
            except sr.UnknownValueError:
                st.error("Could not understand the audio.")
            except Exception as e:
                st.error(f"An error occurred: {e}")

# File upload input
else:
    uploaded_file = st.file_uploader("Upload audio file (WAV or MP3)", type=["wav", "mp3"])
    if uploaded_file:
        st.audio(uploaded_file, format="audio/wav")

        ext = uploaded_file.name.split(".")[-1]
        temp_audio = NamedTemporaryFile(delete=False, suffix=f".{ext}")
        temp_audio.write(uploaded_file.read())
        temp_audio.close()

        # Convert to WAV if MP3
        if ext == "mp3":
            audio = AudioSegment.from_mp3(temp_audio.name)
            wav_path = temp_audio.name.replace(".mp3", ".wav")
            audio.export(wav_path, format="wav")
        else:
            wav_path = temp_audio.name

        if st.button("Transcribe and Translate"):
            text = transcribe_audio(wav_path)
            st.subheader("📝 Transcribed Text:")
            st.write(text)

            translated = translate_text(text, target_language)
            st.subheader("🌐 Translated Text:")
            st.write(translated)
