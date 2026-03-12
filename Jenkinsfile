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
          docker.build("${IMAGE_NAME}:latest", ".")
        }
      }
    }

    stage('Run Unit Tests') {
      steps {
        script {
          // Run unit tests using pytest
          powershell 'docker run --rm ${IMAGE_NAME}:latest pytest'
        }
      }
    }

    stage ('Remove docker image') {
      steps {
        script {
          // Remove the Docker image to free up space
          docker.rmi("${IMAGE_NAME}:latest")
        }
      }
    }

    stage('Login and Push Image to Docker Hub') {
      steps {
        script {
          // Login to Docker Hub and push the image
          docker.withRegistry('https://hub.docker.com', DOCKER_HUB_CRED_ID) {
            docker.build('${USERNAME}/${IMAGE_NAME}', '.').push("latest")
          }
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
