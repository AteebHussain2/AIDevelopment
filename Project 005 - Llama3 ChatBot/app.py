# conda activate "D:\TanDoori Data\Development\AI Develpoment\Gemini API Key Projects\Llama 3 ChatBot\llama3chatbot"

import os
import json
import streamlit as st
from groq import Groq

#streamlit page configuration

st.set_page_config(
    page_title="LLAMA 3.1 ChatBot",
    page_icon="🦙",
    layout="centered"
)

working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))

GROQ_API_KEY = config_data["GROQ_API_KEY"]

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

client = Groq()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🦙 LLAMA 3.1 ChatBot")

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message['content'])

# input field for user message

user_prompt = st.chat_input("Ask LLAMA 3.1")

if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role":"user","content": user_prompt})

    messages =[
        {"role": "system", "content": "You are a Generative AI engineer who can answer all the questions related to generative AI but apart from that you know nothing"},
        *st.session_state.chat_history
    ]

    response = client.chat.completions.create(
        model = "llama-3.1-8b-instant",
        messages=messages
    )
    assistant_response = response.choices[0].message.content
    st.session_state.chat_history.append({"role":"assistant","content": assistant_response})

    # display the response

    with st.chat_message("assistant"):
        st.markdown(assistant_response)