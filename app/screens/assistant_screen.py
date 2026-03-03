from kivy.uix.screenmanager import Screen
import openai
from kivy.properties import StringProperty
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("API_KEY")  # Load API key from .env file

class AssistantScreen(Screen):
    conversation_history = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation = []  # To store the conversation history

    def send_message(self, user_input):
        # Append user input to conversation
        self.conversation.append({"role": "user", "content": user_input})
        
        # Call OpenAI API to get a response
        response = self.get_ai_response(user_input)

        # Append AI response to conversation
        self.conversation.append({"role": "assistant", "content": response})

        # Update the conversation history
        self.update_conversation_history()

    def get_ai_response(self, user_input):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Use the latest model
                messages=self.conversation
            )
            return response['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"Error: {str(e)}"

    def update_conversation_history(self):
        # Format the conversation history for display
        self.conversation_history = "\n".join([
            f"User: {msg['content']}" if msg['role'] == "user" else f"Assistant: {msg['content']}"
            for msg in self.conversation
        ])