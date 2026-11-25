# devops-lab

Projet d'apprentissage DevOps : un petit service web déployé avec une chaîne complète
Docker, Jenkins, Ansible, Kubernetes et supervision, avec une attention particulière à la sécurité.
L'application est volontairement minimale : l'infrastructure est le sujet.

## Avancement

| Étape | Contenu | État |
|---|---|---|
| 1 | Docker : image multi-stage, non-root, compose durci | fait |
| 2 | Jenkins : pipeline CI (lint, tests, build, scan) | à venir |
| 3 | Ansible : provisionnement reproductible | à venir |
| 4 | Kubernetes (kind) : Deployment, Service, probes, HPA | à venir |
| 5 | Déploiement continu Jenkins vers Kubernetes | à venir |
| 6 | Prometheus et Grafana | à venir |
| 7 | Durcissement : Trivy, NetworkPolicy, secrets | à venir |

## L'application

API Flask servie par gunicorn.

| Route | Rôle |
|---|---|
| `/` | statut du service |
| `/health` | sonde de santé (utilisée par Docker puis Kubernetes) |
| `/api/info` | version et environnement, lus dans des variables d'environnement |
| `/metrics` | métriques au format Prometheus |

Tests : `pip install -r requirements-dev.txt && pytest`

## Étape 1 : Docker

```
docker compose up --build -d
curl http://localhost:8080/health
docker exec devops-lab-web-1 id      # uid=10001, donc pas root
docker compose down
```

Choix de conception :

- **Build en deux étapes** : les dépendances s'installent dans une étape jetable, l'image finale ne contient que le nécessaire.
- **Utilisateur non-root** (uid 10001) : une compromission de l'application ne donne pas les droits root dans le conteneur.
- **Durcissement dans `compose.yml`** : système de fichiers en lecture seule (seul `/tmp` est inscriptible, en mémoire), toutes les capacités Linux retirées, `no-new-privileges`.
- **Healthcheck** intégré à l'image.
- **Un seul worker gunicorn** (avec des threads) : les compteurs de `/metrics` vivent en mémoire, plusieurs workers donneraient chacun des valeurs différentes.

## Ce que j'ai appris en route

- Avec un système de fichiers en lecture seule, gunicorn plantait en boucle (`restarting`) faute de `/tmp` inscriptible. Corrigé avec un `tmpfs`.
- Des métriques en mémoire ne sont cohérentes qu'avec un seul processus.
