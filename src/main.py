import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.lang import Builder
Window.clearcolor = (1, 1, 1, 1)

API_URL = "http://127.0.0.1:5000/lifts"

LabelBase.register(name='CustomFont', fn_regular='FugazOne-Regular.ttf')

class HomeScreen(Screen):
    pass

class TemplateScreen(Screen):
    pass

class ShowLiftsScreen(Screen):
    def on_enter(self):
        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                lifts = response.json()
                if not lifts:
                    self.ids.max_lifts_label.text = "No lifts have been saved!"
                    return

                all_lifts = [
                    f"{lift['exercise']} {lift['weight']}kg x{lift['reps']}"
                    for lift in lifts
                ]

                self.ids.max_lifts_label.text = "\n".join(all_lifts)
            else:
                self.ids.max_lifts_label.text = f"Viga serveris: {response.status_code}"
        except Exception as e:
            self.ids.max_lifts_label.text = f"Viga: {str(e)}"

class EndScreen(Screen):
    def on_enter(self):
        lifts_screen = self.manager.get_screen("lifts")
        hours = lifts_screen.elapsed_seconds // 60
        minutes = lifts_screen.elapsed_seconds // 60
        seconds = lifts_screen.elapsed_seconds % 60
        self.ids.duration_label.text = f"Workout lasted: {hours:02d}{minutes:02d}:{seconds:02d}"

        try:
            response = requests.get(API_URL)
            if response.status_code == 200:
                lifts = response.json()
                max_lifts = {}
                for lift in lifts:
                    exercise = lift["exercise"]
                    weight = lift["weight"]
                    if exercise not in max_lifts or weight > max_lifts[exercise]:
                        max_lifts[exercise] = weight

                self.ids.max_lifts_label.text = "\n".join(
                    [f"{ex}: {wt}kg" for ex, wt in max_lifts.items()]
                )
            else:
                self.ids.max_lifts_label.text = "Error fetching lifts"
        except Exception as e:
            self.ids.max_lifts_label.text = f"Error: {str(e)}"

class ErinevadHarjutusedScreen(Screen):
    def lisa_harjutus(self, exercise):
        app = App.get_running_app()
        lifts_screen = app.root.get_screen("lifts")

        weight_text = lifts_screen.ids.weight_input.text
        reps_text = lifts_screen.ids.reps_input.text

        if not weight_text or not reps_text:
            print("⚠️ Please enter weight and reps in LiftsScreen first.")
            return

        try:
            weight = int(weight_text)
            reps = int(reps_text)
        except ValueError:
            print("⚠️ Invalid input — must be numbers.")
            return

        app.add_lift_to_api(exercise, weight, reps)




class LiftsScreen(Screen):
    clock_event = None
    elapsed_seconds = 0

    def on_enter(self):
        self.elapsed_seconds = 0
        self.update_clock_label()
        self.clock_event = Clock.schedule_interval(self.update_timer, 1)

    def on_leave(self):
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None

    def update_timer(self, dt):
        self.elapsed_seconds += 1
        self.update_clock_label()

    def update_clock_label(self):
        hours = self.elapsed_seconds // 60
        minutes = self.elapsed_seconds // 60
        seconds = self.elapsed_seconds % 60
        self.ids.clock_label.text = f"{hours:02d}{minutes:02d}:{seconds:02d}"
    
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

    def finish_workout(self):
        if self.clock_event:
            self.clock_event.cancel()
            self.clock_event = None
        self.manager.current = "end"


class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(LiftsScreen(name="lifts"))
        sm.add_widget(TemplateScreen(name="templates"))
        sm.add_widget(EndScreen(name="end"))
        sm.add_widget(ErinevadHarjutusedScreen(name="erinevad_harjutused"))
        sm.add_widget(ShowLiftsScreen(name="show"))
        return sm

    def add_lift_to_api(self, exercise, weight, reps):
        data = {"exercise": exercise, "weight": weight, "reps": reps}
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 201:
                print(f"✅ Added: {exercise} {weight}kg x{reps}")
            else:
                print(f"⚠️ Server returned {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending data: {e}")

if __name__ == "__main__":
    MyApp().run()
