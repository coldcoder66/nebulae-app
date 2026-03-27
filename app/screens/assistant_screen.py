from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.graphics import Color, RoundedRectangle
import re

from utils.agent import AzureAuthenticationError, NebulaeAgentService

def markdown_to_kivy_markup(text):
    """Convert markdown formatting to Kivy markup."""
    # Escape existing square brackets to prevent conflicts
    text = text.replace('[', '&bl;').replace(']', '&br;')
    
    # Bold: **text** or __text__
    text = re.sub(r'\*\*(.+?)\*\*', r'[b]\1[/b]', text)
    text = re.sub(r'__(.+?)__', r'[b]\1[/b]', text)
    
    # Italic: *text* or _text_ (but not already processed bold)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'[i]\1[/i]', text)
    text = re.sub(r'(?<!_)_(?!_)(.+?)(?<!_)_(?!_)', r'[i]\1[/i]', text)
    
    # Inline code: `text`
    text = re.sub(r'`(.+?)`', r'[color=d63031][font=RobotoMono-Regular]\1[/font][/color]', text)
    
    # Headers: # text -> larger, bold
    text = re.sub(r'^### (.+)$', r'[size=28][b]\1[/b][/size]', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'[size=32][b]\1[/b][/size]', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'[size=36][b]\1[/b][/size]', text, flags=re.MULTILINE)
    
    return text

class AssistantScreen(Screen):
    is_request_in_progress = BooleanProperty(False)
    status_text = StringProperty("Chat with Ranae.")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conversation = []
        self._agent_service = NebulaeAgentService()

    def send_message(self, user_input):
        message = user_input.strip()
        if not message or self.is_request_in_progress:
            return

        self.conversation.append({"role": "user", "content": message})
        self.add_message("user", message)
        self.is_request_in_progress = True
        self.status_text = "Ranae is thinking..."

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
            self.add_message("assistant", response_text)
            self.status_text = "Connected to Ranae."
        elif error_message:
            self.conversation.append({"role": "assistant", "content": error_message})
            self.add_message("assistant", error_message)
            self.status_text = "Azure authentication failed." if isinstance(error_message, str) and error_message.startswith("Azure authentication failed") else "Nebulae request failed."

        self.is_request_in_progress = False

    def add_message(self, role, content):
        """Add a message bubble to the chat interface."""
        messages_container = self.ids.messages_container
        
        # Create outer box for alignment
        outer_box = BoxLayout(
            size_hint_y=None,
            height=0,  # Will be set after label is created
            padding=[0, 5, 0, 5]
        )
        
        # Create message bubble container
        bubble_box = BoxLayout(
            orientation='vertical',
            size_hint_x=0.7,  # Max 70% width
            size_hint_y=None,
            padding=[15, 10, 15, 10]
        )
        
        # Position based on role
        if role == "user":
            outer_box.pos_hint = {"right": 1}
            bubble_box.pos_hint = {"right": 1}
            bg_color = (0.117647, 0.239215, 0.345098, 1)  # Dark blue
            text_color = (1, 1, 1, 1)  # White text
            text_align = "right"
        else:
            outer_box.pos_hint = {"left": 0}
            bubble_box.pos_hint = {"left": 0}
            bg_color = (0.9, 0.9, 0.92, 1)  # Light gray
            text_color = (0.117647, 0.239215, 0.345098, 1)  # Dark blue text
            text_align = "left"
        
        # Create label with markup
        formatted_content = markdown_to_kivy_markup(content)
        label = Label(
            text=formatted_content,
            markup=True,
            size_hint_y=None,
            text_size=(self.width * 0.5, None),  # 50% of screen width for wrapping
            color=text_color,
            font_name="DroplineRegular",
            font_size="20sp",
            valign="top",
            halign=text_align
        )
        
        # Bind to update text_size when container width changes
        def update_text_size(instance, value):
            label.text_size = (instance.width * 0.5, None)
            label.texture_update()
            label.height = label.texture_size[1] + 20
            bubble_box.height = label.height + 20
            outer_box.height = bubble_box.height + 10
        
        # Bind uses Kivy's event system (type checker may not recognize)
        self.bind(width=update_text_size)  # type: ignore
        
        # Initial height calculation
        label.texture_update()
        label.height = label.texture_size[1] + 20
        bubble_box.height = label.height + 20
        outer_box.height = bubble_box.height + 10
        
        # Draw bubble background
        with bubble_box.canvas.before:  # type: ignore
            Color(*bg_color)
            bg_rect = RoundedRectangle(
                pos=bubble_box.pos,
                size=bubble_box.size,
                radius=[15]
            )
        
        # Update background when bubble moves or resizes
        def update_bg(instance, value):
            bg_rect.pos = instance.pos
            bg_rect.size = instance.size
        
        bubble_box.bind(pos=update_bg, size=update_bg)  # type: ignore
        
        bubble_box.add_widget(label)
        outer_box.add_widget(bubble_box)
        messages_container.add_widget(outer_box)
        
        # Scroll to bottom
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)
    
    def _scroll_to_bottom(self):
        """Scroll the messages view to the bottom."""
        scrollview = self.ids.messages_scrollview
        scrollview.scroll_y = 0

    def start_new_chat(self):
        """Clear the current conversation and reset the chat interface."""
        self.conversation.clear()
        self.ids.messages_container.clear_widgets()
        self.status_text = "Chat with Ranae."
        self.is_request_in_progress = False