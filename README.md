# ACEest Fitness Manager

Version: 0.1.0

A modular Flask application built for fitness and gym client management, including client registration, workout logging, body metrics tracking, calorie targeting, and automated program generation.

## Features

- **Client Management**: Add and remove clients, track active memberships, and see client statistics in one dashboard.
- **Automated Calorie Targets**: Calculates calorie goals for Fat Loss, Muscle Gain, and Beginner programs.
- **Workout Logging**: Save workout sessions with type, duration, and notes.
- **Metrics Tracking**: Record body weight, waist measurement, and body fat over time.
- **BMI Calculation**: Displays BMI and category on the client profile.
- **Program Generator**: Produces a sample 3-day workout schedule for each client.
- **Health Endpoint**: Simple `/health` endpoint for monitoring and CI checks.

## Prerequisites

- Python 3.12 or higher
- Docker / Podman for container builds
- Jenkins for CI/CD pipeline execution

## Local Setup

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the application:

```bash
python flask_app.py
```

4. Open the app:

- `http://127.0.0.1:5000`

## Running Tests

Execute the Pytest suite:

```bash
pytest
```

## Docker Usage

Build and run the container:

```bash
docker build -t acetest-fitness-gym-flaskapp:latest .
docker run --rm -p 5000:5000 acetest-fitness-gym-flaskapp:latest
```

Or use Docker Compose:

```bash
docker compose up --build
```

## Jenkins CI Pipeline

The repository includes a `Jenkinsfile` that performs:

- source checkout
- dependency installation
- Docker image build and version tagging
- containerized Pytest execution
- artifact export with `docker save`
- optional SonarQube analysis when `SONAR_TOKEN` is supplied
- Docker Hub push on the `master` branch using credentials

## SonarQube Static Analysis

A `sonar-project.properties` file is included to support static analysis and quality gate enforcement.

## Kubernetes Deployment

Kubernetes manifests are available under `k8s/` for:

- standard deployment and service
- blue-green deployment
- canary release
- rolling updates
- shadow deployment
- A/B testing structure

Apply core resources locally with:

```bash
kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml
```

## Version Control and Release Strategy

- `VERSION` contains the current application release version.
- The Jenkins pipeline uses semantic versioning for Docker tags and build artifacts.
- The repository is organized to support incremental feature branches, automated tests, and deployment artifacts.
