# cloud-systems-project

## Project overview

This repository contains a multi-stage university project for the **Cloud Systems** course.  
The application is a three-tier **Netflix Content Dashboard** built around:
- a PostgreSQL database,
- a FastAPI backend,
- and a frontend dashboard served through Nginx.

The project evolved across five stages.  
The key point is that **Stage 1 focused on the application logic**, while **Stages 2–5 migrated the same application into reproducible local, virtualized, containerized, Kubernetes, and public-cloud environments**.

Dataset used in all stages: **Netflix Content Analysis** from Kaggle.

---

## Important note about project chronology

**Stage 1 was implemented before the later infrastructure stages existed.**  
At that point, the goal was to build the application itself: database schema, CSV import, backend API, frontend UI, filtering, CRUD operations, and advanced data processing.

Only in later stages was the same application migrated to:
- Vagrant + Ansible,
- Docker + Docker Compose,
- local Kubernetes with kind,
- Google Cloud Platform with Terraform, Ansible, and GKE.

Because of that, Stage 1 should be described as the **original functional implementation**, not as a Docker or Kubernetes setup.

---

## Stage 1 – Application logic (Supabase)

The first stage focused on building the application logic.

### What was implemented
- The project used the **Netflix Content Analysis** dataset from Kaggle.
- The original database solution in this stage was **Supabase**, providing a managed PostgreSQL environment.
- A Python import script loaded the CSV dataset into PostgreSQL.
- The backend was implemented in **FastAPI**.
- The frontend provided a dashboard for interacting with the backend.

### Functional scope
The backend supported:
- retrieving records,
- filtering by criteria,
- creating new records,
- updating existing records,
- advanced data processing through statistics and recommendations.

### Example API functionality
- `GET /titles`
- `GET /titles/{show_id}`
- `POST /titles`
- `PUT /titles/{show_id}`
- `GET /stats/top-genres`
- `GET /stats/releases-by-year`
- `GET /recommendations?title=...`

### Original Stage 1 notes
This stage used **Supabase** as the original database backend.  
Later stages migrated the same application to self-managed PostgreSQL environments.

---

## Stage 2 – Infrastructure as Code (Vagrant + Ansible)

The second stage focused on preparing a fully reproducible multi-machine environment.

### What was implemented
- A **three-machine Vagrant setup**:
  - `db`
  - `backend`
  - `frontend`
- Private network communication between:
  - database and backend,
  - backend and frontend
- Only the `frontend` machine exposed a forwarded port to the host.

### Automation
Each machine was provisioned automatically with **Ansible (`ansible_local`)**.

### Architecture
- `db` VM: PostgreSQL and dataset import
- `backend` VM: FastAPI application
- `frontend` VM: built frontend served by Nginx

### Access
The frontend was exposed on:
- `http://localhost:8080`

---

## Stage 3 – Containerization (Docker + Docker Compose)

The third stage focused on containerizing the application.

### What was implemented
- Separate Docker images for:
  - `db`
  - `backend`
  - `frontend`
- A multi-container setup using `docker-compose.yml`

### Architecture
- `db`: PostgreSQL with schema creation and CSV import
- `backend`: FastAPI API container
- `frontend`: React/Vite frontend built and served by Nginx
- Nginx was configured as a reverse proxy for `/api`

### Access
The application could be started locally with Docker Compose and accessed at:
- `http://localhost:8080`

---

## Stage 4 – Kubernetes (kind)

The fourth stage focused on deploying the application to a local Kubernetes cluster.

### What was implemented
- A local Kubernetes cluster using **kind**
- Port mapping from cluster `30000` to host `8080`
- Kubernetes manifests for:
  - `PersistentVolume`
  - `PersistentVolumeClaim`
  - `Deployment`
  - `Service`
- Separate Kubernetes objects for:
  - `db`
  - `backend`
  - `frontend`

### Reliability features
- **Liveness probes**
- **Readiness probes**
- Persistent storage for the database

### Access
The frontend was exposed with a **NodePort** service and was available at:
- `http://localhost:8080`

---

## Stage 5 – Public Cloud (GCP + Terraform + Ansible + GKE)

The fifth stage focused on deploying the project in a public cloud environment.

### What was implemented
- **Google Cloud Platform**
- **Terraform** for declarative infrastructure provisioning
- **Ansible** for automatic VM configuration
- **Google Kubernetes Engine (GKE)** for cloud Kubernetes deployment

### VM deployment
A VM was created in GCP and configured automatically to run the application with Docker Compose.

### GKE deployment
Application images were pushed to **Artifact Registry** and deployed to GKE with:
- namespace
- secret
- persistent volume claim
- db deployment and service
- backend deployment and service
- frontend deployment and service

### Important implementation detail
During GKE deployment, PostgreSQL required:
- `PGDATA=/var/lib/postgresql/data/pgdata`

This fixed the initialization issue caused by the `lost+found` directory on the mounted persistent volume.

---

## How to verify each stage

### Stage 1
Stage 1 is the **original functional implementation**.  
Its logic is documented in the report and source code:
- Supabase database setup
- CSV import script
- FastAPI endpoints
- frontend dashboard

### Stage 2
To verify Stage 2:
```bash
vagrant up
vagrant status
vagrant ssh db -c "hostname && cat /tmp/db-ready.txt"
vagrant ssh backend -c "hostname && cat /tmp/backend-ready.txt"
vagrant ssh backend -c "ping -c 1 192.168.56.11 && ping -c 1 192.168.56.13"
```
Then open:
`http://localhost:8080`


### Stage 3
To verify Stage 3:
```bash
docker compose up -d --build
docker compose ps
docker compose exec db psql -U netflix_user -d netflix_db -c "SELECT COUNT(*) FROM netflix_titles;"
docker compose exec backend curl http://localhost:8000/
```
Then open:
`http://localhost:8080`

### Stage 4
To verify Stage 4:
```bash
kind create cluster --config=k8s/kind-cluster.yaml
kubectl cluster-info
kubectl get nodes
kubectl apply -f k8s/
kubectl get pods
kubectl get svc
```
Then open:
`http://localhost:8080`

### Stage 5 - VM
To verify the cloud VM deployment:
```bash
cd cloud/terraform
terraform init
terraform apply
cd ../ansible
ansible-playbook -i inventory.ini deploy_vm.yml
```
Then open the VM public IP in the browser.
### Stage 5 – GKE
To verify GKE deployment:
```bash
kubectl apply -f cloud/gke/netflix-gke.yaml
kubectl get pods -n netflix
kubectl get svc -n netflix
kubectl get pvc -n netflix
```
Then open the external IP of the frontend LoadBalancer service.

---

### Repository structure
- database/ – schema and import scripts
- backend/ – FastAPI backend
- frontend/ – frontend application
- infra/ansible/ – Ansible files for Vagrant stage
- k8s/ – Kubernetes manifests for local cluster
- cloud/terraform/ – Terraform files for GCP
- cloud/ansible/ – Ansible deployment for GCP VM
- cloud/gke/ – Kubernetes manifests for GKE

