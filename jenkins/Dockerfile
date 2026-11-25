FROM jenkins/jenkins:lts-jdk17
USER root
# Client Docker uniquement (le démon reste celui de Docker Desktop)
COPY --from=docker:27-cli /usr/local/bin/docker /usr/local/bin/docker
USER jenkins
