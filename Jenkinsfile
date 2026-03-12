pipeline {
  agent any
  environment {
    IMAGE_NAME = 'someshwargaikwad/acetest-fitness-gym-flaskapp'
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

    stage('Login and Push Image to Docker Hub') {
      steps {
        script {
          docker.withRegistry('https://registry.hub.docker.com', DOCKER_HUB_CRED_ID) {
            dockerImage.push('latest')
          }
        }
      }
    }

    stage('Clean up') {
        steps {
            sh "docker rmi ${IMAGE_NAME}:${env.BUILD_NUMBER}"
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
