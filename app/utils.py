"""
Utility functions for ACEest Fitness Gym application.

Contains business logic for calorie calculations, BMI calculations,
program generation, and other helper functions.
"""

import random
import re
from typing import Any
from logging_config import logger

# Program definitions with calorie factors based on program type
PROGRAMS = {
    "Fat Loss (FL)": {
        "factor": 22,
        "desc": "High intensity, calorie deficit focus"
    },
    "Muscle Gain (MG)": {
        "factor": 35,
        "desc": "Hypertrophy, surplus focus"
    },
    "Beginner (BG)": {
        "factor": 26,
        "desc": "Technique mastery, maintenance"
    }
}

# Training focus constants
FOCUS_STRENGTH = "Strength"
FOCUS_HYPERTROPHY = "Hypertrophy"
FOCUS_CONDITIONING = "Conditioning"
FOCUS_FULL_BODY = "Full Body"


def calculate_calories(weight: float, program: str) -> int:
    """
    Calculate daily calorie target based on client weight and program type.

    Formula: weight_kg * program_factor

    Args:
        weight (float): Client weight in kilograms.
        program (str): Program type (key from PROGRAMS dict).

    Returns:
        int: Daily calorie target.

    Raises:
        KeyError: If program type not found in PROGRAMS.
    """
    try:
        factor = PROGRAMS[program]["factor"]
        calories = int(weight * factor)
        logger.debug(
            f"Calculated calories for {program}: {weight}kg * {factor} = {calories} kcal"
        )
        return calories
    except KeyError as e:
        logger.error(f"Invalid program type: {program}")
        raise ValueError(f"Program '{program}' not found") from e


def calculate_target_weight(weight: float, program: str) -> float:
    """
    Calculate target weight based on program type.

    - Fat Loss: 95% of current weight
    - Muscle Gain: 105% of current weight
    - Beginner: maintain current weight

    Args:
        weight (float): Current weight in kilograms.
        program (str): Program type.

    Returns:
        float: Target weight in kilograms (rounded to 1 decimal).
    """
    if "Fat Loss" in program:
        target = round(weight * 0.95, 1)
        logger.debug(f"Fat Loss target: {weight}kg -> {target}kg")
        return target
    if "Muscle Gain" in program:
        target = round(weight * 1.05, 1)
        logger.debug(f"Muscle Gain target: {weight}kg -> {target}kg")
        return target
    logger.debug(f"Maintenance target: {weight}kg")
    return round(weight, 1)


def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculate Body Mass Index.

    Formula: BMI = weight_kg / (height_m)^2

    Args:
        weight (float): Weight in kilograms.
        height (float): Height in centimeters.

    Returns:
        float: BMI value (rounded to 1 decimal).

    Raises:
        ValueError: If height is zero or negative.
    """
    if height <= 0:
        logger.error(f"Invalid height value: {height}")
        raise ValueError("Height must be greater than 0")

    height_m = height / 100.0
    bmi = round(weight / (height_m ** 2), 1)
    logger.debug(f"Calculated BMI: {weight}kg / {height}cm = {bmi}")
    return bmi


def bmi_category(bmi: float) -> str:
    """
    Get BMI category based on BMI value.

    WHO categories:
    - < 18.5: Underweight
    - 18.5-24.9: Normal
    - 25-29.9: Overweight
    - >= 30: Obese

    Args:
        bmi (float): BMI value.

    Returns:
        str: BMI category name.
    """
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"

    logger.debug(f"BMI {bmi} categorized as: {category}")
    return category


def generate_program_schedule(
    program_name: str,
) -> tuple[dict[str, list[dict[str, Any]]], str]:
    """
    Generate a randomized 3-day workout schedule based on program type.

    Selects 4 exercises per day from a pool of exercises appropriate
    for the program type (e.g., conditioning for fat loss, hypertrophy for muscle gain).

    Args:
        program_name (str): Program type name.

    Returns:
        tuple: (schedule dict with days and exercises, focus area string)
               schedule format: {"Monday": [...], "Wednesday": [...], "Friday": [...]}

    Example:
        >>> schedule, focus = generate_program_schedule("Fat Loss (FL)")
        >>> schedule["Monday"]
        [{"name": "Running", "sets": 3, "reps": 12}, ...]
    """
    # Exercise pools organized by training focus
    exercises_pool = {
        FOCUS_STRENGTH: [
            "Squat",
            "Deadlift",
            "Bench Press",
            "Overhead Press",
            "Pull-Up",
            "Barbell Row",
        ],
        FOCUS_HYPERTROPHY: [
            "Leg Press",
            "Incline Dumbbell Press",
            "Lat Pulldown",
            "Lateral Raise",
            "Bicep Curl",
            "Tricep Extension",
        ],
        FOCUS_CONDITIONING: [
            "Running",
            "Cycling",
            "Rowing",
            "Burpees",
            "Jump Rope",
            "Kettlebell Swings",
        ],
        FOCUS_FULL_BODY: [
            "Push-Up",
            "Pull-Up",
            "Lunge",
            "Plank",
            "Dumbbell Row",
            "Dumbbell Press",
        ],
    }

    # Determine focus area based on program type
    focus = FOCUS_FULL_BODY  # default
    if "Fat Loss" in program_name:
        focus = FOCUS_CONDITIONING
        logger.debug("Fat Loss program - using Conditioning focus")
    elif "Muscle Gain" in program_name:
        focus = FOCUS_HYPERTROPHY
        logger.debug("Muscle Gain program - using Hypertrophy focus")
    elif "Beginner" in program_name:
        logger.debug("Beginner program - using Full Body focus")

    # Build schedule for 3 training days
    schedule: dict[str, list[dict[str, Any]]] = {}
    days = ["Monday", "Wednesday", "Friday"]
    pool = exercises_pool.get(focus, []) + exercises_pool[FOCUS_STRENGTH]
    sample_count = min(4, len(pool))  # Select up to 4 exercises

    for day in days:
        selected = random.sample(pool, k=sample_count)
        schedule[day] = [
            {
                "name": ex,
                "sets": random.randint(3, 4),
                "reps": random.randint(8, 12),
            }
            for ex in selected
        ]
        logger.debug(f"Generated {day} schedule: {selected}")

    return schedule, focus


def format_phone_number(phone: str) -> str:
    """
    Format phone number to standard format.

    Args:
        phone (str): Raw phone number.

    Returns:
        str: Formatted phone number.
    """
    digits = "".join(filter(str.isdigit, phone))
    if len(digits) == 10:
        return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"
    return phone


def validate_email(email: str) -> bool:
    """
    Basic email validation.

    Args:
        email (str): Email address to validate.

    Returns:
        bool: True if email format is valid.
    """
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None
