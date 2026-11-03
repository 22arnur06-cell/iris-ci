pipeline {
    agent any

    environment {
        IMAGE = 'iris-ci'
        KUBECTL_VERSION = 'v1.37.0'
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

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([
                    file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG'),
                    usernamePassword(credentialsId: 'dockerhub-creds',
                        usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')
                ]) {
                    sh '''
                        set -eu

                        JOB_NAME="iris-ci-job-${BUILD_NUMBER}"
                        IMAGE_REF="${DH_USER}/${IMAGE}:${BUILD_NUMBER}"
                        KUBECTL_PATH="${WORKSPACE}/.tools/kubectl"

                        if command -v kubectl >/dev/null 2>&1; then
                            KUBECTL="$(command -v kubectl)"
                        else
                            mkdir -p "${WORKSPACE}/.tools"
                            curl -fsSLo "$KUBECTL_PATH" \
                                "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl"
                            curl -fsSLo "${KUBECTL_PATH}.sha256" \
                                "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/amd64/kubectl.sha256"
                            printf '%s  %s\n' "$(cat "${KUBECTL_PATH}.sha256")" \
                                "$KUBECTL_PATH" | sha256sum --check --status
                            rm "${KUBECTL_PATH}.sha256"
                            chmod +x "$KUBECTL_PATH"
                            KUBECTL="$KUBECTL_PATH"
                        fi

                        sed \
                            -e "s/^  name: .*/  name: ${JOB_NAME}/" \
                            -e "s|image: .*|image: ${IMAGE_REF}|" \
                            k8s/job.yaml | "$KUBECTL" apply -f -

                        "$KUBECTL" wait --for=condition=complete \
                            --timeout=10m "job/${JOB_NAME}"
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
