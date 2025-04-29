from flask import Flask, render_template, request, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
import pandas as pd
from dataset import load_data

stats = load_data("megaGymDataset.csv")
to_delete = []
app = Flask(__name__)
app.secret_key = "fitness_secret_key"
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
df = pd.read_csv("megaGymDataset.csv")
print(df.head())  # Show the first few rows

# Fake user database (Replace with SQLite or PostgreSQL)
users = {"testuser": bcrypt.generate_password_hash("password").decode('utf-8')}

class User(UserMixin):
    def __init__(self, username):
        self.id = username


@login_manager.user_loader
def load_user(username):
    return User(username) if username in users else None

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def create_user():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        
        if username in users:
            return "User already exists!"
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        users[username] = hashed_password
        return redirect(url_for("home"))
    
    return render_template("create.html")

@app.route("/login", methods=["POST", 'GET'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
        if username in users and bcrypt.check_password_hash(users[username], password):
            login_user(User(username))
            return redirect(url_for("dashboard"))
    
        return redirect(url_for('create_user'))

    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('real.html')

@app.route('/workout', methods=['GET', 'POST'])
@login_required
def workout_form():
    username = current_user.id  # Get logged-in username

    def calculate_bmi_imperial(weight_lbs, height_in):
        try:
            weight_kg = float(weight_lbs) / 2.20462
            height_m = float(height_in) * 0.0254
            return round(weight_kg / (height_m ** 2), 1)
        except:
            return None

    def estimate_fitness_level(age, bmi, gender):
        try:
            age = int(age)
            if age < 16 or bmi is None or bmi > 30:
                return "Beginner"
            elif 18.5 <= bmi <= 25:
                return "Intermediate" if age < 40 else "Advanced"
            else:
                return "Beginner"
        except:
            return "Beginner"

    if request.method == 'POST':
        age = request.form.get('age', '')
        weight = request.form.get('weight', '')
        height = request.form.get('height', '')
        gender = request.form.get('gender', '')
    
        bmi = calculate_bmi_imperial(weight, height)
        fitness_level = estimate_fitness_level(age, bmi, gender)

        to_delete = []  # <<< Move inside POST block

        for key, data in stats.items():
            if data.get('Level') != fitness_level:
                to_delete.append(key)

        for key in to_delete:  # <<< Separate loop AFTER
            del stats[key]
        to_delete = []  # Reset to_delete for next use

        print(f"Age: {age}, Weight: {weight}, Height: {height}, Gender: {gender}, BMI: {bmi}, Level: {fitness_level}")

        return render_template(
            'workout.html',
            username=username,
            age=age,
            weight=weight,
            height=height,
            gender=gender,
            bmi=bmi,
            fitness_level=fitness_level
        )

    return render_template('workout.html', username=username, age='', weight='', height='', gender='', bmi='', fitness_level='')


@app.route('/type', methods=['GET', 'POST'])
@login_required
def workouts():
    username = current_user.id
    selected_equipment = request.form.getlist('item')
    selected_equipment = [item.capitalize() for item in selected_equipment]  # Gets all checked items as a list
    print(selected_equipment)  # Example: ['bands', 'dumbell', 'machine']
    # Now you can use selected_equipment in your logic
    to_delete = []  # <<< Move inside POST block

    for key, data in stats.items():
        if data.get('Equipment') != selected_equipment:
            to_delete.append(key)
        

    for key in to_delete:  # <<< Separate loop AFTER
        del stats[key]
    to_delete = []  # Reset to_delete for next use
    
    return render_template('type.html', equipment=selected_equipment, username=username)

@app.route('/area', methods=['GET', 'POST'])
@login_required
def area():
    username = current_user.id
    targets = request.form.getlist('item')  # Gets all checked items as a list
    targets = [item.capitalize() for item in targets]
    print(targets)  # Example: ['bands', 'dumbell', 'machine']
    to_delete = []  # <<< Move inside POST block

    for key, data in stats.items():
        if data.get('Type') != targets:
            to_delete.append(key)

    for key in to_delete:  # <<< Separate loop AFTER
        del stats[key]
    to_delete = []  # Reset to_delete for next use
    # Now you can use selected_equipment in your logic
    return render_template('area.html', targets=targets, username=username)


@app.route('/exercises', methods=['GET', 'POST'])
@login_required
def exercises():
    username = current_user.id
    targets = request.form.getlist('item')
    targets = [item.capitalize() for item in targets]
    print(targets)
    to_delete = []  # <<< Move inside POST block
    for key, data in stats.items():
        if data.get('BodyPart') != targets:
            to_delete.append(key)

    for key in to_delete:  # <<< Separate loop AFTER
        del stats[key]
    to_delete = []  # Reset to_delete for next use
    print(stats)
    return render_template('exercises.html', targets=targets, username=username, stats=stats)

if __name__ == "__main__":
    app.run(debug=True)