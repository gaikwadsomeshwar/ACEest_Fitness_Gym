# ACEest Fitness Manager

A foundational Flask web application tailored for fitness and gym management. This application allows trainers to manage clients, track workouts and body metrics, and generate basic workout programs based on specific fitness goals.

## Features

- **Client Management**: Register new clients with details like age, weight, height, and specific fitness programs (Fat Loss, Muscle Gain, Beginner).
- **Dashboard**: A centralized view of all active clients and their key statistics.
- **Calorie Calculator**: Automatically calculates daily calorie targets based on the selected program and client weight.
- **Workout Logging**: Log daily workout sessions including type, duration, and notes.
- **Metrics Tracking**: Track body weight, waist circumference, and body fat percentage over time.
- **BMI Calculation**: Automatic BMI calculation and risk categorization on the client profile.
- **AI Program Generator**: Generates a randomized 3-day workout schedule tailored to the client's focus area.

## Prerequisites

- Python 3.12 or higher
- pip (Python package installer)

## Local Setup and Execution

Follow these steps to set up and run the application on your local machine.

### 1. Clone or Download the Repository

Ensure all project files (Python scripts and HTML templates) are in the same directory.

### 2. Create a Virtual Environment (Optional but Recommended)

It is best practice to run Python applications in an isolated environment.

**Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Install the required Python packages using `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database and Run the App

Run the main application script. This will automatically create the SQLite database (`aceest_fitness.db`) if it does not exist.

```bash
python flask_app.py
```

### 5. Access the Application

Open your web browser and navigate to:

- **Local Machine:** `http://127.0.0.1:5000`
- **Network:** `http://<your-ip-address>:5000`

## Running Tests

To verify the application logic and ensure everything is working as expected, you can run the included test suite manually.

1. Ensure your virtual environment is activated and dependencies are installed.
2. Run the tests using `pytest`:

```bash
pytest
```

## Docker Setup (Recommended)

To avoid compatibility issues with local Python versions (like Python 3.14), run the application using Docker.

```bash
docker-compose up --build
```

The application will be available at `http://localhost:5000`.
