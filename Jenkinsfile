pipeline {
  agent any

  stages {
    stage('Checkout Code') {
      steps {
        checkout scm
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          // Build the Docker image and tag it
          powershell 'docker build -t acetest-fitness-gym-flaskapp:latest .'
        }
      }
    }

    stage('Run Unit Tests') {
      steps {
        script {
          // Run pytest within a new container from the built image
          // The --rm flag automatically removes the container after tests finish
          powershell 'docker run --rm acetest-fitness-gym-flaskapp:latest pytest'
        }
      }
    }

    stage('Deploy Application') {
      steps {
        script {
          // Stop any existing container and run a new one in detached mode
          powershell 'docker stop acetest-fitness-gym-flaskapp; if ($?) { $true }'
          powershell 'docker rm acetest-fitness-gym-flaskapp; if ($?) { $true }'
          powershell 'docker run -d --name acetest-fitness-gym-flaskapp -p 5000:5000 acetest-fitness-gym-flaskapp:latest'
        }
      }
    }
  }

  post {
      success {
        echo 'Pipeline executed successfully'
      }
      failure {
        echo 'Pipeline failed. Check logs for details.'
    }
  }
}
