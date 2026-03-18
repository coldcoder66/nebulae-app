from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty

# import sys
# sys.path.append("../utils")

from utils.agent import AzureAuthenticationError, NebulaeAgentService

class AssistantScreen(Screen):
    conversation_history = StringProperty("")
    is_request_in_progress = BooleanProperty(False)
    status_text = StringProperty("Sign in to Azure to chat with Nebulae.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation = []
        self._agent_service = NebulaeAgentService()

    def send_message(self, user_input):
        message = user_input.strip()
        if not message or self.is_request_in_progress:
            return

        self.conversation.append({"role": "user", "content": message})
        self.update_conversation_history()
        self.is_request_in_progress = True
        self.status_text = "Nebulae is thinking..."

        Clock.schedule_once(lambda _: self._request_agent_response(), 0)

    def _request_agent_response(self):
        from threading import Thread

        conversation_snapshot = [dict(message) for message in self.conversation]
        worker = Thread(
            target=self._run_agent_request,
            args=(conversation_snapshot,),
            daemon=True,
        )
        worker.start()

    def _run_agent_request(self, conversation_snapshot):
        try:
            response_text = self._agent_service.ask(conversation_snapshot)
            Clock.schedule_once(
                lambda _: self._finish_request(response_text=response_text),
                0,
            )
        except AzureAuthenticationError as exc:
            Clock.schedule_once(
                lambda _: self._finish_request(error_message=str(exc)),
                0,
            )
        except Exception as exc:
            Clock.schedule_once(
                lambda _: self._finish_request(
                    error_message=f"Nebulae could not complete the request: {exc}"
                ),
                0,
            )

    def _finish_request(self, response_text=None, error_message=None):
        if response_text:
            self.conversation.append({"role": "assistant", "content": response_text})
            self.status_text = "Connected to Azure AI Foundry."
        elif error_message:
            self.conversation.append({"role": "assistant", "content": error_message})
            self.status_text = "Azure authentication failed." if isinstance(error_message, str) and error_message.startswith("Azure authentication failed") else "Nebulae request failed."

        self.is_request_in_progress = False
        self.update_conversation_history()

    def update_conversation_history(self):
        self.conversation_history = "\n".join([
            f"User: {msg['content']}" if msg['role'] == "user" else f"Assistant: {msg['content']}"
            for msg in self.conversation
        ])