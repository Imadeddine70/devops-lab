# Serveur cible : une "machine" Ubuntu avec SSH, que Ansible va configurer
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-server sudo python3 python3-apt \
 && rm -rf /var/lib/apt/lists/*
# Compte d'administration : connexion par clé uniquement, sudo sans mot de passe
RUN useradd --create-home --shell /bin/bash deploy \
 && echo "deploy ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/deploy \
 && chmod 440 /etc/sudoers.d/deploy
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 22 8080
ENTRYPOINT ["/entrypoint.sh"]
