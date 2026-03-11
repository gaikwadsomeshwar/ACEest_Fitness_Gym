pipeline {
  agent any
  environment {
    // Define variables for Docker Hub username/repo and credential ID
    DOCKERHUB_REPO = 'someshwargaikwad/acetest-fitness-gym-flaskapp' // e.g., myuser/my-app
    DOCKER_CRED_ID = 'dockerhub-cred' // The ID you set in Jenkins credentials
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

    stage('Build Image') {
      steps {
        script {
          // Build the image using the Dockerfile in the current directory, tagging with the build number
          dockerImage = docker.build("${DOCKERHUB_REPO}:${env.BUILD_NUMBER}")
          // Tag the image with 'latest' as well
          dockerImage.tag('latest')
        }
      }
    }
        stage('Push Image') {
      steps {
        script {
          // Use withRegistry to log in and push the images securely
          docker.withRegistry("https://hub.docker.com/repository/docker/${DOCKERHUB_REPO}", DOCKER_CRED_ID) {
            dockerImage.push("${env.BUILD_NUMBER}")
            dockerImage.push('latest')
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
