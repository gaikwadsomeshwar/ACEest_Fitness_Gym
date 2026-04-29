# ACEest Fitness Gym - Code Structure and Architecture

## Overview

ACEest Fitness Gym is a modular Flask-based web application for managing fitness gym clients, workouts, metrics, and personalized training programs.

**Version:** 0.1.0  
**Framework:** Flask 3.0.3  
**Database:** SQLite  
**Python:** 3.12+

## Project Structure

```
ACEest_Fitness_Gym/
├── app/
│   ├── __init__.py              # Package initializer
│   ├── database.py              # Database utilities (connection, init, migrations)
│   ├── utils.py                 # Business logic (calculations, program generation)
│   └── templates/               # HTML templates for the web interface
│       ├── index.html
│       ├── add_client.html
│       ├── client_detail.html
│       ├── add_workout.html
│       ├── add_metric.html
│       └── generated_program.html
│
├── config.py                    # Configuration management (environments)
├── logging_config.py            # Logging setup and configuration
├── flask_app.py                 # Main Flask application and routes
├── test_app.py                  # Unit tests with pytest
├── requirements.txt             # Python dependencies
├── VERSION                      # Application version
├── Dockerfile                   # Docker containerization
├── docker-compose.yml           # Docker Compose configuration
├── Jenkinsfile                  # CI/CD pipeline
├── sonar-project.properties     # SonarQube configuration
├── pytest.ini                   # Pytest configuration
├── README.md                    # User documentation
└── ARCHITECTURE.md              # This file

k8s/                             # Kubernetes deployment manifests
├── deployment.yaml              # Standard deployment
├── service.yaml                 # Service configuration
├── blue-green.yaml              # Blue-green deployment strategy
├── canary.yaml                  # Canary deployment strategy
├── rolling-update.yaml          # Rolling update strategy
├── shadow-deployment.yaml       # Shadow deployment for testing
└── ab-testing.yaml              # A/B testing configuration
```

## Core Modules

### config.py

Manages application configuration for different environments.

**Classes:**

- `Config` - Base configuration
- `DevelopmentConfig` - Development settings
- `ProductionConfig` - Production settings
- `TestingConfig` - Test settings

**Key Features:**

- Environment-based config selection
- Secret key management
- Database URI configuration
- Session configuration
- File upload settings

### logging_config.py

Sets up structured logging with file and console handlers.

**Key Features:**

- Rotating file handlers (10 MB max per file)
- Separate error logs
- Console output for development
- ISO 8601 timestamp formatting
- Logs stored in `logs/` directory

**Log Files:**

- `logs/app.log` - Application events
- `logs/error.log` - Error-level logs only

### app/database.py

Database utilities and schema management.

**Functions:**

- `get_db_connection(db_name)` - Get database connection
- `init_db(db_name)` - Initialize database schema
- `drop_all_tables(db_name)` - Drop all tables (for testing)

**Tables:**

- `users` - User authentication and roles
- `clients` - Client information
- `workouts` - Workout session logs
- `metrics` - Body measurements (weight, waist, body fat)
- `progress` - Weekly adherence tracking

### app/utils.py

Business logic and utility functions.

**Constants:**

- `PROGRAMS` - Training program definitions with calorie factors
- `EXERCISES_POOL` - Exercise pools organized by training focus

**Functions:**

- `calculate_calories(weight, program)` - Daily calorie target
- `calculate_target_weight(weight, program)` - Goal weight calculation
- `calculate_bmi(weight, height)` - Body Mass Index
- `bmi_category(bmi)` - BMI categorization
- `generate_program_schedule(program_name)` - AI workout schedule generation
- `validate_email(email)` - Email validation
- `format_phone_number(phone)` - Phone number formatting

### flask_app.py

Main Flask application and route handlers.

**Routes:**

- `GET  /` - Dashboard with client list and search
- `GET  /health` - Health check endpoint
- `GET|POST /add_client` - Add new client
- `GET  /client/<id>` - Client detail page
- `GET|POST /client/<id>/log_workout` - Log workout
- `GET|POST /client/<id>/log_metric` - Log metrics
- `GET  /client/<id>/generate_program` - Generate AI program
- `POST /client/<id>/delete` - Delete client
- `404` - Page not found
- `500` - Server error

**Features:**

- Comprehensive logging throughout
- Input validation with error messages
- Transaction-safe database operations
- Graceful error handling
- Flash messages for user feedback

## Database Schema

### users table

```sql
id INTEGER PRIMARY KEY
username TEXT UNIQUE NOT NULL
email TEXT UNIQUE
password_hash TEXT NOT NULL
role TEXT DEFAULT 'trainer'
created_at TEXT DEFAULT CURRENT_TIMESTAMP
is_active INTEGER DEFAULT 1
```

### clients table

```sql
id INTEGER PRIMARY KEY
name TEXT UNIQUE NOT NULL
age INTEGER
height REAL
weight REAL
program TEXT
calories INTEGER
target_weight REAL
target_adherence INTEGER
membership_status TEXT DEFAULT 'Active'
membership_end TEXT
created_at TEXT DEFAULT CURRENT_TIMESTAMP
created_by_user_id INTEGER
```

### workouts table

```sql
id INTEGER PRIMARY KEY
client_id INTEGER NOT NULL
date TEXT NOT NULL
workout_type TEXT
duration_min INTEGER
notes TEXT
created_at TEXT DEFAULT CURRENT_TIMESTAMP
FOREIGN KEY(client_id) REFERENCES clients(id)
```

### metrics table

```sql
id INTEGER PRIMARY KEY
client_id INTEGER NOT NULL
date TEXT NOT NULL
weight REAL
waist REAL
bodyfat REAL
created_at TEXT DEFAULT CURRENT_TIMESTAMP
FOREIGN KEY(client_id) REFERENCES clients(id)
```

### progress table

```sql
id INTEGER PRIMARY KEY
client_id INTEGER NOT NULL
week TEXT NOT NULL
adherence INTEGER
notes TEXT
created_at TEXT DEFAULT CURRENT_TIMESTAMP
FOREIGN KEY(client_id) REFERENCES clients(id)
```

## Business Logic

### Calorie Calculation

Daily calorie targets are calculated based on client weight and program:

- **Fat Loss (FL)**: weight × 22
- **Muscle Gain (MG)**: weight × 35
- **Beginner (BG)**: weight × 26

### Target Weight Calculation

Based on program type:

- **Fat Loss**: Current weight × 0.95 (5% reduction)
- **Muscle Gain**: Current weight × 1.05 (5% gain)
- **Beginner**: Maintain current weight

### BMI Calculation

Formula: BMI = weight_kg / (height_m)²

Categories:

- Underweight: < 18.5
- Normal: 18.5-24.9
- Overweight: 25-29.9
- Obese: ≥ 30

### Program Generation

Generates randomized 3-day workout schedules:

- **Fat Loss**: Focuses on Conditioning exercises
- **Muscle Gain**: Focuses on Hypertrophy exercises
- **Beginner**: Full Body exercises

Each day includes 4 randomly selected exercises with 3-4 sets and 8-12 reps.

## Testing

Run tests with:

```bash
pytest                           # Run all tests
pytest -v                        # Verbose output
pytest --cov                     # With coverage
pytest --maxfail=1              # Stop on first failure
```

**Test Coverage:**

- Index/dashboard page loading
- Health check endpoint
- Client creation and validation
- Calorie calculation
- Client search
- Workout logging
- Metric tracking
- Program generation
- Duplicate client handling
- Input validation

## Logging

Logging is configured in `logging_config.py` and used throughout the application.

**Log Levels:**

- `DEBUG` - Detailed debugging information
- `INFO` - General informational messages
- `WARNING` - Warning messages for potentially problematic situations
- `ERROR` - Error messages with full exception traces

**Example Log Messages:**

```
2024-04-29 10:15:30 - aceest - INFO - Flask app initialized: development mode, v0.1.0
2024-04-29 10:15:32 - aceest - INFO - Accessing index/dashboard page
2024-04-29 10:15:33 - aceest - INFO - Attempting to add new client
2024-04-29 10:15:33 - aceest - DEBUG - Adding client: name=John Doe, weight=75.0, program=Fat Loss (FL), calories=1650
2024-04-29 10:15:33 - aceest - INFO - Successfully added client: John Doe
```

## Configuration

### Environment Variables

```bash
FLASK_ENV=development          # development, production, testing
FLASK_DEBUG=1                  # Enable debug mode
FLASK_SECRET_KEY=your_secret   # Secret key for sessions
ACEEST_DB=aceest_fitness.db    # Database file path
```

### Configuration Classes

**Development:**

- DEBUG = True
- SESSION_COOKIE_SECURE = False
- TESTING = False

**Production:**

- DEBUG = False
- SESSION_COOKIE_SECURE = True
- TESTING = False

**Testing:**

- TESTING = True
- DATABASE = test_database.db
- WTF_CSRF_ENABLED = False

## Best Practices Implemented

1. **Modular Structure** - Separation of concerns with dedicated modules
2. **Comprehensive Logging** - All operations logged for debugging and monitoring
3. **Input Validation** - User input validated before processing
4. **Error Handling** - Try-except blocks with proper error logging
5. **Database Optimization** - Indexes on frequently queried columns
6. **Security** - SQL injection prevention using parameterized queries
7. **Testing** - Unit tests with pytest and coverage tracking
8. **Documentation** - Docstrings on all functions and classes
9. **Code Quality** - Flake8 linting with consistent formatting
10. **Version Management** - VERSION file for semantic versioning

## CI/CD Integration

The Jenkinsfile implements:

- Dependency installation
- Docker image building with version tags
- Containerized test execution
- Build artifact export
- SonarQube static analysis
- Docker Hub publishing

## Deployment

### Docker

```bash
docker build -t acetest-fitness-gym-flaskapp:0.1.0 .
docker run -p 5000:5000 acetest-fitness-gym-flaskapp:0.1.0
```

### Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
```

### Docker Compose

```bash
docker-compose up --build
```

## Error Handling

The application implements graceful error handling:

1. **Database Errors** - Caught and logged with user-friendly messages
2. **Validation Errors** - Pre-submission validation with clear error messages
3. **HTTP Errors** - Custom 404 and 500 error pages
4. **Exceptions** - All exceptions logged with full stack traces

## Performance Considerations

1. **Database Indexes** - Indexes on client name, client-date combinations
2. **Connection Pooling** - Proper connection management
3. **Pagination** - Support for limiting query results
4. **Caching** - Version cached at startup
