import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import kivy
from kivy.uix.label import Label
from kivy.core.text import LabelBase, DEFAULT_FONT
from kivy.core.window import Window
Window.fullscreen = True
kivy.require('1.11.1') # Replace with your Kivy version

#vorgu sisene ipc:/Users/Omanik/Downloads/proge4ttg-main/src/main.py
API_URL = "http://127.0.0.1:5000/lifts"

class MyLayout(BoxLayout):
    def add_lift(self):
        exercise = self.ids.exercise_input.text
        weight = int(self.ids.weight_input.text)
        reps = int(self.ids.reps_input.text)

        data = {"exercise": exercise, "weight": weight, "reps": reps}
        response = requests.post(API_URL, json=data)

        if response.status_code == 201:
            self.ids.output_label.text = f"Added: {exercise} {weight}kg x{reps}"
        else:
            self.ids.output_label.text = "Error adding lift"

    def get_lifts(self):
        response = requests.get(API_URL)
        if response.status_code == 200:
            lifts = response.json()
            self.ids.output_label.text = "\n".join(
                [f"{l['exercise']} {l['weight']}kg x{l['reps']}" for l in lifts]
            )
        else:
            self.ids.output_label.text = "Error fetching lifts"

class MyApp(App):
    def build(self):
        return MyLayout()

if __name__ == "__main__":
    MyApp().run()
