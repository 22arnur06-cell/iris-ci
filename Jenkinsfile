pipeline {
    agent any

    environment {
        IMAGE = 'iris-ci'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Unit tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    pytest -v
                '''
            }
        }

        stage('Build Docker image') {
            steps {
                sh 'docker build -t ${IMAGE}:${BUILD_NUMBER} -t ${IMAGE}:latest .'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    sh '''
                        set +x
                        export DOCKER_CONFIG="$(mktemp -d)"
                        cleanup() {
                            result=$?
                            if ! docker logout; then
                                echo 'Docker logout failed'
                                result=1
                            fi
                            if [ -f "$DOCKER_CONFIG/config.json" ]; then
                                if ! rm -f "$DOCKER_CONFIG/config.json"; then
                                    echo 'Failed to remove temporary Docker credentials'
                                    result=1
                                fi
                            fi
                            if ! rmdir "$DOCKER_CONFIG"; then
                                echo 'Failed to remove temporary Docker config directory'
                                result=1
                            fi
                            exit "$result"
                        }
                        trap cleanup EXIT
                        printf '%s' "$DH_PASS" | docker login --username "$DH_USER" --password-stdin
                        docker tag "${IMAGE}:${BUILD_NUMBER}" "${DH_USER}/${IMAGE}:${BUILD_NUMBER}"
                        docker tag "${IMAGE}:latest" "${DH_USER}/${IMAGE}:latest"
                        docker push "${DH_USER}/${IMAGE}:${BUILD_NUMBER}"
                        docker push "${DH_USER}/${IMAGE}:latest"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline finished successfully'
        }
        failure {
            echo 'Pipeline failed'
        }
    }
}
