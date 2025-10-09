import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen

API_URL = "http://127.0.0.1:5000/lifts"


class HomeScreen(Screen):
    pass

class TemplateScreen(Screen):
    pass

class ShowLiftsScreen(Screen):
    pass

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
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(LiftsScreen(name="lifts"))
        sm.add_widget(TemplateScreen(name="templates"))
        sm.add_widget(ErinevadHarjutusedScreen(name="erinevad_harjutused"))
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
