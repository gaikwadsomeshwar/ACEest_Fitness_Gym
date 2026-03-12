pipeline {
  agent any
  environment {
    IMAGE_NAME = 'acetest-fitness-gym-flaskapp'
    USERNAME = 'someshwargaikwad'
    DOCKER_HUB_CRED_ID = 'dockerhub-cred'
  }

  stages {
    stage('Checkout Code') {
      steps {
        checkout scm
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          // Build the Docker image using the Dockerfile in the current directory
          powershell 'docker build -t ${IMAGE_NAME}:latest .'
        }
      }
    }

    stage('Run Unit Tests') {
      steps {
        script {
          // Run unit tests inside a temporary container
          powershell 'docker run --rm ${IMAGE_NAME}:latest pytest'
        }
      }
    }

    stage('Login and Push Image to Docker Hub') {
      steps {
        script {
          // Login to Docker Hub and push the image
          docker.withRegistry('https://hub.docker.com', DOCKER_HUB_CRED_ID)
          powershell 'docker push ${USERNAME}/${IMAGE_NAME}:latest'
        }
      }
    }
  }

  post {
      success {
        echo 'Pipeline executed successfully!'
      }
      failure {
        echo 'Pipeline failed. Check logs for details.'
      }
  }
}
