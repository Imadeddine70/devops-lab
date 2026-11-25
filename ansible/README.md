# Étape 3 : Ansible

Ansible configure un serveur de façon **reproductible** : on décrit l'état voulu, on lance le
playbook, et relancer ne change rien si le serveur est déjà conforme (idempotence).

Le lab est entièrement dans Docker :

- `control` : un conteneur avec Ansible (le poste de l'administrateur) ;
- `node1` : un conteneur Ubuntu avec SSH qui joue le rôle de serveur à configurer.

```
cd ansible
docker compose up --build -d
docker compose exec control ansible-playbook site.yml      # 1re exécution : des "changed"
docker compose exec control ansible-playbook site.yml      # 2e exécution : changed=0
curl http://localhost:8083/health
docker compose down -v
```

Rôles :

| Rôle | Rôle |
|---|---|
| `common` | paquets de base et utilisateur système `appsvc` |
| `ssh_hardening` | root interdit, mot de passe interdit, 3 essais max, utilisateurs autorisés ; vérifie la config réelle avec `sshd -T` |
| `app` | copie l'application, crée un virtualenv, lance gunicorn sous un utilisateur non privilégié |

Lab uniquement : la vérification des empreintes SSH est désactivée (`ansible.cfg`).
