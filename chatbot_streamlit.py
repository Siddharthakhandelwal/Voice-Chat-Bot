import streamlit as st
import os
import google.generativeai as genai
import pyttsx3
import speech_recognition as sr
from streamlit_webrtc import webrtc_streamer, WebRtcMode

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response

def transcribe_audio(audio_data):
    recognizer = sr.Recognizer()
    try:
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "Sorry, I couldn't understand your speech."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

st.set_page_config(page_title="Q&A Demo")
st.header("CONVERSATIONAL Q&A CHATBOT USING GEMINI API \N{ROBOT FACE} \N{SPEECH BALLOON}")

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

submit = False
speech_input = st.checkbox("Use Speech Input")
if speech_input:
    webrtc_ctx = webrtc_streamer(key="speech-input", mode="sendonly", audio=True)
    if webrtc_ctx.video_processor:
        webrtc_ctx.video_processor.stop()
    if webrtc_ctx.audio_processor:
        audio_data = webrtc_ctx.audio_processor.get_frame()
        if audio_data:
            input = transcribe_audio(audio_data)
            submit = True
else:
    input = st.text_input("Input: ", key="input")
    submit = st.button("Ask the question")

if submit and input:
    response = get_gemini_response(input)
    st.session_state['chat_history'].append(("You", input))
    st.subheader("The Response is")
    response_text = ""
    for chunk in response:
        if hasattr(chunk, 'text'):
            response_text += chunk.text
            st.write(chunk.text)
        elif hasattr(chunk, 'value'):
            response_text += chunk.value
            st.write(chunk.value)
        else:
            st.warning("Invalid response format")
    st.session_state['chat_history'].append(("Bot", response_text))

    # Speak the response if it exists
    if response_text:
        engine = pyttsx3.init()
        engine.say(response_text)
        engine.runAndWait()

st.subheader("The Chat History is")
for role, text in st.session_state['chat_history']:
    st.write(f"{role}: {text}")

st.markdown(""" <div style='text-align: center; font-size: 25px;'> Developed with \N{YELLOW HEART}, using <span style='color: cyan; font-weight: 500'>Gemini</span> and <span style='color: cyan; font-weight: 500'>Streamlit</span> </div> """, unsafe_allow_html=True)
