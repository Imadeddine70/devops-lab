# Supervision

Prérequis : le cluster kind existe et l'application est déployée.

```
# 1. metrics-server (nécessaire à l'autoscaling), adapté à kind
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.7.2/components.yaml
kubectl -n kube-system patch deployment metrics-server --type=json -p "[{\"op\":\"add\",\"path\":\"/spec/template/spec/containers/0/args/-\",\"value\":\"--kubelet-insecure-tls\"}]"

# 2. Namespace puis secret Grafana (le mot de passe n'est jamais dans git)
kubectl apply -f monitoring/00-namespace.yaml
kubectl -n monitoring create secret generic grafana-admin --from-literal=password=CHOISIS_UN_MOT_DE_PASSE

# 3. Prometheus et Grafana
kubectl apply -f monitoring/
```

- Prometheus : http://localhost:9090 (Status, Targets : les 2 pods doivent être UP)
- Grafana : http://localhost:3000, utilisateur `admin`, dashboard « devops-lab »

## Test de l'autoscaling
```
kubectl run load --image=busybox:1.36 --restart=Never -- /bin/sh -c "while true; do wget -q -O- http://devops-lab.devops-lab/health; done"
kubectl -n devops-lab get hpa -w
kubectl delete pod load
```
