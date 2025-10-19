from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///strloglifts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, default="Workout")
    date = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Integer, nullable=False) 
    notes = db.Column(db.String(200), nullable=True)
    
    lifts = db.relationship('Lift', backref='workout', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "date": self.date,
            "duration": self.duration,
            "notes": self.notes,
            "lifts": [lift.to_dict() for lift in self.lifts]
        }


class Lift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)
    workout_id = db.Column(db.Integer, db.ForeignKey('workout.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "exercise": self.exercise,
            "weight": self.weight,
            "reps": self.reps,
            "workout_id": self.workout_id
        }

with app.app_context():
    db.create_all()

@app.route("/workouts", methods=["POST"])
def create_workout():
    data = request.json
    
    new_workout = Workout(
        name=data.get("name", "Workout"),
        date=data.get("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        duration=data.get("duration", 0),
        notes=data.get("notes", "")
    )
    db.session.add(new_workout)
    db.session.flush() 
    
    for lift_data in data.get("lifts", []):
        lift = Lift(
            exercise=lift_data["exercise"],
            weight=lift_data["weight"],
            reps=lift_data["reps"],
            workout_id=new_workout.id
        )
        db.session.add(lift)
    
    db.session.commit()
    
    return jsonify(new_workout.to_dict()), 201

@app.route("/workouts", methods=["GET"])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify([workout.to_dict() for workout in workouts])

@app.route("/workouts/<int:workout_id>", methods=["GET"])
def get_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    return jsonify(workout.to_dict())

@app.route("/workouts/<int:workout_id>", methods=["DELETE"])
def delete_workout(workout_id):
    workout = Workout.query.get_or_404(workout_id)
    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout deleted successfully"})

@app.route("/lifts", methods=["POST"])
def add_lift():
    data = request.json
    
    if "workout_id" not in data:
        workout = Workout(
            name="Single Lift Workout",
            date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            duration=0,
            notes="Auto-created for single lift"
        )
        db.session.add(workout)
        db.session.flush()
        workout_id = workout.id
    else:
        workout_id = data["workout_id"]
    
    new_lift = Lift(
        exercise=data["exercise"],
        weight=data["weight"],
        reps=data["reps"],
        workout_id=workout_id
    )
    db.session.add(new_lift)
    db.session.commit()
    
    return jsonify(new_lift.to_dict()), 201

@app.route("/lifts", methods=["GET"])
def get_lifts():
    lifts = Lift.query.all()
    return jsonify([lift.to_dict() for lift in lifts])

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)