from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///strloglifts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Lift(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    exercise = db.Column(db.String(100), nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "exercise": self.exercise,
            "weight": self.weight,
            "reps": self.reps,
        }

with app.app_context():
    db.create_all()

@app.route("/lifts", methods=["POST"])
def add_lift():
    data = request.json
    new_lift = Lift(
        exercise=data["exercise"],
        weight=data["weight"],
        reps=data["reps"]
    )
    db.session.add(new_lift)
    db.session.commit()
    return jsonify(new_lift.to_dict()), 201

@app.route("/lifts", methods=["GET"])
def get_lifts():
    lifts = Lift.query.all()
    return jsonify([lift.to_dict() for lift in lifts])

if __name__ == "__main__":
    # Run on localhost for local development
    app.run(host="127.0.0.1", port=5000, debug=True)
