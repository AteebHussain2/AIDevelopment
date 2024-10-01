from groq import Groq
import discord
from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
BOT_KEY = os.getenv("BOT_KEY")
CHATME_ID = os.getenv("CHATME_ID")

groq_client = Groq(api_key=GROQ_API_KEY)

# Check if ChatME.txt exists, create it if it doesn't
if not os.path.exists('ChatME.txt'):
    open('ChatME.txt', 'w').close()

with open('ChatME.txt', 'r') as readChatHistory:
    ChatHistory = readChatHistory.read()

def writeChatHistory(message=None, response=None):
    try:
        with open('ChatME.txt', 'a') as writeChatHistory:
            if message:
                writeChatHistory.write(f"{message.author}: {message.content}\n")
            elif response:
                writeChatHistory.write(f"ChatME: {response}\n")
    except Exception as e:
        print(f"Error writing to ChatHistory: {str(e)}")

def BotResponse(user_prompt):
    messages = [
        {
            "role": "system",
            "content": f"{ChatHistory}",
        },
        {
            "role": "user",
            "content": user_prompt,
        }
    ]
    
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged on as {self.user}!")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.channel.id == int(CHATME_ID):
            channel = message.channel
            writeChatHistory(message=message)
            response = BotResponse(message.content)
            writeChatHistory(response=response)
            await channel.send(response)

if __name__ == "__main__":
    intents = discord.Intents.default()
    intents.message_content = True
    client = MyClient(intents=intents)
    client.run(BOT_KEY)