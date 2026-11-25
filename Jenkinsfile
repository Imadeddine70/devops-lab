pipeline {
    agent any

    options {
        timeout(time: 20, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        IMAGE = "devops-lab:${env.BUILD_NUMBER}"
    }

    stages {
        stage('Lint et tests') {
            steps {
                // L'étape "test" du Dockerfile lance flake8 puis pytest.
                // Si l'un des deux échoue, le build s'arrête ici.
                sh 'docker build --target test -t devops-lab-test:${BUILD_NUMBER} .'
            }
        }

        stage('Build de l image') {
            steps {
                sh 'docker build -t ${IMAGE} .'
            }
        }

        stage('Scan de vulnérabilités (Trivy)') {
            steps {
                // Échoue s'il reste une vulnérabilité CRITICAL pour laquelle un correctif existe.
                sh '''
                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v trivy-cache:/root/.cache \
                      aquasec/trivy:0.58.0 image \
                      --severity CRITICAL --ignore-unfixed --exit-code 1 \
                      ${IMAGE}
                '''
            }
        }

        stage('Test de fumée') {
            steps {
                // Lance l'image, attend qu'elle réponde sur /health, puis la supprime.
                sh '''
                    docker run -d --name smoke-${BUILD_NUMBER} ${IMAGE}
                    for i in $(seq 1 15); do
                      if docker exec smoke-${BUILD_NUMBER} python -c \
                        "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2).status==200 else 1)"; then
                        echo "Service OK"; exit 0
                      fi
                      sleep 2
                    done
                    echo "Le service ne répond pas"; docker logs smoke-${BUILD_NUMBER}; exit 1
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rm -f smoke-${BUILD_NUMBER} || true'
        }
        success {
            echo "Pipeline réussi : image ${IMAGE}"
        }
    }
}
