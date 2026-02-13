# Deploying HomeControl to Kubernetes

This guide explains how to deploy the HomeControl backend to a Kubernetes cluster using the generated manifests in `backend/k8s/`.

## Prerequisites
-   A running Kubernetes cluster (e.g., Minikube, Docker Desktop K8s, GKE, EKS).
-   `kubectl` installed and configured.
-   **Important**: You must build the `backend-app` image and make it available to your cluster.
    -   **Docker Desktop**: It shares images with local docker.
    -   **Minikube**: Run `eval $(minikube docker-env)` before building.
    -   **Cloud**: Push `backend-app` to a container registry (Docker Hub, ECR, GCR).

## Deployment Steps

1.  **Navigate to directory**:
    ```bash
    cd backend
    ```

2.  **Apply Configuration & Secrets**:
    ```bash
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secrets.yaml
    ```

3.  **Apply Storage**:
    ```bash
    kubectl apply -f k8s/persistent-volumes.yaml
    ```

4.  **Deploy Data (Postgres & Redis)**:
    ```bash
    kubectl apply -f k8s/postgres.yaml
    kubectl apply -f k8s/redis.yaml
    ```

5.  **Deploy Application**:
    ```bash
    kubectl apply -f k8s/nginx-configmap.yaml
    kubectl apply -f k8s/backend.yaml
    kubectl apply -f k8s/nginx.yaml
    ```

6.  **Verify Status**:
    ```bash
    kubectl get pods
    kubectl get services
    ```

7.  **Access the App**:
    -   **Docker Desktop / Cloud LoadBalancer**: Access `http://localhost` (or the external IP).
    -   **Minikube**: Run `minikube service nginx` to get the URL.
