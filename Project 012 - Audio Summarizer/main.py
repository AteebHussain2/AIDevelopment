# conda activate "D:\TanDoori Data\DataBase\Projects\AIDevelopment\Project 012 - Audio Summarizer\voiceSummarizer"

import streamlit as st
import os
import google.generativeai as genai
import tempfile
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

def convert_audio_to_wav(audio_file_path):
    audio = AudioSegment.from_file(audio_file_path)
    wav_file_path = audio_file_path.replace('.mp3', '.wav')
    audio.export(wav_file_path, format='wav')
    return wav_file_path

def transcribe_audio(audio_file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    return text

def summarize_text(text):
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-001")
    response = model.generate_content(
        [
            "Please summarize the following text. Provide the summary in markdown only.",
            text
        ]
    )
    if hasattr(response, 'text'):
        return response.text
    else:
        return "Error: Unable to summarize text."

def save_uploaded_file(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix="." + uploaded_file.name.split('.')[-1]) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            return temp_file.name
    except Exception as e:
        st.error(f"Error Handling uploaded file: {e}")
        return None

# Streamlit interface
st.title("Audio Summarization App")

with st.expander("About this app"):
    st.write("""
This app uses Gemini model to summarize audio files.
Upload your audio file in WAV and MP3 format and get a concise summary of its content.
""")

audio_file = st.file_uploader("Upload Audio File", type=['wav', 'mp3'])
if audio_file is not None:
    audio_path = save_uploaded_file(audio_file)
    st.audio(audio_path)

    # if not audio_path.endswith('.wav'):
    #     audio_path = convert_audio_to_wav(audio_path)

if st.button("Summarize Audio"):
    if not audio_path.endswith('.wav'):
        audio_path = convert_audio_to_wav(audio_path)
    with st.spinner("Transcribing audio..."):
        transcribed_text = transcribe_audio(audio_path)
    with st.spinner("Summarizing..."):
        summary_text = summarize_text(transcribed_text)
        st.markdown(summary_text)