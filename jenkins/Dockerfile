FROM jenkins/jenkins:lts-jdk17
USER root
# Client Docker uniquement (le démon reste celui de Docker Desktop)
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
# kubectl pour déployer sur le cluster kind
RUN ARCH="$(dpkg --print-architecture)" \
 && curl -fsSL -o /usr/local/bin/kubectl "https://dl.k8s.io/release/v1.31.0/bin/linux/${ARCH}/kubectl" \
 && chmod +x /usr/local/bin/kubectl
USER jenkins
