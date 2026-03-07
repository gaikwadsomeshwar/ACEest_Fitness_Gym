# Import necessary libraries for database handling, random generation, dates, and web framework
import sqlite3
import random
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash

# Configure Flask to look for templates in the current directory
app = Flask(__name__, template_folder='.')
app.secret_key = 'aceest_secret_key'
DB_NAME = "aceest_fitness.db"

# Core Business Logic: Program Factors for Calorie Calculation
PROGRAMS = {
    "Fat Loss (FL)": {"factor": 22, "desc": "High intensity, calorie deficit focus"},
    "Muscle Gain (MG)": {"factor": 35, "desc": "Hypertrophy, surplus focus"},
    "Beginner (BG)": {"factor": 26, "desc": "Technique mastery, maintenance"}
}

# Helper function to establish a database connection
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row # Access columns by name
    return conn

# Initialize the database tables if they don't exist
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Schema adapted from Aceestver-3.2.4.py
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        age INTEGER,
        height REAL,
        weight REAL,
        program TEXT,
        calories INTEGER,
        target_weight REAL,
        target_adherence INTEGER,
        membership_status TEXT DEFAULT 'Active',
        membership_end TEXT
    )
    """)
    
    # Workouts Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        date TEXT,
        workout_type TEXT,
        duration_min INTEGER,
        notes TEXT,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
    """)

    # Metrics Table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        date TEXT,
        weight REAL,
        waist REAL,
        bodyfat REAL,
        FOREIGN KEY(client_id) REFERENCES clients(id)
    )
    """)
    conn.commit()
    conn.close()

# Route: Dashboard (Home) - Lists all clients
@app.route('/')
def index():
    search_query = request.args.get('search')
    conn = get_db_connection()
    if search_query:
        clients = conn.execute('SELECT * FROM clients WHERE lower(name) LIKE lower(?)', ('%' + search_query + '%',)).fetchall()
    else:
        clients = conn.execute('SELECT * FROM clients').fetchall()
    conn.close()
    return render_template('index.html', clients=clients)

# Route: Add Client - Handles form submission to register a new client
@app.route('/add_client', methods=('GET', 'POST'))
def add_client():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        weight = request.form['weight']
        height = request.form['height']
        program = request.form['program']

        if not name or not weight or not program:
            flash('Name, Weight, and Program are required!')
        else:
            # Calculate daily calorie target based on weight and program factor
            try:
                weight_val = float(weight)
                factor = PROGRAMS[program]['factor']
                calories = int(weight_val * factor)
                
                # Calculate target weight based on program
                target_weight = weight_val
                if "Fat Loss" in program:
                    target_weight = weight_val * 0.95
                elif "Muscle Gain" in program:
                    target_weight = weight_val * 1.05
                
                conn = get_db_connection()
                conn.execute("""
                    INSERT INTO clients (name, age, height, weight, program, calories, target_weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, age, height, weight_val, program, calories, round(target_weight, 1)))
                conn.commit()
                conn.close()
                flash(f'Client {name} added successfully!')
                return redirect(url_for('index'))
            except sqlite3.IntegrityError:
                flash(f'Client with name {name} already exists.')
            except ValueError:
                flash('Invalid numeric input for Age, Weight, or Height.')

    return render_template('add_client.html', programs=PROGRAMS)

# Route: Client Profile - Shows details, BMI, and history
@app.route('/client/<int:client_id>')
def client_detail(client_id):
    conn = get_db_connection()
    client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
    
    # Fetch recent activity
    workouts = conn.execute('SELECT * FROM workouts WHERE client_id = ? ORDER BY date DESC LIMIT 5', (client_id,)).fetchall()
    metrics = conn.execute('SELECT * FROM metrics WHERE client_id = ? ORDER BY date DESC LIMIT 5', (client_id,)).fetchall()
    conn.close()
    
    if client is None:
        return "Client not found", 404
        
    # BMI Calculation Logic
    bmi = 0
    bmi_category = "N/A"
    if client['height'] and client['weight']:
        h_m = client['height'] / 100.0
        bmi = round(client['weight'] / (h_m * h_m), 1)
        if bmi < 18.5: bmi_category = "Underweight"
        elif bmi < 25: bmi_category = "Normal"
        elif bmi < 30: bmi_category = "Overweight"
        else: bmi_category = "Obese"

    return render_template('client_detail.html', client=client, workouts=workouts, metrics=metrics, bmi=bmi, bmi_category=bmi_category)

# Route: Log Workout - Saves a workout session for a specific client
@app.route('/client/<int:client_id>/log_workout', methods=('GET', 'POST'))
def log_workout(client_id):
    if request.method == 'POST':
        w_date = request.form['date']
        w_type = request.form['type']
        duration = request.form['duration']
        notes = request.form['notes']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO workouts (client_id, date, workout_type, duration_min, notes) VALUES (?, ?, ?, ?, ?)',
                     (client_id, w_date, w_type, duration, notes))
        conn.commit()
        conn.close()
        flash('Workout logged successfully!')
        return redirect(url_for('client_detail', client_id=client_id))
        
    return render_template('add_workout.html', client_id=client_id, today=date.today())

# Route: Log Metric - Saves body stats and updates current weight
@app.route('/client/<int:client_id>/log_metric', methods=('GET', 'POST'))
def log_metric(client_id):
    if request.method == 'POST':
        m_date = request.form['date']
        weight = request.form['weight']
        waist = request.form['waist']
        bodyfat = request.form['bodyfat']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO metrics (client_id, date, weight, waist, bodyfat) VALUES (?, ?, ?, ?, ?)',
                     (client_id, m_date, weight, waist, bodyfat))
        
        # Update current weight in client profile
        if weight:
            conn.execute('UPDATE clients SET weight = ? WHERE id = ?', (weight, client_id))
            
        conn.commit()
        conn.close()
        flash('Body metrics logged successfully!')
        return redirect(url_for('client_detail', client_id=client_id))
        
    return render_template('add_metric.html', client_id=client_id, today=date.today())

# Route: Generate Program - Creates a random 3-day schedule based on program type
@app.route('/client/<int:client_id>/generate_program')
def generate_program(client_id):
    conn = get_db_connection()
    client = conn.execute('SELECT * FROM clients WHERE id = ?', (client_id,)).fetchone()
    conn.close()
    
    # Logic adapted from Aceestver-3.1.2.py
    exercises_pool = {
        "Strength": ["Squat", "Deadlift", "Bench Press", "Overhead Press", "Pull-Up", "Barbell Row"],
        "Hypertrophy": ["Leg Press", "Incline Dumbbell Press", "Lat Pulldown", "Lateral Raise", "Bicep Curl", "Tricep Extension"],
        "Conditioning": ["Running", "Cycling", "Rowing", "Burpees", "Jump Rope", "Kettlebell Swings"],
        "Full Body": ["Push-Up", "Pull-Up", "Lunge", "Plank", "Dumbbell Row", "Dumbbell Press"]
    }
    
    # Determine focus area based on the client's assigned program
    program_name = client['program']
    focus = "Full Body"
    if "Fat Loss" in program_name:
        focus = "Conditioning"
    elif "Muscle Gain" in program_name:
        focus = "Hypertrophy"
    elif "Beginner" in program_name:
        focus = "Full Body"
        
    # Generate a 3-day sample schedule
    schedule = {}
    days = ["Monday", "Wednesday", "Friday"]
    
    for day in days:
        daily_exercises = []
        # Logic: Mix specific focus exercises with general strength basics
        pool = exercises_pool.get(focus, []) + exercises_pool["Strength"]
        selected = random.sample(pool, k=4)
        
        for ex in selected:
            sets = random.randint(3, 4)
            reps = random.randint(8, 12)
            daily_exercises.append({"name": ex, "sets": sets, "reps": reps})
        schedule[day] = daily_exercises

    return render_template('generated_program.html', client=client, schedule=schedule, focus=focus)

# Route: Delete Client - Removes client and associated data
@app.route('/client/<int:client_id>/delete', methods=('POST',))
def delete_client(client_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM workouts WHERE client_id = ?', (client_id,))
    conn.execute('DELETE FROM metrics WHERE client_id = ?', (client_id,))
    conn.execute('DELETE FROM clients WHERE id = ?', (client_id,))
    conn.commit()
    conn.close()
    flash('Client deleted successfully!')
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    print("\n---------------------------------------------------")
    print(" * Local Access: http://127.0.0.1:5000 (Use this on this computer)")
    print(" * Network Access: http://<your_ip>:5000 (Use this from other devices on the same network)")
    print("---------------------------------------------------\n")
    app.run(debug=True, port=5000, host='0.0.0.0')