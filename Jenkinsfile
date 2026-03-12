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
          docker.build("${IMAGE_NAME}:latest", ".")
        }
      }
    }

    stage('Run Unit Tests') {
      steps {
        script {
          docker.image("${IMAGE_NAME}:latest").inside {
            sh 'pytest'
          }
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
