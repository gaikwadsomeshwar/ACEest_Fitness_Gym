pipeline {
  agent any
  stages {
    stage('Build & Test') {
      steps {
        sh 'python3 -m venv venv'
        sh './venv/bin/pip install -r requirements.txt'
        sh './venv/bin/pytest test_app.py'
      }
    }
    stage('Run Flask App') {
      steps {
        // Background process example
        sh 'nohup ./venv/bin/python flask_app.py > flask.log 2>&1 &'
      }
    }
    stage('Create docker image') {
      steps {
        sh 'docker build -t flask-app:latest .'
      }
    }
  }
}
