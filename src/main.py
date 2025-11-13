from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.clock import Clock
from kivy.network.urlrequest import UrlRequest
from kivy.core.text import LabelBase
import json
from datetime import datetime
from kivy.core.window import Window
Window.fullscreen = 'auto'

class HomeScreen(Screen):
    pass

class LiftsScreen(Screen):
    current_exercise = StringProperty("")
    workout_start_time = NumericProperty(0)
    current_workout_lifts = ListProperty([])
    
    def on_enter(self):
        self.workout_start_time = Clock.get_time()
        self.update_clock()
        Clock.schedule_interval(self.update_clock, 1)
    
    def update_clock(self, dt=None):
        if self.workout_start_time:
            elapsed = Clock.get_time() - self.workout_start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.ids.clock_label.text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def add_lift(self):
        weight = self.ids.weight_input.text
        reps = self.ids.reps_input.text
        
        if weight and reps and self.current_exercise:
            lift_data = {
                "exercise": self.current_exercise,
                "weight": int(weight),
                "reps": int(reps)
            }
            self.current_workout_lifts.append(lift_data)
            
            self.ids.weight_input.text = ""
            self.ids.reps_input.text = ""
            
            print(f"Added {self.current_exercise}: {weight}kg x {reps} reps")
    
    def finish_workout(self):
        if not self.current_workout_lifts:
            print("No lifts to save!")
            return
        

        duration_minutes = int((Clock.get_time() - self.workout_start_time) / 60)
        
        workout_data = {
            "name": f"Workout {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "duration": duration_minutes,
            "notes": f"Completed {len(self.current_workout_lifts)} lifts",
            "lifts": self.current_workout_lifts
        }
        
        headers = {'Content-Type': 'application/json'}
        UrlRequest(
            'http://127.0.0.1:5000/workouts',
            on_success=self.on_workout_saved,
            on_failure=self.on_request_error,
            on_error=self.on_request_error,
            req_headers=headers,
            req_body=json.dumps(workout_data),
            method='POST'
        )
    
    def on_workout_saved(self, req, result):
        print("Workout saved successfully!")
        self.current_workout_lifts = []
        self.workout_start_time = 0
        self.current_exercise = ""
        Clock.unschedule(self.update_clock)
        self.ids.clock_label.text = "00:00:00"
        
        self.manager.current = "end"
    
    def on_request_error(self, req, error):
        print(f"Error saving workout: {error}")

class ErinevadHarjutusedScreen(Screen):
    def lisa_harjutus(self, exercise):
        lifts_screen = self.manager.get_screen('lifts')
        lifts_screen.current_exercise = exercise
        print(f"Selected exercise: {exercise}")

class ShowLiftsScreen(Screen):
    def on_enter(self):
        self.load_workouts()
    
    def load_workouts(self):
        UrlRequest(
            'http://127.0.0.1:5000/workouts',
            on_success=self.on_workouts_loaded,
            on_failure=self.on_request_error,
            on_error=self.on_request_error
        )
    
    def on_workouts_loaded(self, req, result):
        display_text = "WORKOUT HISTORY:\n\n"
        
        for workout in result:
            display_text += f"{workout['name']} ({workout['date']})\n"
            display_text += f"Duration: {workout['duration']} min\n"
            
            exercise_max = {}
            for lift in workout['lifts']:
                exercise = lift['exercise']
                weight = lift['weight']
                if exercise not in exercise_max or weight > exercise_max[exercise]:
                    exercise_max[exercise] = weight
            
            for exercise, max_weight in exercise_max.items():
                display_text += f"  {exercise}: {max_weight}kg (max)\n"
            
            display_text += "  All lifts:\n"
            for lift in workout['lifts']:
                display_text += f"    {lift['exercise']}: {lift['weight']}kg x {lift['reps']}\n"
            
            display_text += "\n" + "="*50 + "\n\n"
        
        self.ids.max_lifts_label.text = display_text
    
    def on_request_error(self, req, error):
        print(f"Error loading workouts: {error}")

class EndScreen(Screen):
    def on_enter(self):
        UrlRequest(
            'http://127.0.0.1:5000/workouts',
            on_success=self.on_workouts_loaded,
            on_failure=self.on_request_error
        )
    
    def on_workouts_loaded(self, req, result):
        if result:
            latest_workout = result[-1]
            
            self.ids.duration_label.text = f"Workout lasted: {latest_workout['duration']} minutes"
            
            exercise_max = {}
            for lift in latest_workout['lifts']:
                exercise = lift['exercise']
                weight = lift['weight']
                if exercise not in exercise_max or weight > exercise_max[exercise]:
                    exercise_max[exercise] = weight
            
            max_lifts_text = "Best Lifts:\n"
            for exercise, max_weight in exercise_max.items():
                max_lifts_text += f"{exercise}: {max_weight}kg\n"
            
            self.ids.max_lifts_label.text = max_lifts_text
    
    def on_request_error(self, req, error):
        print(f"Error loading workout data: {error}")

class TemplateScreen(Screen):
    pass

class MyApp(App):
    def build(self):
        LabelBase.register(name="CustomFont",
                          fn_regular="FugazOne-Regular.ttf")
        
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(LiftsScreen(name='lifts'))
        sm.add_widget(TemplateScreen(name='templates'))
        sm.add_widget(ErinevadHarjutusedScreen(name='erinevad_harjutused'))
        sm.add_widget(EndScreen(name='end'))
        sm.add_widget(ShowLiftsScreen(name='show'))
        return sm

if __name__ == '__main__':
    MyApp().run()
