import os
from pathlib import Path
import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Configure Google API
api_key = st.secrets["API_KEY"]["GOOGLE_API_KEY"]
genai.configure(api_key=api_key)

# Initialize Gemini Pro model
model = genai.GenerativeModel('gemini-pro')

# Function to load FAQ from a text file
@st.cache_data
def load_faq(file_path):
    faq = {}
    with open(file_path, 'r') as f:
        content = f.read().split('\n\n')
    for item in content:
        if '?' in item:
            question, answer = item.split('\n', 1)
            faq[question.strip()] = answer.strip()
    return faq

# Function to format FAQ for display
def format_faq_for_display(faq):
    formatted_faq = ""
    for question, answer in faq.items():
        formatted_faq += f"**Q: {question}**\n\n{answer}\n\n---\n\n"
    return formatted_faq

# Function to generate response using Gemini Pro
def generate_response(query, context):
    prompt = f"""
    Context: {context}

    Human: {query}

    Assistant: Analyze the human's input and respond accordingly:
    1. If it's a question that cannot be answered based on the given context, respond exactly with: 'cannot response'
    2. If it's a greeting (e.g., "Hi", "Hello"), respond with: "Hello! How may I help you today?"
    3. If it's a short affirmation or acknowledgment (e.g., "Nice", "Okay", "Thanks"), respond with: "I'm glad I could assist you. Is there anything else you'd like to know?"
    4. If it's a question that can be answered based on the context, provide a concise and relevant answer.
    5. If it's any other respose then answer with: "I'm here to help. What would you like to know?"
    """
    
    response = model.generate_content(prompt)
    return response.text

# Function to answer questions
def answer_question(user_query, faq):
    # Combine all FAQ content for context
    context = "\n".join([f"Q: {q}\nA: {a}" for q, a in faq.items()])
    
    # Generate response using Gemini Pro
    answer = generate_response(user_query, context)
    
    if "don't have enough information" in answer.lower():
        return None
    return answer

# WhatsApp fallback function
def whatsapp_fallback(query):
    whatsapp_link = "https://wa.link/m8ghvf"  # Replace with your actual WhatsApp Link
    return f"I not able to answer your question: '{query}'. Please contact our support via WhatsApp link: {whatsapp_link}."

# Streamlit app
def main():
    st.title("FAQ Chatbot")

    # Load FAQ
    faq_path = Path('data/FAQ.txt')
    if not faq_path.exists():
        st.error(f"Error: FAQ file not found at {faq_path}. Please make sure the file exists.")
        return

    faq = load_faq(faq_path)

    # Display FAQ in sidebar
    st.sidebar.title("Frequently Asked Questions")
    formatted_faq = format_faq_for_display(faq)
    st.sidebar.markdown(formatted_faq)

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("What is your question?"):
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        response = answer_question(prompt, faq)
        
        if response != "cannot response":
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
        else:
            fallback_message = whatsapp_fallback(prompt)
            # Display fallback message in chat message container
            with st.chat_message("assistant"):
                st.markdown(fallback_message)
            # Add fallback message to chat history
            st.session_state.messages.append({"role": "assistant", "content": fallback_message})

if __name__ == "__main__":
    main()