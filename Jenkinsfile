pipeline {
    agent any

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    environment {
        IMAGE        = "devops-lab:${env.BUILD_NUMBER}"
        KIND_NODE    = "devops-lab-control-plane"
        K8S_NS       = "devops-lab"
        TRIVY_IMAGE  = "aquasec/trivy:0.58.0"
    }

    stages {
        stage('Lint et tests') {
            steps {
                // L'étape "test" du Dockerfile lance flake8 puis pytest.
                sh 'docker build --target test -t devops-lab-test:${BUILD_NUMBER} .'
            }
        }

        stage('Build de l image') {
            steps {
                sh 'docker build -t ${IMAGE} .'
            }
        }

        stage('Scan de l image (Trivy)') {
            steps {
                // Échoue s'il reste une vulnérabilité CRITICAL pour laquelle un correctif existe.
                sh '''
                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      -v trivy-cache:/root/.cache \
                      ${TRIVY_IMAGE} image \
                      --severity CRITICAL --ignore-unfixed --exit-code 1 \
                      ${IMAGE}
                '''
            }
        }

        stage('Scan des manifests Kubernetes (Trivy)') {
            steps {
                // --volumes-from : le conteneur Trivy voit le même espace de travail que Jenkins.
                sh '''
                    docker run --rm --volumes-from jenkins-lab \
                      -v trivy-cache:/root/.cache \
                      ${TRIVY_IMAGE} config \
                      --severity HIGH,CRITICAL --exit-code 1 \
                      ${WORKSPACE}/k8s
                '''
            }
        }

        stage('Test de fumée') {
            steps {
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

        stage('Chargement de l image dans le cluster') {
            steps {
                // Le cluster kind n'a pas accès à nos images locales : on l'importe dans son containerd.
                sh 'docker save ${IMAGE} | docker exec -i ${KIND_NODE} ctr -n k8s.io images import -'
            }
        }

        stage('Déploiement Kubernetes') {
            steps {
                withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                    sh '''
                        rm -rf .k8s-render && cp -r k8s .k8s-render
                        sed -i "s|image: devops-lab:dev|image: ${IMAGE}|" .k8s-render/20-deployment.yaml
                        kubectl apply -f .k8s-render/
                        kubectl -n ${K8S_NS} rollout status deployment/devops-lab --timeout=120s
                        kubectl -n ${K8S_NS} get pods -o wide
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker rm -f smoke-${BUILD_NUMBER} || true'
        }
        success {
            echo "Déployé : ${IMAGE} sur http://localhost:8082"
        }
        failure {
            script {
                try {
                    withCredentials([file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')]) {
                        sh 'kubectl -n ${K8S_NS} get pods || true'
                    }
                } catch (err) {
                    echo "Diagnostic Kubernetes indisponible : ${err.message}"
                }
            }
        }
    }
}
