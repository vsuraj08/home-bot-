

import streamlit as st
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
from gtts import gTTS
import os
import base64
import tempfile
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def main():
    st.title("🎤 Home Security Chatbot 💬🤖")
    st.subheader('Record your voice and get a response from the AI Home Security Assistant')

    st.sidebar.header("About Home Security Chatbot")
    st.sidebar.write(f'''This is a home security chatbot that takes voice input and provides responses related to home security.''')

    st.sidebar.info(f'''Development process includes these steps.  
    1️⃣ Convert Voice into text using Google's speech recognition API.  
    2️⃣ Feed the text into a language model (e.g., Gemini) to generate a response.
    3️⃣ Convert the response text into speech using Google TTS API.  
    And boom, 🚀 ''')

    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space
    st.sidebar.write("")  # Adds one line of space

    st.sidebar.write("Developed by [Your Name]")

    security_recorder = audio_recorder(text='Speak', icon_size="2x", icon_name="microphone-lines", key="security_recorder")

    if security_recorder is not None:
        
        with st.container():
            col1, col2 = st.columns(2)

            with col2:
                # Display the audio file
                st.header('🔊')                                                                                                                                                                                                                                                                                                                                                                                                                                                          
                st.audio(security_recorder)

                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_security_recording:
                    temp_security_recording.write(security_recorder)
                    temp_security_recording_path = temp_security_recording.name
                
                # Convert audio file to text
                text = audio_to_text(temp_security_recording_path)
                st.success(text)

                # Remove the temporary file
                os.remove(temp_security_recording_path)

        response_text = security_model_response(text)

        with st.container():
            col1, col2 = st.columns(2)

            with col1:
                # Convert the response text to speech
                response_audio_html = response_to_audio(response_text)

                st.header('🤖')
                st.markdown(response_audio_html, unsafe_allow_html=True)

                # Display the updated response text below the audio
                st.info(response_text)

def audio_to_text(temp_security_recording_path):
    # Speech Recognition
    recognizer = sr.Recognizer()
    with sr.AudioFile(temp_security_recording_path) as source:
        security_recorded_voice = recognizer.record(source)
        try:
            text = recognizer.recognize_google(security_recorded_voice, language="en")
            return text
        except sr.UnknownValueError:
            return "Sorry, I couldn't understand your voice."
        except sr.RequestError:
            return "Sorry, my speech service is down."

def response_to_audio(text, lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts_audio_path = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False).name
    tts.save(tts_audio_path)

    # Get the base64 string of the audio file
    audio_base64 = get_audio_base64(tts_audio_path)

    # Autoplay audio using HTML and JavaScript
    audio_html = f"""
    <audio controls autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        Your browser does not support the audio element.
    </audio>
    """
    return audio_html

# Function to encode the audio file to base64
def get_audio_base64(file_path):
    with open(file_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    return base64.b64encode(audio_bytes).decode()

def security_model_response(text):
    prompt = f"""You are a home security assistant. Answer the question based on general home security knowledge. 
    Keep your response brief and informative. If you don't understand the question, respond with 'I did not understand the question, please try again.' 
    Question: {text}"""

    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    )

    chat_session = model.start_chat()
    response = chat_session.send_message(prompt)

    return response.text

if __name__ == "__main__":
    main()
