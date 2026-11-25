# Sécurité du projet

Chaque contrôle ci-dessous est **vérifiable** : la commande de test est indiquée.

| Couche | Contrôle | Vérification |
|---|---|---|
| Image | Build multi-stage, image finale sans outils de build | `docker history devops-lab:dev` |
| Image | Utilisateur non-root (uid 10001) | `docker run --rm devops-lab:dev id` |
| Image | Scan Trivy : le pipeline échoue s'il reste une faille CRITICAL corrigeable | étape « Scan de l'image » de Jenkins |
| Conteneur | Système de fichiers en lecture seule, capacités Linux retirées, `no-new-privileges` | `compose.yml` |
| Serveur (Ansible) | SSH : root interdit, mot de passe interdit, 3 essais, utilisateurs autorisés | `ansible-playbook` vérifie `sshd -T` |
| Kubernetes | Pod Security Standards « restricted » imposé sur le namespace | voir test ci-dessous |
| Kubernetes | Pas de jeton de compte de service monté dans les pods | `automountServiceAccountToken: false` |
| Kubernetes | Limites CPU et mémoire, probes de santé | `kubectl -n devops-lab describe pod` |
| Kubernetes | NetworkPolicy : tout refusé en entrée sauf le port 8080 | `k8s/50-networkpolicy.yaml` |
| Kubernetes | Scan Trivy des manifests (HIGH et CRITICAL) | étape « Scan des manifests » de Jenkins |
| Secrets | Mot de passe Grafana créé à la main, jamais dans git | `kubectl -n monitoring get secret grafana-admin` |
| RBAC | Prometheus n'a que le droit de lire les pods | `monitoring/10-prometheus.yaml` |

## Test : le cluster refuse un pod dangereux

```
kubectl -n devops-lab run intrus --image=busybox:1.36 --privileged -- sleep 3600
```

Résultat observé : `Error from server (Forbidden): ... violates PodSecurity "restricted:latest"`, avec quatre motifs (privilégié, élévation de privilèges, capacités non retirées, root). Le cluster bloque le pod avant
même qu'il démarre, ce qui prouve que le profil est réellement appliqué.

## Limites connues (à connaître pour un entretien)

- **Socket Docker monté dans Jenkins** : équivaut à un accès root à la machine hôte. Acceptable pour un
  lab local. En production : agents Jenkins éphémères, Kaniko ou BuildKit sans démon.
- **Vérification des empreintes SSH désactivée** dans le lab Ansible.
- **Images non signées** : une étape suivante serait de signer avec cosign et de vérifier à l'admission.
- **NetworkPolicy** : appliquée seulement si le plugin réseau du cluster la supporte.
- **Pas de TLS** entre les composants du lab.
