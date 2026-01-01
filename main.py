from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image as CoreImage
from kivy.core.text import LabelBase
from kivy.core.window import Window
import os


class MainLayout(BoxLayout):
    pass


class NebulaeApp(App):
    def build(self):
        return MainLayout()


if __name__ == "__main__":
    # Register the imported font by searching common locations for a matching .otf/.ttf
    def _find_font(substr="bayer"):
        substr = substr.lower()
        # Search the app directory first
        app_dir = os.path.dirname(__file__)
        for root, _, files in os.walk(app_dir):
            for f in files:
                if f.lower().endswith((".otf", ".ttf")) and substr in f.lower():
                    return os.path.join(root, f)
        # Search user's Downloads
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        for root, _, files in os.walk(downloads):
            for f in files:
                if f.lower().endswith((".otf", ".ttf")) and substr in f.lower():
                    return os.path.join(root, f)
        return None

    try:
        found_font = _find_font("bayer")
        if found_font and os.path.exists(found_font):
            LabelBase.register(name="BayerType", fn_regular=found_font)
    except Exception:
        pass

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

    NebulaeApp().run()
