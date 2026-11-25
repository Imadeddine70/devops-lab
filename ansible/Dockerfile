# Conteneur "poste de contrôle" Ansible
FROM python:3.12-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends openssh-client \
 && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir ansible-core==2.17.7
# Sur un dossier monté depuis Windows, Ansible ignore ansible.cfg (dossier "world-writable") : on le force
ENV ANSIBLE_CONFIG=/project/ansible/ansible.cfg
WORKDIR /project/ansible
