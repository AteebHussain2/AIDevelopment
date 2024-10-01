# conda activate "D:\TanDoori Data\Development\AI Develpoment\Llama 3 ChatBot x Chats\llama3ChatBotxChats"

import os
import json
import streamlit as st
from groq import Groq

# Streamlit page configuration
st.set_page_config(
    page_title="LLAMA 3.1 ChatBot × Chats",
    page_icon="🦙",
    layout="wide"  # Use wide layout for sidebars
)

working_dir = os.path.dirname(os.path.abspath(__file__))
config_data = json.load(open(f"{working_dir}/config.json"))
GROQ_API_KEY = config_data["GROQ_API_KEY"]
os.environ["GROQ_API_KEY"] = GROQ_API_KEY
client = Groq()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
if "title_generated" not in st.session_state:
    st.session_state.title_generated = False

st.title("🦙 LLAMA 3.1 ChatBot")

# Sidebar for conversation list
st.sidebar.title("Conversations")

# Button to create a new conversation
if st.sidebar.button("Start Conversation"):
    new_conversation_title = "New Untitled Conversation"
    st.session_state.conversations[new_conversation_title] = []
    st.session_state.chat_history = st.session_state.conversations[new_conversation_title]
    st.session_state.title_generated = False  # Reset title_generated flag

# Update the sidebar conversation list
for conversation_title, history in st.session_state.conversations.items():
    if st.sidebar.button(f"{conversation_title}", key=conversation_title):
        st.session_state.chat_history = history

# Generate title for conversation
def generate_title(chat_history):
    conversation_title = "New Untitled Conversation" if not st.session_state.chat_history else list(st.session_state.conversations.keys())[-1]
    messages = [
        {"role": "system", "content": f"You are a title generator. You have given a chat history of a conversation and you have to generate a title for the conversation based on the rules: 1. Title Should precise and less than 100 characters. / 2. Title should be based on chat history. / 3. Title should describe whole chat history. / 4. You will just give one title. / 5. You are supposed to give the title, so don't generate anything else like: 'Based on the chat history, I would suggest the following title'. / 6. Don't write anything like .txt or .md / 9. You can only use AlphaNumeric characters. / 8. Chat history is given as <history>{chat_history}</history>"},
    ]
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=messages
    )
    title = response.choices[0].message.content.strip()
    # Rename the file
    os.rename(f"{conversation_title}.txt", f"{title}.txt")
    # Update the conversation title in the sidebar
    st.session_state.conversations[title] = st.session_state.chat_history
    st.session_state.conversations.pop(conversation_title)
    # st.session_state.chat_history = []
    st.session_state.title_generated = True

# Main chat area
st.markdown("## Chat")
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message['content'])

# Input field for user message
user_prompt = st.chat_input("Ask LLAMA 3.1")
if user_prompt:
    st.chat_message("user").markdown(user_prompt)
    st.session_state.chat_history.append({"role":"user","content": user_prompt})

    # Get the current filename
    conversation_title = "New Untitled Conversation" if not st.session_state.chat_history else list(st.session_state.conversations.keys())[-1]

    # Save chat history to file
    with open(f"{conversation_title}.txt", "w") as f:
        for message in st.session_state.chat_history:
            f.write(f"{message['role']}: {message['content']}\n")

    messages =[ 
        {"role": "system", "content": "You are an AI Assistant who can answer all the questiosn of the user. but you have to keep in mind some rules while questions. 1. Be friendly, Calm, don't be frustrated with multiple questions. 2. Don't Harass someone, use simple language, do not abuse etc. 3. Provide answer from a - z with links to external articles if any. 4. If you don't know about anything, just give it a nice try and if you are at your limit simply say why you are not able proceed the user request."},
        *st.session_state.chat_history 
    ]
    response = client.chat.completions.create(
        model = "llama-3.1-8b-instant",
        messages=messages
    )
    assistant_response = response.choices[0].message.content
    st.session_state.chat_history.append({"role":"assistant","content": assistant_response})

    # Display the response
    with st.chat_message("assistant"):
        st.markdown(assistant_response)

    # Generate title after 2000 characters
    if len("".join([message['content'] for message in st.session_state.chat_history])) > 2000 and not st.session_state.title_generated:
        with open(f"{conversation_title}.txt", "r") as f:
            chat_history = f.read()
        generate_title(chat_history)
