# SHERPA Deployment Guide

## Deployment Options

SHERPA supports multiple deployment modes to fit your needs:

### 1. Local Development (Simplest)

**Best for:** Trying SHERPA, local development, no cloud needed

```bash
git clone https://github.com/nirmalarya/sherpa
cd sherpa
./init.sh
sherpa serve
```

**Access:** http://localhost:3003

**What you get:**
- ✅ Full functionality
- ✅ Local file-based knowledge search
- ✅ SQLite database
- ✅ No cloud costs
- ✅ Works offline

---

### 2. Docker Compose (Recommended for Teams)

**Best for:** Team deployments, consistent environments

```bash
git clone https://github.com/nirmalarya/sherpa
cd sherpa
docker-compose up -d
```

**Includes:**
- SHERPA backend (FastAPI)
- SHERPA frontend (React)
- PostgreSQL (optional, can use SQLite)
- Vector DB (Qdrant - coming in v1.1)

**Access:** http://localhost:3003

---

### 3. Kubernetes (Production - Cloud Agnostic)

**Best for:** Production deployments, any cloud provider

**Works on:**
- AWS EKS
- Google GKE
- Azure AKS
- On-premise Kubernetes
- DigitalOcean K8s
- Linode K8s

#### Quick Deploy

```bash
# Deploy to any Kubernetes cluster
kubectl apply -f infrastructure/kubernetes/

# Check status
kubectl get pods -n sherpa

# Get external IP
kubectl get service sherpa-frontend -n sherpa
```

#### Helm Chart (v1.1)

```bash
# Add SHERPA helm repo
helm repo add sherpa https://charts.sherpa.dev

# Install
helm install my-sherpa sherpa/sherpa \
  --set kb.backend=local \
  --set ingress.enabled=true \
  --set ingress.host=sherpa.yourcompany.com
```

---

### 4. SaaS (Managed by SHERPA Team)

**Best for:** No infrastructure management, just use it

**Coming soon:** https://sherpa.dev (planned)

**Features:**
- ✅ Zero setup
- ✅ Always up-to-date
- ✅ Managed infrastructure
- ✅ Automatic backups
- ✅ Enterprise support

---

## Knowledge Base Options

### v1.0 (Current): Local File Search

**Setup:** None! Works out of the box
**Pros:** Simple, no dependencies
**Cons:** Basic search (keyword matching)

```bash
# Default mode - just works
sherpa serve
```

### v1.1 (Next): Local Vector DB

**Option A: Qdrant**
```bash
# Run Qdrant locally
docker run -p 6333:6333 qdrant/qdrant

# Configure SHERPA
export SHERPA_KB_BACKEND=qdrant
export QDRANT_URL=http://localhost:6333

sherpa serve
```

**Option B: ChromaDB**
```bash
# Embedded - no separate service!
pip install chromadb

export SHERPA_KB_BACKEND=chroma
sherpa serve
```

**Pros:** Semantic search, no cloud, works offline
**Cons:** Local only (not shared across team)

### v2.0 (Future): AWS Bedrock (Optional)

**For SaaS deployments or enterprises with AWS:**

```bash
export SHERPA_KB_BACKEND=bedrock
export BEDROCK_KB_ID=your-kb-id
export AWS_REGION=us-east-1

sherpa serve
```

**Pros:** Managed, scalable, shared knowledge
**Cons:** Requires AWS, costs money

---

## Environment Variables

### Required (All Modes)
```bash
# None! SHERPA works out of the box with defaults
```

### Optional (Enhanced Features)
```bash
# Knowledge Base Backend
export SHERPA_KB_BACKEND=local      # file, local, qdrant, chroma, bedrock

# Database (default: SQLite)
export DATABASE_URL=postgresql://...  # Optional: Use PostgreSQL

# Azure DevOps (optional)
export AZURE_DEVOPS_PAT=your-pat
export AZURE_DEVOPS_ORG=your-org

# AWS Bedrock (only if using bedrock backend)
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export BEDROCK_KB_ID=your-kb-id
```

---

## Kubernetes Deployment Details

### Architecture

```
                    Ingress (sherpa.yourcompany.com)
                            ↓
        ┌──────────────────┴──────────────────┐
        │                                     │
  Frontend Service                  Backend Service
  (React/Vite)                      (FastAPI)
        │                                     │
        └──────────────────┬──────────────────┘
                          ↓
              ┌───────────┴────────────┐
              │                        │
         PostgreSQL              Vector DB (optional)
         (StatefulSet)           (Qdrant/Chroma)
```

### Resources Needed

**Minimum:**
- 2 CPUs
- 4GB RAM
- 10GB storage

**Recommended:**
- 4 CPUs
- 8GB RAM
- 50GB storage

### Scaling

```bash
# Scale backend
kubectl scale deployment sherpa-backend --replicas=5 -n sherpa

# Scale frontend
kubectl scale deployment sherpa-frontend --replicas=3 -n sherpa
```

---

## Database Options

### SQLite (Default - v1.0)
**Pros:** No setup, simple
**Cons:** Single-instance only

### PostgreSQL (Recommended for Production - v1.1)
**Pros:** Multi-instance, robust
**Cons:** Requires database server

```bash
# K8s with PostgreSQL
helm install my-sherpa sherpa/sherpa \
  --set database.type=postgresql \
  --set database.host=postgres.sherpa.svc.cluster.local
```

---

## Cost Comparison

### Local Deployment
**Cost:** $0/month
**Best for:** Development, small teams

### Self-Hosted K8s
**Cost:** $50-200/month (K8s cluster cost)
**Best for:** Companies, full control

### SaaS (When Available)
**Cost:** TBD (usage-based)
**Best for:** No infrastructure management

---

## Quick Start by Use Case

**"I want to try SHERPA locally"**
```bash
git clone https://github.com/nirmalarya/sherpa
cd sherpa && ./init.sh && sherpa serve
```

**"I want to deploy for my team"**
```bash
kubectl apply -f infrastructure/kubernetes/
```

**"I want better search without cloud"**
```bash
# v1.1 (coming soon)
docker-compose up -d  # Includes Qdrant
```

**"I want enterprise deployment with AWS"**
```bash
# Deploy to K8s with Bedrock backend
# Contact for enterprise support
```

---

## Support

- **Community:** GitHub Issues
- **Documentation:** See docs/ directory
- **Enterprise:** Contact for managed deployments

---

**SHERPA: Run anywhere, from laptop to cloud!** ☁️

