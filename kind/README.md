# Cluster local (kind)

Prérequis (une fois, dans PowerShell) :
```
winget install Kubernetes.kind
winget install Kubernetes.kubectl
```
Rouvre PowerShell après l'installation.

Création du cluster et déploiement manuel de l'étape 4 :
```
kind create cluster --config kind/cluster.yaml
docker build -t devops-lab:dev .
docker save devops-lab:dev | docker exec -i devops-lab-control-plane ctr -n k8s.io images import -
kubectl apply -f k8s/
kubectl -n devops-lab get pods
curl http://localhost:8082/api/info
```

Si la création échoue : `kind delete cluster --name devops-lab`, puis relancer.

Suppression : `kind delete cluster --name devops-lab`
