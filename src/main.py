from kivy.app import App
from kivy.uix.label import Label
from modules.backend import process_text
import sys
print(sys.path)


class MyApp(App):
    def build(self):
        return None  # Kivy otsib automaatselt myapp.kv

    def process_input(self, text):
        result = process_text(text)
        self.root.ids.output_label.text = result

if __name__ == "__main__":
    MyApp().run()
