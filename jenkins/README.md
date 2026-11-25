# Jenkins

```
cd jenkins
docker compose up --build -d
docker compose logs jenkins        # mot de passe administrateur initial
```
Ouvrir http://localhost:8081, installer les plugins suggérés, créer le compte admin.

## Job
New Item, nom `devops-lab`, type Pipeline, « Pipeline script from SCM », Git,
URL du dépôt, branche `*/main`, Script Path `Jenkinsfile`.

## Accès au cluster (étapes 4 et 5)
Jenkins doit pouvoir joindre le cluster kind :
```
kind get kubeconfig --internal --name devops-lab > kubeconfig-ci
docker network connect kind jenkins-lab
```
Puis dans Jenkins : Manage Jenkins, Credentials, (global), Add Credentials, type **Secret file**,
fichier `kubeconfig-ci`, ID **kubeconfig**. Supprimer ensuite `kubeconfig-ci` du disque :
c'est un secret, il ne doit jamais être commité.

## Pourquoi `user: root` et le socket Docker ?
Pour construire des images, Jenkins parle au démon Docker de la machine via son socket. Cela équivaut
à un accès root sur l'hôte : acceptable en lab, à éviter en production (voir `docs/SECURITY.md`).
