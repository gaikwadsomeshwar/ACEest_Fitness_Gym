pipeline {
  agent any
  environment {
    IMAGE_NAME = 'acetest-fitness-gym-flaskapp'
    DOCKER_HUB_CRED_ID = 'dockerhub-cred'
  }

  stages {
    stage('Checkout Code') {
      steps {
        checkout scm
      }
    }

    stage('Install Dependencies') {
      steps {
        sh 'python -m pip install --upgrade pip; pip install -r requirements.txt'
      }
    }

    stage('Build Docker Image') {
      steps {
        script {
          def version = readFile('VERSION').trim()
          sh "docker build -t ${IMAGE_NAME}:${version} -t ${IMAGE_NAME}:latest ."
        }
      }
    }

    stage('Run Unit Tests') {
      steps {
        script {
          def version = readFile('VERSION').trim()
          sh "docker run --rm ${IMAGE_NAME}:${version} pytest --maxfail=1 -q"
        }
      }
    }

    stage('Build Artifact') {
      steps {
        script {
          def version = readFile('VERSION').trim()
          sh 'New-Item -ItemType Directory -Path build -Force | Out-Null'
          sh "docker save ${IMAGE_NAME}:${version} -o build/${IMAGE_NAME}_${version}.tar"
        }
      }
    }

    stage('Static Analysis') {
      when {
        expression { return env.SONAR_TOKEN != null && env.SONAR_TOKEN != '' }
      }
      steps {
        script {
          sh 'sonar-scanner -Dsonar.login=$env:SONAR_TOKEN'
        }
      }
    }

    stage('Publish Docker Image') {
      when {
        branch 'master'
      }
      steps {
        script {
          withCredentials([usernamePassword(credentialsId: env.DOCKER_HUB_CRED_ID, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
            def version = readFile('VERSION').trim()
            sh 'docker login -u $env:DOCKER_USERNAME -p $env:DOCKER_PASSWORD'
            sh "docker tag ${IMAGE_NAME}:${version} ${DOCKER_USERNAME}/${IMAGE_NAME}:${version}"
            sh "docker tag ${IMAGE_NAME}:${version} ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
            sh "docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:${version}"
            sh "docker push ${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
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
