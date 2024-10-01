import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from storyGenerator import StoryGenerator
from recipeGenerator import RecipeGenerator
from PIL import Image
import datetime
from webSearcher import WebSearcher
from blogWriter import BlogWriter
from newsLetter import NewsLetter

load_dotenv()

# Streamlit page configuration
logo = Image.open('chatbot.png')
add = Image.open('add.png')
st.set_page_config(
    page_title="Aapka ChatBot",
    page_icon=logo,
    layout="wide"  # Use wide layout for sidebars
)

class ChatBot:
    def __init__(self):
        self.working_dir = os.path.dirname(os.path.abspath(__file__))
        os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
        self.client = Groq()

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        if "conversations" not in st.session_state:
            st.session_state.conversations = {}
        if "title_generated" not in st.session_state:
            st.session_state.title_generated = False
        if "current_conversation" not in st.session_state:
            st.session_state.current_conversation = "New Chat"

        # Sidebar for conversation list
        st.sidebar.title("Aapka Chatbot")

        # Button to create a new conversation
        if st.sidebar.button("Chat"):
            new_conversation_title = "New Chat"
            st.session_state.conversations[new_conversation_title] = []
            st.session_state.chat_history = st.session_state.conversations[new_conversation_title]
            st.session_state.current_conversation = new_conversation_title
            st.session_state.title_generated = False  # Reset title_generated flag

        # Update the sidebar conversation list
        for conversation_title, history in st.session_state.conversations.items():
            if st.sidebar.button(f"{conversation_title}", key=conversation_title):
                st.session_state.chat_history = history
                st.session_state.current_conversation = conversation_title

    def generate_title(self, chat_history):
        conversation_title = st.session_state.current_conversation
        messages = [
            {"role": "system", "content": f"You are a title generator. You have given a chat history of a conversation and you have to generate a title for the conversation based on the rules: 1. Title Should precise and less than 100 characters. / 2. Title should be based on chat history. / 3. Title should describe whole chat history. / 4. You will just give one title. / 5. You are supposed to give the title, so don't generate anything else like: 'Based on the chat history, I would suggest the following title'. / 6. Don't write anything like .txt or .md / 9. You can only use AlphaNumeric characters. / 8. Chat history is given as <history>{chat_history}</history>"},
        ]
        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=messages
        )
        title = response.choices[0].message.content.strip()
        # Rename the file
        os.rename(f"{self.working_dir}/history/{conversation_title}.md", f"{self.working_dir}/history/{title}.md")
        # Update the conversation title in the sidebar
        st.session_state.conversations[title] = st.session_state.chat_history
        st.session_state.conversations.pop(conversation_title)
        st.session_state.current_conversation = title
        st.session_state.title_generated = True

    def generate_response(self, messages):
        response = self.client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=messages
        )
        return response.choices[0].message.content

    def handle_user_input(self, user_prompt):
        # Get the current filename
        conversation_title = st.session_state.current_conversation

        # Save chat history to file
        with open(f"{self.working_dir}/history/{conversation_title}.md", "w") as f:
            for message in st.session_state.chat_history:
                f.write(f"<{message['role']}>\n{message['content']}\n</{message['role']}>\n\n")

        messages = [
            {"role": "system", "content": "You are an AI Assistant: 'Aapka ChatBot' who can answer all the questions of the user. but you have to keep in mind some rules while answering questions. 1. Be friendly, Calm, don't be frustrated with multiple questions. 2. Don't Harass someone, use simple language, do not abuse etc. 3. Provide answer from a - z with links to external articles if any. 4. If you don't know about anything, just give it a nice try and if you are at your limit simply say why you are not able to proceed with the user request."},
            *st.session_state.chat_history
        ]
        assistant_response = self.generate_response(messages)
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
        with open(f"{self.working_dir}/history/{conversation_title}.md", "w") as f:
            for message in st.session_state.chat_history:
                f.write(f"<{message['role']}>\n{message['content']}\n</{message['role']}>\n\n")

        # Display the response
        with st.chat_message("assistant"):
            st.markdown(assistant_response)

    def main(self):
        # Main chat area
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message['content'])

        # Input field for user message
        user_prompt = st.chat_input("Ask Aapka ChatBot anything....")

        # Handle user input
        if user_prompt:
            st.chat_message("user").markdown(user_prompt)
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})

            conversation_title = st.session_state.current_conversation

            if "/story" in user_prompt.lower():
                with st.spinner('Generating Story...'):
                    user_prompt = user_prompt.replace("/story", "").strip()
                    story_generator = StoryGenerator(user_prompt)
                if story_generator:
                    st.chat_message("assistant").markdown(story_generator["content"])
                    st.session_state.chat_history.append({"role": "assistant", "content": story_generator["content"]})
                    with open(f"{self.working_dir}/history/{conversation_title}.md", "w") as f:
                        for message in st.session_state.chat_history:
                            f.write(f"<{message['role']}>\n{message['content']}\n</{message['role']}>\n\n")
                else:
                    st.error("Failed to generate story. Please try again.")

            elif "/recipe" in user_prompt.lower():
                with st.spinner('Generating Recipe...'):
                    user_prompt = user_prompt.replace("/recipe", "").strip()
                    recipe_generator = RecipeGenerator(user_prompt)
                if recipe_generator:
                    st.chat_message("assistant").markdown(recipe_generator["content"])
                    st.session_state.chat_history.append({"role": "assistant", "content": recipe_generator["content"]})

                    with open(f"{self.working_dir}/history/{conversation_title}.md", "w") as f:
                        for message in st.session_state.chat_history:
                            f.write(f"<{message['role']}>\n{message['content']}\n</{message['role']}>\n\n")
                else:
                    st.error("Failed to generate recipe. Please try again.")

            elif "/web" in user_prompt.lower():
                with st.spinner('Performing Web Search...'):
                    user_prompt = user_prompt.replace("/web", "").strip()
                    web_searcher = WebSearcher(user_prompt)
                if web_searcher:
                    st.chat_message("assistant").markdown(web_searcher)
                    st.session_state.chat_history.append({"role": "assistant", "content": web_searcher})
                    with open(f"{self.working_dir}/history/{conversation_title}.md", "w") as f:
                        for message in st.session_state.chat_history:
                            f.write(f"<{message['role']}>\n{message['content']}\n</{message['role']}>\n\n")
                else:
                    st.error("Failed to perform web search. Please try again.")

            elif "/blog" in user_prompt.lower():
                with st.spinner('Generating Blog...'):
                    user_prompt = user_prompt.replace("/blog", "").strip()
                    blog_writer = BlogWriter(user_prompt)
                if blog_writer:
                    st.chat_message("assistant").markdown(blog_writer["content"])
                    st.session_state.chat_history.append({"role": "assistant", "content": blog_writer["content"]})
                    with open(f"{self.working_dir}/history/{conversation_title}.md", "w") as f:
                        for message in st.session_state.chat_history:
                            f.write(f"<{message['role']}>\n{message['content']}\n</{message['role']}>\n\n")
                else:
                    st.error("Failed to generate blog. Please try again.")

            elif "/news" in user_prompt.lower():
                with st.spinner('Generating Newsletter...'):
                    user_prompt = user_prompt.replace("/news", "").strip()
                    newsletter_generator = NewsLetter(user_prompt)
                if newsletter_generator:
                    st.chat_message("assistant").markdown(newsletter_generator["content"])
                    st.session_state.chat_history.append({"role": "assistant", "content": newsletter_generator["content"]})
                    with open(f"{self.working_dir}/history/{conversation_title}.md", "w") as f:
                        for message in st.session_state.chat_history:
                            f.write(f"<{message['role']}>\n{message['content']}\n</{message['role']}>\n\n")
                else:
                    st.error("Failed to generate newsletter. Please try again.")

            else:
                with st.spinner("Generating Response..."):
                    self.handle_user_input(user_prompt)

        # Generate title after 2000 characters
        if len("".join([message['content'] for message in st.session_state.chat_history])) > 2000 and not st.session_state.title_generated:
            with open(f"{self.working_dir}/history/{conversation_title}.md", "r") as f:
                chat_history = f.read()
            self.generate_title(chat_history)

if __name__ == "__main__":
    if not os.path.exists("README.md"):
        with open("README.md", "w") as config_file:
            config_file.write("""
# Aapka ChatBot

This is a simple chatbot built using Streamlit and Groq. It allows you to have conversations with an AI assistant and save the chat history to a file.

## Features

1. **Conversation History**: The chat history is saved to a file for each conversation.
2. **Title Generation**: The title of the conversation is generated based on the chat history.
3. **User Input Handling**: The user input is handled and the response is generated by the AI assistant.
## Generators

### Story Generator
The Story Generator takes a user prompt and generates a story based on the input. It uses the `StoryGenerator` class to create the story.

### Recipe Generator
The Recipe Generator takes a user prompt and generates a recipe based on the input. It uses the `RecipeGenerator` class to create the recipe.

### Image Generator
The Image Generator takes a user prompt and generates an image based on the input. It uses the `ImageGenerator` class to create the image.

### Blog Writer
The Blog Writer takes a user prompt and generates a blog post based on the input. It uses the `BlogWriter` class to create the blog post.

### Web Searcher
The Web Searcher takes a user prompt and performs a web search based on the input. It uses the `WebSearcher` class to perform the search and return the results.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/aapka-chatbot.git
   ```
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
                              
## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```
2. Use the chatbot to have conversations with the AI assistant.
3. The chat history is saved to a file for each conversation.
4. The title of the conversation is generated based on the chat history.
                              
## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

""")
            if not os.path.exists("history"):
                os.makedirs("history")
            if not os.path.exists("data"):
                os.makedirs("data")
            if not os.path.exists("cache"):
                os.makedirs("cache")

    chatbot = ChatBot()
    chatbot.main()