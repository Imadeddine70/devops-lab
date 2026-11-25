# devops-lab

Projet d'apprentissage DevOps : un petit service web déployé avec une chaîne complète
Docker, Jenkins, Ansible, Kubernetes et supervision, avec une attention particulière à la sécurité.
L'application est volontairement minimale : l'infrastructure est le sujet.

## Avancement

| Étape | Contenu | Dossier |
|---|---|---|
| 1 | Docker : image multi-stage, non-root, compose durci | `Dockerfile`, `compose.yml` |
| 2 | Jenkins : pipeline CI (lint, tests, build, scan Trivy, test de fumée) | `Jenkinsfile`, `jenkins/` |
| 3 | Ansible : provisionnement reproductible et durcissement SSH | `ansible/` |
| 4 | Kubernetes (kind) : déploiement, probes, autoscaling, NetworkPolicy | `k8s/`, `kind/` |
| 5 | Déploiement continu : Jenkins déploie sur Kubernetes | `Jenkinsfile` |
| 6 | Supervision : Prometheus et Grafana | `monitoring/` |
| 7 | Sécurité transverse et limites connues | `docs/SECURITY.md` |

## Résultats vérifiés

| Test | Résultat |
|---|---|
| Image Docker | exécutée en uid 10001 (non-root), healthcheck OK |
| Pipeline Jenkins | lint, tests, build, scan Trivy de l'image (0 CRITICAL), scan des manifests, test de fumée, déploiement : tous verts |
| Déploiement Kubernetes | 2 pods `Running`, rollout sans interruption |
| Autoscaling | sous charge, CPU à 329 % de l'objectif : passage de 2 à 5 pods, puis retour à 2 après la fenêtre de stabilisation de 5 minutes |
| Supervision | Prometheus collecte les 2 pods, dashboard Grafana provisionné par fichier |
| Ansible | serveur configuré, application joignable ; connexion SSH root refusée (`Permission denied (publickey)`), utilisateur `deploy` accepté |

## Vue d'ensemble

```
git push -> Jenkins -> lint + tests -> build -> scan Trivy -> test de fumée
                                                      |
                                    import dans le cluster kind
                                                      |
                              kubectl apply -> Deployment (2 pods) -> Service
                                                      |
                              Prometheus (scrape /metrics) -> Grafana
```

## Ordre de mise en route

1. **Docker** : `docker compose up --build -d` puis `curl http://localhost:8080/health`
2. **Jenkins** : voir `jenkins/README.md`
3. **Ansible** : voir `ansible/README.md`
4. **Cluster** : voir `kind/README.md`
5. **Déploiement par Jenkins** : voir `jenkins/README.md`
6. **Supervision** : voir `monitoring/README.md`

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
