"""
ACEest Fitness Gym - Flask Application

A modular Flask web application for managing fitness gym clients, workouts,
metrics, and personalized training programs.

Version: 0.1.0
Author: DevOps Assignment
License: MIT
"""

import os
import sqlite3
from datetime import date
from logging_config import logger
from flask import Flask, render_template, request, redirect, url_for, flash

from config import get_config
from app.database import get_db_connection, init_db
from app.utils import (
    PROGRAMS,
    calculate_calories,
    calculate_target_weight,
    calculate_bmi,
    bmi_category,
    generate_program_schedule,
)


def read_version() -> str:
    """
    Read application version from VERSION file.

    Returns:
        str: Version string (e.g., "0.1.0"). Returns "0.0.0" if file not found.
    """
    try:
        with open("VERSION", "r", encoding="utf-8") as version_file:
            version = version_file.read().strip()
            logger.debug(f"Loaded application version: {version}")
            return version
    except FileNotFoundError:
        logger.warning("VERSION file not found, using default 0.0.0")
        return "0.0.0"


# Initialize Flask application
APP_VERSION = read_version()
config = get_config()
app = Flask(__name__, template_folder=".")
app.config.from_object(config)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "aceest_secret_key_dev")

DB_NAME = os.getenv("ACEEST_DB", "aceest_fitness.db")

# Template constants
TEMPL_INDEX = "index.html"
TEMPL_ADD_CLIENT = "add_client.html"
TEMPL_CLIENT_DETAIL = "client_detail.html"
TEMPL_ADD_WORKOUT = "add_workout.html"
TEMPL_ADD_METRIC = "add_metric.html"
TEMPL_PROGRAM = "generated_program.html"
TEMPL_ERROR = "error.html"

logger.info(f"Flask app initialized: {app.config.get('ENV')} mode, v{APP_VERSION}")


def get_connection():
    """
    Get database connection with proper configuration.

    Returns:
        sqlite3.Connection: Database connection object.
    """
    return get_db_connection(DB_NAME)


@app.route("/", methods=("GET",))
def index():
    """
    Dashboard/Home route - displays list of all clients.

    Supports search functionality for filtering clients by name.

    Returns:
        str: Rendered HTML template with client list.
    """
    logger.info("Accessing index/dashboard page")
    search_query = request.args.get("search", "").strip()

    try:
        with get_connection() as conn:
            if search_query:
                logger.debug(f"Searching clients with query: {search_query}")
                clients = conn.execute(
                    "SELECT * FROM clients WHERE lower(name) LIKE lower(?)",
                    ("%" + search_query + "%",),
                ).fetchall()
            else:
                clients = conn.execute("SELECT * FROM clients").fetchall()

        logger.debug(f"Retrieved {len(clients)} clients from database")
        return render_template(
            TEMPL_INDEX,
            clients=clients,
            programs=PROGRAMS,
            version=APP_VERSION,
        )
    except Exception as e:
        logger.error(f"Error accessing dashboard: {str(e)}", exc_info=True)
        flash("Error loading dashboard. Please try again.", "error")
        return render_template(TEMPL_INDEX, clients=[], programs=PROGRAMS, version=APP_VERSION), 500


@app.route("/health", methods=("GET",))
def health():
    """
    Health check endpoint for monitoring and CI/CD pipelines.

    Returns:
        dict: JSON response with status and version.
    """
    logger.debug("Health check requested")
    return {"status": "OK", "version": APP_VERSION}, 200


@app.route("/add_client", methods=("GET", "POST"))
def add_client():
    """
    Add a new client to the system.

    GET: Render form for adding a new client.
    POST: Process form submission and insert client into database.

    Expected form fields:
        - name: Client's full name (required)
        - age: Client's age (optional)
        - weight: Client's weight in kg (required)
        - height: Client's height in cm (optional)
        - program: Training program type (required)

    Returns:
        str: Rendered HTML template or redirect to index on success.
    """
    if request.method == "POST":
        logger.info("Attempting to add new client")
        
        name = request.form.get("name", "").strip()
        age = request.form.get("age", "").strip()
        weight = request.form.get("weight", "").strip()
        height = request.form.get("height", "").strip()
        program = request.form.get("program", "").strip()

        # Validate required fields
        if not name or not weight or not program:
            error_msg = "Name, Weight, and Program are required!"
            logger.warning(f"Client add validation failed: {error_msg}")
            flash(error_msg, "error")
            return render_template(TEMPL_ADD_CLIENT, programs=PROGRAMS), 400

        try:
            # Parse and validate numeric inputs
            weight_val = float(weight)
            age_val = int(age) if age else None
            height_val = float(height) if height else None

            # Calculate derived values
            calories = calculate_calories(weight_val, program)
            target_weight = calculate_target_weight(weight_val, program)

            logger.debug(
                f"Adding client: name={name}, weight={weight_val}, program={program}, "
                f"calories={calories}"
            )

            with get_connection() as conn:
                conn.execute(
                    """
                    INSERT INTO clients 
                    (name, age, height, weight, program, calories, target_weight)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (name, age_val, height_val, weight_val, program, calories, target_weight),
                )
                conn.commit()

            logger.info(f"Successfully added client: {name}")
            flash(f"Client {name} added successfully!", "success")
            return redirect(url_for("index"))

        except sqlite3.IntegrityError:
            error_msg = f"Client with name {name} already exists."
            logger.warning(f"Duplicate client error: {error_msg}")
            flash(error_msg, "error")
            return render_template(TEMPL_ADD_CLIENT, programs=PROGRAMS), 400
        except ValueError as e:
            error_msg = f"Invalid numeric input for client {name}: {str(e)}"
            logger.warning(f"Add client validation error: {error_msg}")
            flash(f"Invalid input: {str(e)}", "error")
            return render_template(TEMPL_ADD_CLIENT, programs=PROGRAMS), 400
        except Exception as e:
            logger.error(f"Unexpected error adding client {name}: {str(e)}", exc_info=True)
            flash("An error occurred while adding the client.", "error")
            return render_template(TEMPL_ADD_CLIENT, programs=PROGRAMS), 500

    return render_template(TEMPL_ADD_CLIENT, programs=PROGRAMS)


@app.route("/client/<int:client_id>", methods=("GET",))
def client_detail(client_id):
    """
    Display detailed client profile including BMI, workouts, and metrics.

    Args:
        client_id (int): ID of the client to display.

    Returns:
        str: Rendered client detail template or 404 error.
    """
    logger.info(f"Accessing client profile: client_id={client_id}")

    try:
        with get_connection() as conn:
            client = conn.execute(
                "SELECT * FROM clients WHERE id = ?", (client_id,)
            ).fetchone()
            workouts = conn.execute(
                "SELECT * FROM workouts WHERE client_id = ? ORDER BY date DESC LIMIT 5",
                (client_id,),
            ).fetchall()
            metrics = conn.execute(
                "SELECT * FROM metrics WHERE client_id = ? ORDER BY date DESC LIMIT 5",
                (client_id,),
            ).fetchall()

        if client is None:
            logger.warning(f"Client not found: client_id={client_id}")
            return "Client not found", 404

        # Calculate BMI if height and weight are available
        bmi = 0.0
        category = "N/A"
        if client["height"] and client["weight"]:
            bmi = calculate_bmi(client["weight"], client["height"])
            category = bmi_category(bmi)
            logger.debug(f"Calculated BMI for client {client_id}: {bmi} ({category})")

        logger.debug(f"Retrieved profile for client: {client['name']}")
        return render_template(
            TEMPL_CLIENT_DETAIL,
            client=client,
            workouts=workouts,
            metrics=metrics,
            bmi=bmi,
            bmi_category=category,
        )
    except Exception as e:
        logger.error(f"Error retrieving client detail: {str(e)}", exc_info=True)
        flash("Error loading client details.", "error")
        return redirect(url_for("index"))


@app.route("/client/<int:client_id>/log_workout", methods=("GET", "POST"))
def log_workout(client_id):
    """
    Log a workout session for a client.

    GET: Display workout logging form.
    POST: Process and store workout data.

    Expected form fields:
        - date: Workout date (required)
        - type: Workout type (required)
        - duration: Duration in minutes (required)
        - notes: Additional notes (optional)

    Args:
        client_id (int): ID of the client.

    Returns:
        str: Rendered form or redirect to client detail on success.
    """
    if request.method == "POST":
        logger.info(f"Logging workout for client_id={client_id}")

        w_date = request.form.get("date", "").strip()
        w_type = request.form.get("type", "").strip()
        duration = request.form.get("duration", "").strip()
        notes = request.form.get("notes", "").strip()

        if not w_date or not w_type or not duration:
            error_msg = "Date, type, and duration are required for workout logging."
            logger.warning(f"Workout validation failed: {error_msg}")
            flash(error_msg, "error")
            return render_template(TEMPL_ADD_WORKOUT, client_id=client_id, today=date.today()), 400
        else:
            try:
                duration_val = int(duration)
                logger.debug(f"Recording workout: type={w_type}, duration={duration_val}min")

                with get_connection() as conn:
                    conn.execute(
                        "INSERT INTO workouts (client_id, date, workout_type, duration_min, notes) "
                        "VALUES (?, ?, ?, ?, ?)",
                        (client_id, w_date, w_type, duration_val, notes),
                    )
                    conn.commit()

                logger.info(f"Workout logged successfully for client_id={client_id}")
                flash("Workout logged successfully!", "success")
                return redirect(url_for("client_detail", client_id=client_id))
            except ValueError as e:
                logger.warning(f"Invalid duration value provided for client {client_id}: {str(e)}")
                flash("Duration must be a number.", "error")
                return render_template(TEMPL_ADD_WORKOUT, client_id=client_id, today=date.today()), 400
            except Exception as e:
                logger.error(f"Error logging workout for client {client_id}: {str(e)}", exc_info=True)
                flash("Error logging workout.", "error")
                return render_template(TEMPL_ADD_WORKOUT, client_id=client_id, today=date.today()), 500

    return render_template(TEMPL_ADD_WORKOUT, client_id=client_id, today=date.today())


def _validate_and_parse_metric_input(m_date: str, weight: str, waist: str, bodyfat: str):
    """
    Validate and parse metric input values.

    Args:
        m_date (str): Measurement date.
        weight (str): Weight in kg.
        waist (str): Waist circumference in cm.
        bodyfat (str): Body fat percentage.

    Returns:
        tuple: (date, weight_val, waist_val, bodyfat_val) or raises ValueError.

    Raises:
        ValueError: If required fields are missing or invalid numeric values.
    """
    if not m_date or not weight:
        raise ValueError("Date and Weight are required for metric logging.")

    weight_val = float(weight)
    waist_val = float(waist) if waist else None
    bodyfat_val = float(bodyfat) if bodyfat else None
    return m_date, weight_val, waist_val, bodyfat_val


@app.route("/client/<int:client_id>/log_metric", methods=("GET", "POST"))
def log_metric(client_id):
    """
    Log body metrics for a client (weight, waist, body fat).

    GET: Display metrics logging form.
    POST: Process and store metric data, update client's current weight.

    Expected form fields:
        - date: Measurement date (required)
        - weight: Weight in kg (required)
        - waist: Waist circumference in cm (optional)
        - bodyfat: Body fat percentage (optional)

    Args:
        client_id (int): ID of the client.

    Returns:
        str: Rendered form or redirect to client detail on success.
    """
    if request.method == "POST":
        logger.info(f"Logging metrics for client_id={client_id}")

        m_date = request.form.get("date", "").strip()
        weight = request.form.get("weight", "").strip()
        waist = request.form.get("waist", "").strip()
        bodyfat = request.form.get("bodyfat", "").strip()

        try:
            m_date, weight_val, waist_val, bodyfat_val = _validate_and_parse_metric_input(
                m_date, weight, waist, bodyfat
            )

            logger.debug(
                f"Recording metrics: weight={weight_val}kg, waist={waist_val}, "
                f"bodyfat={bodyfat_val}"
            )

            with get_connection() as conn:
                conn.execute(
                    "INSERT INTO metrics (client_id, date, weight, waist, bodyfat) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (client_id, m_date, weight_val, waist_val, bodyfat_val),
                )
                conn.execute(
                    "UPDATE clients SET weight = ? WHERE id = ?",
                    (weight_val, client_id),
                )
                conn.commit()

            logger.info(f"Metrics logged successfully for client_id={client_id}")
            flash("Body metrics logged successfully!", "success")
            return redirect(url_for("client_detail", client_id=client_id))
        except ValueError as e:
            error_msg = str(e) or "Weight, waist, and body fat must be valid numeric values."
            logger.warning(f"Metric validation error for client {client_id}: {error_msg}")
            flash(error_msg, "error")
            return render_template(TEMPL_ADD_METRIC, client_id=client_id, today=date.today()), 400
        except Exception as e:
            logger.error(f"Error logging metrics for client {client_id}: {str(e)}", exc_info=True)
            flash("Error logging metrics.", "error")
            return render_template(TEMPL_ADD_METRIC, client_id=client_id, today=date.today()), 500
            
    return render_template(TEMPL_ADD_METRIC, client_id=client_id, today=date.today())


@app.route("/client/<int:client_id>/generate_program", methods=("GET",))
def generate_program(client_id):
    """
    Generate an AI-style workout program for a client.

    Creates a randomized 3-day workout schedule based on the client's
    training program type (e.g., Fat Loss, Muscle Gain, Beginner).

    Args:
        client_id (int): ID of the client.

    Returns:
        str: Rendered program template or 404 error.
    """
    logger.info(f"Generating program for client_id={client_id}")

    try:
        with get_connection() as conn:
            client = conn.execute(
                "SELECT * FROM clients WHERE id = ?", (client_id,)
            ).fetchone()

        if client is None:
            logger.warning(f"Client not found for program generation: client_id={client_id}")
            return "Client not found", 404

        schedule, focus = generate_program_schedule(client["program"])
        logger.info(f"Generated program for client {client['name']}: focus={focus}")

        return render_template(
            TEMPL_PROGRAM,
            client=client,
            schedule=schedule,
            focus=focus,
        )
    except Exception as e:
        logger.error(f"Error generating program: {str(e)}", exc_info=True)
        flash("Error generating program.", "error")
        return redirect(url_for("index"))


@app.route("/client/<int:client_id>/delete", methods=("POST",))
def delete_client(client_id):
    """
    Delete a client and all associated data (workouts, metrics).

    WARNING: This action cannot be undone and will permanently remove all
    associated data (workouts, metrics, progress) for the client.

    Args:
        client_id (int): ID of the client to delete.

    Returns:
        str: Redirect to index after deletion.
    """
    logger.warning(f"Deleting client_id={client_id} - ALL associated data will be removed")

    try:
        with get_connection() as conn:
            client_name = conn.execute(
                "SELECT name FROM clients WHERE id = ?", (client_id,)
            ).fetchone()

            conn.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            conn.commit()

        logger.info(f"Client deleted successfully: {client_name['name'] if client_name else 'Unknown'}")
        flash("Client deleted successfully!", "success")
    except Exception as e:
        logger.error(f"Error deleting client: {str(e)}", exc_info=True)
        flash("Error deleting client.", "error")

    return redirect(url_for("index"))


# Error handlers
@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.path}")
    return render_template(TEMPL_ERROR, error_code=404, message="Page not found"), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    logger.error(f"500 error: {str(error)}", exc_info=True)
    return render_template(
        TEMPL_ERROR,
        error_code=500,
        message="Internal server error. Please try again later.",
    ), 500


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Starting ACEest Fitness Gym Application")
    logger.info(f"Version: {APP_VERSION}")
    logger.info(f"Database: {DB_NAME}")
    logger.info("=" * 60)

    # Initialize database on startup
    init_db(DB_NAME)

    print("\n" + "-" * 60)
    print("✓ ACEest Fitness Gym is running!")
    print(f"✓ Version: {APP_VERSION}")
    print("✓ Local Access:  http://127.0.0.1:5000")
    print("✓ Network Access: http://<your_ip>:5000")
    print("-" * 60 + "\n")

    app.run(debug=app.config['DEBUG'], port=5000, host="0.0.0.0")
