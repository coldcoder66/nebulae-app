from kivy.app import App
from kivy.uix.boxlayout import BoxLayout

class MainLayout(BoxLayout):
    pass

class NebulaeApp(App):
    def build(self):
        return MainLayout()

if __name__ == "__main__":
    NebulaeApp().run()
