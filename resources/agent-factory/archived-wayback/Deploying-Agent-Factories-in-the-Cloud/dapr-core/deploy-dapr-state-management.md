# Deploy Dapr + State Management

> **Archived from:** <https://agentfactory.panaversity.org/docs/Deploying-Agent-Factories-in-the-Cloud/dapr-core/deploy-dapr-state-management>  
> **Wayback snapshot:** 2026-04-22  
> **Status:** retired from the live site — recovered for offline study.

---

You understand the sidecar pattern and building blocks from L01-L02. Now deploy a real Dapr control plane and write code that talks to it.

This lesson has two parts. Part A deploys Dapr and Redis on your Kubernetes cluster, then explores what Dapr actually installed. Part B builds a FastAPI app, containerizes it, deploys it as a pod, and tests every state operation through the sidecar.

Your code runs inside a container. `DaprClient()` talks to `localhost:3500`, which is the sidecar injected into your pod. The sidecar talks to Redis. Your app never touches Redis directly.

## Part A: Deploy Dapr with Helm (15 minutes)​

### Prerequisites Check​
    
    
    kubectl cluster-info  
    
    
    
    Kubernetes control plane is running at https://127.0.0.1:6443  
    CoreDNS is running at https://127.0.0.1:6443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy  
    
    
    
    helm version  
    
    
    
    version.BuildInfo{Version:"v3.16.3", ...}  
    

If either command fails, revisit Chapters 79-81 for Docker Desktop Kubernetes and Helm setup.

### Step 1: Add Dapr Helm Repository​
    
    
    helm repo add dapr https://dapr.github.io/helm-charts/  
    helm repo update  
    

### Step 2: Install Dapr Control Plane​
    
    
    helm upgrade --install dapr dapr/dapr \  
      --version=1.17.4 \  
      --namespace dapr-system \  
      --create-namespace \  
      --wait  
    

`--wait` blocks until all pods are ready. `upgrade --install` is idempotent: run it again and nothing breaks.

### Step 3: Verify Control Plane​
    
    
    kubectl get pods -n dapr-system  
    
    
    
    NAME                                     READY   STATUS    RESTARTS   AGE  
    dapr-operator-7d8b9f4c5b-x2j4k           1/1     Running   0          45s  
    dapr-sentry-5f6c7d8e9f-m3n5p             1/1     Running   0          45s  
    dapr-sidecar-injector-6a7b8c9d0e-q1r2s   1/1     Running   0          45s  
    dapr-placement-server-0                  1/1     Running   0          45s  
    dapr-scheduler-server-0                  1/1     Running   0          45s  
    

Five pods, five roles:

Component| Role  
---|---  
**dapr-operator**|  Manages Dapr component resources and Kubernetes integration  
**dapr-sidecar-injector**|  Injects sidecars into pods with Dapr annotations  
**dapr-sentry**|  Certificate authority for mTLS between services  
**dapr-placement-server**|  Actor placement service (Chapter 89)  
**dapr-scheduler-server**|  Job scheduling for the Jobs API (Lesson 7)  
  
### Step 4: Deep Dive: Explore What Dapr Installed​

Before moving on, stop and explore. Understanding what Helm deployed builds intuition for debugging later.

**Pods with node placement:**
    
    
    kubectl get pods -n dapr-system -o wide  
    

**Detailed pod spec (pick any pod):**
    
    
    kubectl describe pod -l app=dapr-operator -n dapr-system  
    

**Services exposed by Dapr:**
    
    
    kubectl get svc -n dapr-system  
    

**Custom Resource Definitions (CRDs):**
    
    
    kubectl get crds | grep dapr  
    

You should see CRDs for `components`, `configurations`, `subscriptions`, `resiliencies`, and `httpendpoints`. These are the Kubernetes-native objects Dapr watches.

**MutatingWebhookConfiguration:**
    
    
    kubectl get mutatingwebhookconfiguration | grep dapr  
    

This is **how sidecar injection works**. When you create a pod with `dapr.io/enabled: "true"`, the Kubernetes API server calls this webhook. The sidecar-injector receives the pod spec, adds the `daprd` container, and returns the modified spec. No CLI needed, no manual container definitions.

**RBAC and ClusterRoles:**
    
    
    kubectl get clusterroles | grep dapr  
    

These grant Dapr components permission to watch pods, manage secrets, and read component definitions.

**Full Helm manifest (what Helm actually created):**
    
    
    helm get manifest dapr -n dapr-system | grep "^kind:" | sort | uniq -c | sort -rn  
    

**Helm values (your configuration):**
    
    
    helm get values dapr -n dapr-system  
    

#### Exploration Checklist​

Confirm these before proceeding:

  * 5 pods running in `dapr-system` (operator, sidecar-injector, sentry, placement, scheduler)
  * `MutatingWebhookConfiguration` exists (sidecar injection mechanism)
  * CRDs registered (components, configurations, subscriptions, resiliencies, httpendpoints)
  * ClusterRoles grant Dapr permissions to watch cluster resources
  * Sentry pod has TLS secrets for mTLS


### Step 5: Deploy Redis​

Dapr needs a backend for state storage. Deploy Redis with the Bitnami Helm chart:
    
    
    helm repo add bitnami https://charts.bitnami.com/bitnami  
    helm repo update  
      
    helm install redis bitnami/redis \  
      --namespace default \  
      --set auth.enabled=false \  
      --set architecture=standalone  
    

Wait for Redis to be ready:
    
    
    kubectl get pods -l app.kubernetes.io/name=redis  
    
    
    
    NAME               READY   STATUS    RESTARTS   AGE  
    redis-master-0     1/1     Running   0          60s  
    

`auth.enabled=false` and `architecture=standalone` keep this simple for learning. Production Redis uses authentication and replication.

### Step 6: Create and Apply State Store Component​

Dapr components tell the sidecar which backend to use. Create `statestore.yaml`:
    
    
    # statestore.yaml  
    apiVersion: dapr.io/v1alpha1  
    kind: Component  
    metadata:  
      name: statestore  
      namespace: default  
    spec:  
      type: state.redis  
      version: v1  
      metadata:  
        - name: redisHost  
          value: redis-master.default.svc.cluster.local:6379  
        - name: redisPassword  
          value: ""  
    

Field| Purpose  
---|---  
`type: state.redis`| Use the Redis state store implementation  
`version: v1`| Component API version  
`redisHost`| Kubernetes DNS name for the Redis service  
`redisPassword`| Empty because `auth.enabled=false`  
  
Apply it:
    
    
    kubectl apply -f statestore.yaml  
    

Verify:
    
    
    kubectl get components  
    
    
    
    NAME         AGE  
    statestore   15s  
    

Critical: Deployment Order

The statestore component **must exist before** you deploy any app pod that uses it. The `daprd` sidecar loads components at startup. If the component doesn't exist when the pod starts, the sidecar won't find it and your app will get `state store statestore is not configured` errors. Apply `statestore.yaml` first, deploy your app pod second.

Your Dapr control plane is running with a Redis state store configured. Any pod with Dapr annotations can now use the state API.

* * *

## Part B: Build and Deploy the State App (20 minutes)​

### The Full Pipeline​

Every change follows this path:
    
    
    Write code → Dockerfile → docker build → Pod YAML → kubectl apply  
    → Dapr injects sidecar → App talks to sidecar → Sidecar talks to Redis  
    

Your FastAPI app calls `localhost:3500` (the sidecar). The sidecar resolves `statestore` from the component YAML and routes to Redis. Your code never imports `redis`.

### Step 7: Initialize the Project​
    
    
    uv init dapr-app && cd dapr-app  
    uv add "fastapi[standard]" dapr  
    

`dapr` vs `dapr-client`

The correct PyPI package is **`dapr`** (version 1.14+). There is an older package called `dapr-client` that contains only proto stubs from an abandoned beta. If you install `dapr-client`, you will get `ModuleNotFoundError: No module named 'dapr.clients'` at runtime. Use `dapr`.

### Step 8: Application Code​

Create `main.py`:
    
    
    # main.py  
    from fastapi import FastAPI, HTTPException  
    from dapr.clients import DaprClient  
    from dapr.clients.grpc._state import StateItem  
    from pydantic import BaseModel  
    import json  
    import uuid  
      
    app = FastAPI()  
      
    STORE = "statestore"  
      
      
    class Todo(BaseModel):  
        id: str | None = None  
        title: str  
        done: bool = False  
      
      
    # --- SAVE ---  
    @app.post("/todos")  
    def create_todo(todo: Todo):  
        todo.id = str(uuid.uuid4())  
        with DaprClient() as client:  
            client.save_state(  
                store_name=STORE,  
                key=f"todo-{todo.id}",  
                value=todo.model_dump_json(),  
            )  
        return todo  
      
      
    # --- GET ---  
    @app.get("/todos/{todo_id}")  
    def get_todo(todo_id: str):  
        with DaprClient() as client:  
            state = client.get_state(store_name=STORE, key=f"todo-{todo_id}")  
            if not state.data:  
                raise HTTPException(status_code=404, detail="Todo not found")  
            return Todo.model_validate_json(state.data)  
      
      
    # --- DELETE ---  
    @app.delete("/todos/{todo_id}")  
    def delete_todo(todo_id: str):  
        with DaprClient() as client:  
            client.delete_state(store_name=STORE, key=f"todo-{todo_id}")  
        return {"status": "deleted"}  
      
      
    # --- UPDATE with ETag (optimistic concurrency) ---  
    @app.put("/todos/{todo_id}")  
    def update_todo(todo_id: str, todo: Todo):  
        with DaprClient() as client:  
            # Read current state + ETag  
            state = client.get_state(store_name=STORE, key=f"todo-{todo_id}")  
            if not state.data:  
                raise HTTPException(status_code=404, detail="Todo not found")  
      
            current_etag = state.etag  
      
            # Write with ETag — fails if someone else updated since our read  
            try:  
                client.save_state(  
                    store_name=STORE,  
                    key=f"todo-{todo_id}",  
                    value=todo.model_dump_json(),  
                    etag=current_etag,  
                )  
            except Exception as e:  
                raise HTTPException(status_code=409, detail=f"Conflict: {e}")  
      
        return todo  
      
      
    # --- BULK SAVE ---  
    @app.post("/todos/bulk")  
    def bulk_save(todos: list[Todo]):  
        items = []  
        for t in todos:  
            t.id = t.id or str(uuid.uuid4())  
            items.append(  
                StateItem(key=f"todo-{t.id}", value=t.model_dump_json())  
            )  
      
        with DaprClient() as client:  
            client.save_bulk_state(store_name=STORE, states=items)  
      
        return {"saved": len(items)}  
      
      
    # --- HEALTH ---  
    @app.get("/health")  
    def health():  
        return {"status": "healthy"}  
    

Key points about this code:

  * **`with DaprClient() as client:`** is synchronous. The SDK uses gRPC under the hood to talk to the sidecar at `localhost:50001`.
  * **`StateItem`** from `dapr.clients.grpc._state` is required for bulk operations. Passing plain dicts to `save_bulk_state` raises `'dict' has no attribute 'key'`.
  * **ETag concurrency** : read the etag, write with it. If another process modified the state between your read and write, the save fails. This is first-write-wins.


### Step 9: Dockerfile​

Create a multi-stage `Dockerfile`:
    
    
    # Dockerfile  
    FROM ghcr.io/astral-sh/uv:0.7-python3.12-bookworm-slim AS builder  
      
    WORKDIR /app  
    COPY pyproject.toml uv.lock ./  
    RUN uv sync --frozen --no-install-project  
    COPY . .  
    RUN uv sync --frozen  
      
    FROM python:3.12-slim-bookworm  
      
    RUN useradd --create-home appuser  
    WORKDIR /app  
    COPY --from=builder /app/.venv /app/.venv  
    COPY --from=builder /app/main.py .  
    ENV PATH="/app/.venv/bin:$PATH"  
      
    USER appuser  
    EXPOSE 8000  
      
    HEALTHCHECK --interval=30s --timeout=3s \  
      CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1  
      
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  
    

### Step 10: Build the Image​
    
    
    docker build -t dapr-state-app:latest .  
    

On Docker Desktop Kubernetes, locally built images are available to pods without pushing to a registry. The `imagePullPolicy: Never` annotation in the pod YAML handles this.

k3s Users

If you're using k3s instead of Docker Desktop, run `kimport dapr-state-app:latest` after `docker build`. k3s uses containerd, which doesn't share Docker's image store.

### Step 11: Pod YAML with Dapr Annotations​

Create `deployment.yaml`:
    
    
    # deployment.yaml  
    apiVersion: apps/v1  
    kind: Deployment  
    metadata:  
      name: dapr-state-app  
      labels:  
        app: dapr-state-app  
    spec:  
      replicas: 1  
      selector:  
        matchLabels:  
          app: dapr-state-app  
      template:  
        metadata:  
          labels:  
            app: dapr-state-app  
          annotations:  
            dapr.io/enabled: "true"  
            dapr.io/app-id: "dapr-state-app"  
            dapr.io/app-port: "8000"  
        spec:  
          containers:  
            - name: app  
              image: dapr-state-app:latest  
              imagePullPolicy: Never  
              ports:  
                - containerPort: 8000  
    

Why a Deployment, not a Pod

Use `kind: Deployment` for Dapr workloads. On Dapr 1.17+, the operator only auto-creates the `<app-id>-dapr` headless Service (which other apps resolve via DNS when calling `invoke_method`) for workloads owned by a Deployment or StatefulSet. Bare Pods work for this single-service lesson but break as soon as another service tries to call them in L04.

The three Dapr annotations:

Annotation| Purpose  
---|---  
`dapr.io/enabled: "true"`| Triggers the MutatingWebhook to inject the `daprd` sidecar  
`dapr.io/app-id: "dapr-state-app"`| Unique identity for this app in the Dapr mesh  
`dapr.io/app-port: "8000"`| Port where your app listens (sidecar forwards traffic here)  
  
`imagePullPolicy: Never` tells Kubernetes to use the local Docker image instead of pulling from a registry.

### Step 12: Deploy and Verify​

Confirm the statestore component exists (it must be present before the pod starts):
    
    
    kubectl get components  
    

Deploy it:
    
    
    kubectl apply -f deployment.yaml  
    

Watch the rollout:
    
    
    kubectl rollout status deployment/dapr-state-app  
    kubectl get pods -l app=dapr-state-app  
    

Wait for `2/2` in the READY column:
    
    
    NAME                              READY   STATUS    RESTARTS   AGE  
    dapr-state-app-6f7c9bd8d9-abcde   2/2     Running   0          30s  
    

`2/2` means two containers are running: your app and the `daprd` sidecar. If you see `1/2`, the sidecar is waiting for your app to respond on port 8000. If you see `0/2` with `Error` or `CrashLoopBackOff`, your app is crashing.

Grab the generated pod name for later commands and verify the containers inside:
    
    
    POD=$(kubectl get pod -l app=dapr-state-app -o jsonpath='{.items[0].metadata.name}')  
    kubectl get pod "$POD" -o jsonpath='{.spec.containers[*].name}'  
    
    
    
    app daprd  
    

### Step 13: Test All Endpoints​

Forward the port:
    
    
    kubectl port-forward deployment/dapr-state-app 8000:8000  
    

In another terminal, test each operation:

**Save a todo:**
    
    
    curl -s -X POST http://localhost:8000/todos \  
      -H "Content-Type: application/json" \  
      -d '{"title": "Learn Dapr state"}' | python -m json.tool  
    

Note the `id` in the response. Use it in subsequent commands (shown as `<ID>` below).

**Get the todo:**
    
    
    curl -s http://localhost:8000/todos/<ID> | python -m json.tool  
    

**Update with ETag concurrency:**
    
    
    curl -s -X PUT http://localhost:8000/todos/<ID> \  
      -H "Content-Type: application/json" \  
      -d '{"title": "Learn Dapr state", "done": true}' | python -m json.tool  
    

**Bulk save:**
    
    
    curl -s -X POST http://localhost:8000/todos/bulk \  
      -H "Content-Type: application/json" \  
      -d '[  
        {"id": "bulk-1", "title": "First bulk item"},  
        {"id": "bulk-2", "title": "Second bulk item"},  
        {"id": "bulk-3", "title": "Third bulk item"}  
      ]' | python -m json.tool  
    

**Delete:**
    
    
    curl -s -X DELETE http://localhost:8000/todos/<ID>  
    

**Verify deletion (expect 404):**
    
    
    curl -s http://localhost:8000/todos/<ID>  
    
    
    
    { "detail": "Todo not found" }  
    

### Step 14: Check Logs​

**App container logs:**
    
    
    kubectl logs deployment/dapr-state-app -c app  
    

**Sidecar logs:**
    
    
    kubectl logs deployment/dapr-state-app -c daprd  
    

The sidecar logs show component loading, gRPC calls, and state store interactions. When debugging, always check both containers.

* * *

## Key Concepts Demonstrated​

Concept| What You Did  
---|---  
Helm deployment| Deployed Dapr control plane with `helm upgrade --install`  
Sidecar injection| MutatingWebhook added `daprd` container automatically  
Component YAML| Configured Redis backend without touching app code  
State CRUD| Save, get, delete through `DaprClient()`  
ETag concurrency| First-write-wins with version tracking  
Bulk operations| `StateItem` objects for multi-key writes  
Container pipeline| Code to Dockerfile to image to pod with Dapr annotations  
  
## Dapr State vs Direct Redis​

Aspect| Direct Redis (redis-py)| Dapr State API  
---|---|---  
**Backend lock-in**|  Code tied to Redis| Swap via component YAML  
**Connection management**|  Your responsibility| Sidecar handles it  
**Concurrency**|  Manual ETag implementation| Built-in first-write-wins  
**mTLS**|  Manual certificate setup| Automatic via Sentry  
**State backends**|  Redis only| 30+ supported stores  
  
For a single service using Redis forever, direct Redis is fine. For distributed systems where you might change backends or need consistent patterns across services, Dapr provides the abstraction.

## Rebuild and Redeploy Workflow​

When you change code, the full cycle is:
    
    
    docker build -t dapr-state-app:latest .  
    kubectl rollout restart deployment/dapr-state-app  
    kubectl rollout status deployment/dapr-state-app    # wait for 2/2  
    

On k3s, add `kimport dapr-state-app:latest` after `docker build`.

## Troubleshooting​

Symptom| Cause| Fix  
---|---|---  
`ModuleNotFoundError: dapr.clients`| Installed `dapr-client` instead of `dapr`| `uv remove dapr-client && uv add dapr`  
`state store statestore is not configured`| Component didn't exist when pod started| Apply `statestore.yaml` before the app pod  
`'dict' has no attribute 'key'` on bulk save| `save_bulk_state` expects `StateItem` objects| Use `StateItem(key=k, value=v)`  
Pod shows `0/2 Error` or `CrashLoopBackOff`| App is crashing at startup| `kubectl logs deployment/dapr-state-app -c app`  
`ImagePullBackOff` (k3s)| Docker image not in containerd registry| Run `kimport` after `docker build`  
Pod stuck at `1/2`| `daprd` waiting for app to respond on port 8000| Check if app is crashing: `kubectl logs deployment/dapr-state-app -c app`  
  
## Cleanup​

Delete the app Deployment. Keep Dapr and Redis running for L04 (service invocation):
    
    
    kubectl delete deployment dapr-state-app  
    

* * *

## Reflect on Your Skill​

You built a `dapr-deployment` skill in Lesson 0. Does it cover the full pipeline from Helm deployment through containerized app deployment?

### Test It​
    
    
    Using my dapr-deployment skill, generate:  
    1. Helm commands to deploy Dapr 1.17 with verification  
    2. A Redis state store component YAML  
    3. A FastAPI app with DaprClient state operations  
    4. A Dockerfile and pod YAML with Dapr annotations  
      
    Does my skill produce a deployable result end-to-end?  
    

### Improve It​

If you found gaps, update the skill to include:

  * The statestore-before-pod deployment order warning
  * `StateItem` for bulk operations (not plain dicts)
  * The `dapr` package (not `dapr-client`)
  * The rebuild/redeploy cycle


* * *

## Try With AI​

**Deploy and Explore Dapr**
    
    
    I just deployed Dapr 1.17 on Kubernetes with Helm. Walk me through  
    what got installed: pods, CRDs, services, MutatingWebhookConfiguration,  
    and ClusterRoles. Explain how sidecar injection works using the  
    mutating webhook.  
    

**What you're learning:** Dapr uses a MutatingWebhookConfiguration to intercept pod creation. Understanding this mechanism applies to any Kubernetes operator that modifies pods at admission time.

* * *

**Debug a State Store Error**
    
    
    My Dapr app returns "state store statestore is not configured" but  
    kubectl get components shows the statestore exists. What are all  
    the possible causes? Walk me through the debugging steps including  
    checking daprd sidecar logs and component namespace.  
    

**What you're learning:** Dapr component resolution depends on namespace matching and startup order. Debugging sidecar issues teaches you to read `daprd` logs separately from app logs.

* * *

**Extend with a New State Backend**
    
    
    I have a working Dapr state app using Redis. Create a second component  
    YAML that uses PostgreSQL as the state backend. Show me how to switch  
    my app between Redis and PostgreSQL without changing any Python code.  
    

**What you're learning:** Backend portability is the core value proposition of Dapr's building block pattern. Changing a component YAML changes the backend; your application code stays identical.

**Safety note:** This lesson uses `auth.enabled=false` on Redis and no encryption at rest. Production state stores require authentication, TLS, and the Secrets building block (Lesson 8) for credentials.