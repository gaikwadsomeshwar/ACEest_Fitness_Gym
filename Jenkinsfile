pipeline {
  agent any
  environment {
    // Define variables for Docker Hub username/repo and credential ID
    DOCKERHUB_REG = 'hub.docker.com'
    DOCKER_USERNAME = 'someshwargaikwad'
    DOCKER_CRED_ID = 'dockerhub-cred'
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

    stage('Push DockerImage') {
      steps {
        script {
          powershell 'echo ${env.DOCKER_CRED_ID} | docker login --username ${env.DOCKER_USERNAME} --password-stdin ${env.DOCKERHUB_REG}'
          powershell 'docker push ${env.DOCKERHUB_USERNAME}/acetest-fitness-gym-flaskapp:latest'
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
