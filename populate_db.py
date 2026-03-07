import sqlite3

# Database configuration
DB_NAME = "aceest_fitness.db"

# Program definitions matching flask_app.py logic
PROGRAMS = {
    "Fat Loss (FL)": 22,
    "Muscle Gain (MG)": 35,
    "Beginner (BG)": 26
}

# Dataset of 20 clients
# Format: (Name, Age, Height(cm), Weight(kg), Program)
DATASET = [
    ("John Doe", 34, 178, 85.0, "Fat Loss (FL)"),
    ("Jane Smith", 29, 165, 62.0, "Muscle Gain (MG)"),
    ("Mike Ross", 25, 182, 75.0, "Muscle Gain (MG)"),
    ("Rachel Zane", 24, 170, 58.0, "Fat Loss (FL)"),
    ("Harvey Specter", 40, 185, 90.0, "Beginner (BG)"),
    ("Donna Paulsen", 38, 172, 65.0, "Beginner (BG)"),
    ("Louis Litt", 42, 175, 95.0, "Fat Loss (FL)"),
    ("Jessica Pearson", 45, 178, 70.0, "Beginner (BG)"),
    ("Alex Williams", 30, 180, 88.0, "Muscle Gain (MG)"),
    ("Samantha Wheeler", 32, 173, 68.0, "Muscle Gain (MG)"),
    ("Robert Zane", 55, 188, 100.0, "Fat Loss (FL)"),
    ("Katrina Bennett", 28, 168, 60.0, "Fat Loss (FL)"),
    ("Travis Tanner", 35, 183, 86.0, "Muscle Gain (MG)"),
    ("Dana Scott", 33, 175, 64.0, "Beginner (BG)"),
    ("Sean Cahill", 48, 176, 82.0, "Fat Loss (FL)"),
    ("Sheila Sazs", 39, 165, 75.0, "Fat Loss (FL)"),
    ("Harold Gunderson", 26, 179, 72.0, "Muscle Gain (MG)"),
    ("Jenny Griffith", 27, 164, 56.0, "Beginner (BG)"),
    ("Trevor Evans", 31, 181, 84.0, "Fat Loss (FL)"),
    ("Daniel Hardman", 52, 174, 80.0, "Beginner (BG)")
]

def seed_database():
    """Populates the database with the sample dataset."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    print(f"Connecting to {DB_NAME}...")
    
    # Ensure table exists (in case app hasn't run yet)
    # We rely on the app's schema, but for safety we can assume the app has been run or we just insert.
    # If table doesn't exist, this will fail. The README says run flask_app.py first.
    
    count = 0
    for name, age, height, weight, program in DATASET:
        # Calculate calories based on program factor
        factor = PROGRAMS.get(program, 26)
        calories = int(weight * factor)
        
        # Determine target weight (simple logic for dataset generation)
        target_weight = weight
        if "Fat Loss" in program:
            target_weight = weight * 0.95 # Target 5% loss
        elif "Muscle Gain" in program:
            target_weight = weight * 1.05 # Target 5% gain
            
        try:
            cur.execute("""
                INSERT INTO clients (name, age, height, weight, program, calories, target_weight, membership_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Active')
            """, (name, age, height, weight, program, calories, round(target_weight, 1)))
            count += 1
            print(f"Inserted: {name}")
        except sqlite3.IntegrityError:
            print(f"Skipped: {name} (Already exists)")
        except sqlite3.OperationalError as e:
            print(f"Error: {e}. Make sure to run flask_app.py first to initialize the database.")
            break

    conn.commit()
    conn.close()
    print(f"\nSuccessfully added {count} clients to the database.")

if __name__ == "__main__":
    seed_database()