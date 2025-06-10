# 🎙️ Speech-to-Text & Translation App

This app allows you to **convert speech to text** and **translate it into multiple languages** using your **microphone** or an **uploaded audio file**. It’s built with Python, Streamlit, Google Speech Recognition API, and Google Translate.

---

## 🎥 Demo

![App Demo](https://github.com/chinmay-pardeshi/speech-to-text-translator/blob/main/Demo/speechtotext-gif.gif)


---

## 🚀 Features

- 🎤 Record audio directly from your **microphone**
- 📁 Upload **.wav** or **.mp3** audio files
- 📝 Converts speech to text using **Google Speech Recognition**
- 🌐 Translates transcribed text to:
  - English (`en`)
  - Hindi (`hi`)
  - Marathi (`mr`)
- 🔄 Automatic audio format handling (MP3 → WAV)

---

## 🛠️ Tech Stack

- Python
- [Streamlit](https://streamlit.io/)
- [speech_recognition](https://pypi.org/project/SpeechRecognition/)
- [googletrans](https://pypi.org/project/googletrans/)
- [pydub](https://pydub.com/) (for MP3 to WAV conversion)

---

## 💻 How to Run the App

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/speech-translate-app.git
cd speech-translate-app
````

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Streamlit app

```bash
streamlit run app.py
```

---

## 🌐 Supported Languages

| Code | Language |
| ---- | -------- |
| en   | English  |
| hi   | Hindi    |
| mr   | Marathi  |

```

---

