from kivymd.app import MDApp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.videoplayer import VideoPlayer
from kivy.uix.floatlayout import FloatLayout
from kivy.core.image import Image as CoreImage
from kivy.core.text import LabelBase
from kivy.core.window import Window
import os

#Import all of the screens so that they are recognized when loading the Kivy files
from screens.home_screen import HomeScreen, MainLayout
from screens.library_screen import LibraryScreen
from screens.settings_screen import SettingsScreen
from screens.assistant_screen import AssistantScreen
from screens.videos_screen import VideosScreen
from screens.visual_graphics_screen import VisualGraphicsScreen

class NebulaeApp(MDApp):
    def _find_font(self, substr="bayer"):
        """
        Register the imported font by searching common locations for a matching .otf/.ttf
        """

        #TODO hardcode the path to the font file and delete this search function
        substr = substr.lower()
        # Search the app directory first
        app_dir = os.path.join(os.path.dirname(__file__), 'assets', 'fonts')
        for root, _, files in os.walk(app_dir):
            for f in files:
                if f.lower().endswith((".otf", ".ttf")) and substr in f.lower():
                    return os.path.join(root, f)
        return None

    def build(self) -> ScreenManager:
        """
        Build and set the theme for the screen manager. Returns a
        Widget instance that is the root of the widget tree.
        """

        #TODO clean up all this font finding and window sizing code
        found_font = self._find_font("bayer")
        if found_font and os.path.exists(found_font):
            LabelBase.register(name="BayerType", fn_regular=found_font)
        else:
            print("Warning: fonttype not found")

        # Register the "droplineregular" font
        LabelBase.register(name="DroplineRegular", fn_regular=self._find_font("droplineregular"))

        # Try to fit the app to the user's screen: maximize, else use system size, else fallback to fullscreen
        try:
            if hasattr(Window, "maximize"):
                try:
                    Window.maximize()
                except Exception:
                    pass
            elif getattr(Window, "system_size", None):
                try:
                    Window.size = Window.system_size
                except Exception:
                    pass
            else:
                try:
                    Window.fullscreen = 'auto'
                except Exception:
                    pass
        except Exception:
            pass

        return super(NebulaeApp, self).build()
    
if __name__ == "__main__":
    NebulaeApp().run()
