# Capstone: Dapr-Enabled Task API

> **Archived from:** <https://agentfactory.panaversity.org/docs/Deploying-Agent-Factories-in-the-Cloud/dapr-core/capstone-dapr-task-api>  
> **Wayback snapshot:** 2026-04-20  
> **Status:** retired from the live site — recovered for offline study.

---

You learned each Dapr building block in isolation. State management in Lesson 03. Pub/sub in Lesson 05. Service invocation in Lesson 04. Secrets in Lesson 08. Each one replaced a direct infrastructure client with a single Dapr API call.

Now compose them all into one application. The Part 6 Task API currently imports `redis`, `confluent_kafka`, and `httpx` to talk to infrastructure. After this capstone, it imports none of them. Every infrastructure interaction flows through Dapr.

Zero infrastructure imports in application code. That is the payoff.

## The Transformation​

This table is the entire chapter in one glance:

Before (Direct SDKs)| After (Dapr)  
---|---  
`import redis`| `from dapr.clients import DaprClient`  
`redis.set()` / `redis.get()`| `client.save_state()` / `client.get_state()`  
`producer.send()`| `client.publish_event()`  
`httpx.post(url)`| `client.invoke_method(app_id=...)`  
`os.getenv("API_KEY")`| `client.get_secret()`  
  
Infrastructure becomes configuration. Need to swap Redis for PostgreSQL? Change a YAML file. Your Python stays the same.

## Success Criteria​

  1. **SC-1** : Pod shows `2/2 READY` (app + daprd sidecar)
  2. **SC-2** : CRUD tasks via Dapr state with ETag concurrency
  3. **SC-3** : Events published to pub/sub on create and complete
  4. **SC-4** : Task completion invokes `notification-service` via Dapr
  5. **SC-5** : No `redis`, `kafka`, or `httpx` imports in application code


## Architecture​
    
    
    ┌──────────────────────────────────────────────────────────────────┐  
    │                Docker Desktop Kubernetes                         │  
    │                                                                  │  
    │  ┌──────────────────────────────────────────────────────────┐   │  
    │  │  task-api Pod (2/2 containers)                           │   │  
    │  │  ┌──────────────────────┐  ┌──────────────────────────┐  │   │  
    │  │  │  FastAPI Application │  │  Dapr Sidecar (daprd)    │  │   │  
    │  │  │  POST /tasks         │  │  State API    :3500      │  │   │  
    │  │  │  GET  /tasks/{id}    │──│  Pub/Sub API  :3500      │  │   │  
    │  │  │  PUT  /tasks/{id}    │  │  Invoke API   :3500      │  │   │  
    │  │  │  DELETE /tasks/{id}  │  │  Secrets API  :3500      │  │   │  
    │  │  └──────────────────────┘  └──────────────────────────┘  │   │  
    │  └──────────────────────────────────────────────────────────┘   │  
    │                          │                                       │  
    │            ┌─────────────┴─────────────┐                        │  
    │            ▼                           ▼                        │  
    │  ┌──────────────────┐     ┌──────────────────┐                  │  
    │  │  Redis            │     │  Redis            │                  │  
    │  │  (statestore)     │     │  (pubsub)         │                  │  
    │  └──────────────────┘     └──────────────────┘                  │  
    │                                                                  │  
    │  ┌──────────────────┐     ┌──────────────────┐                  │  
    │  │  notification-svc │     │  Kubernetes       │                  │  
    │  │  app-id:          │     │  Secrets          │                  │  
    │  │  notification     │     │  (k8s-secrets)    │                  │  
    │  └──────────────────┘     └──────────────────┘                  │  
    └──────────────────────────────────────────────────────────────────┘  
    

## Data Models​

Create `models.py`:
    
    
    from pydantic import BaseModel, Field  
    from datetime import datetime  
    from enum import Enum  
      
      
    class TaskStatus(str, Enum):  
        PENDING = "pending"  
        IN_PROGRESS = "in_progress"  
        COMPLETED = "completed"  
      
      
    class TaskCreate(BaseModel):  
        title: str = Field(..., min_length=1, max_length=200)  
        description: str | None = None  
        priority: int = Field(default=1, ge=1, le=5)  
      
      
    class Task(BaseModel):  
        id: str  
        title: str  
        description: str | None = None  
        status: TaskStatus = TaskStatus.PENDING  
        priority: int = 1  
        created_at: datetime  
        updated_at: datetime  
      
      
    class TaskEvent(BaseModel):  
        event_type: str  
        task_id: str  
        title: str  
        status: str  
        timestamp: datetime  
    

`TaskStatus` is a string enum so it serializes cleanly to JSON. `TaskCreate` validates input with `Field` constraints. `TaskEvent` carries the data published to the pub/sub topic.

## Main Application​

Create `main.py`. This is the complete application. Every infrastructure call goes through `DaprClient`. The `DaprApp` from `dapr-ext-fastapi` handles programmatic pub/sub subscriptions.
    
    
    from contextlib import asynccontextmanager  
    from datetime import datetime  
    from fastapi import FastAPI, HTTPException  
    from dapr.clients import DaprClient  
    from dapr.ext.fastapi import DaprApp  
    import json  
    import uuid  
      
    from models import Task, TaskCreate, TaskStatus, TaskEvent  
      
    # Names match component metadata.name in YAML  
    STORE_NAME = "statestore"  
    PUBSUB_NAME = "pubsub"  
    TOPIC_NAME = "task-events"  
      
      
    @asynccontextmanager  
    async def lifespan(app: FastAPI):  
        """Block startup until the Dapr sidecar is ready."""  
        with DaprClient() as client:  
            client.wait(timeout_s=30)  
        yield  
      
      
    app = FastAPI(title="Task API with Dapr", lifespan=lifespan)  
    dapr_app = DaprApp(app)  
      
      
    # ── CRUD Endpoints ──────────────────────────────────────────────  
      
      
    @app.post("/tasks", response_model=Task, status_code=201)  
    def create_task(task_create: TaskCreate):  
        """Create task, save state, publish event."""  
        now = datetime.utcnow()  
        task = Task(  
            id=str(uuid.uuid4()),  
            title=task_create.title,  
            description=task_create.description,  
            priority=task_create.priority,  
            created_at=now,  
            updated_at=now,  
        )  
      
        with DaprClient() as client:  
            client.save_state(  
                store_name=STORE_NAME,  
                key=f"task-{task.id}",  
                value=task.model_dump_json(),  
            )  
      
            event = TaskEvent(  
                event_type="task.created",  
                task_id=task.id,  
                title=task.title,  
                status=task.status.value,  
                timestamp=now,  
            )  
            client.publish_event(  
                pubsub_name=PUBSUB_NAME,  
                topic_name=TOPIC_NAME,  
                data=event.model_dump_json(),  
                data_content_type="application/json",  
            )  
      
        return task  
      
      
    @app.get("/tasks/{task_id}", response_model=Task)  
    def get_task(task_id: str):  
        """Retrieve task from Dapr state store."""  
        with DaprClient() as client:  
            state = client.get_state(store_name=STORE_NAME, key=f"task-{task_id}")  
            if not state.data:  
                raise HTTPException(status_code=404, detail="Task not found")  
            return Task.model_validate_json(state.data)  
      
      
    @app.put("/tasks/{task_id}/status", response_model=Task)  
    def update_task_status(task_id: str, status: TaskStatus):  
        """Update status with ETag concurrency, publish event."""  
        with DaprClient() as client:  
            state = client.get_state(store_name=STORE_NAME, key=f"task-{task_id}")  
            if not state.data:  
                raise HTTPException(status_code=404, detail="Task not found")  
      
            task = Task.model_validate_json(state.data)  
            task.status = status  
            task.updated_at = datetime.utcnow()  
      
            # ETag ensures no concurrent overwrites  
            client.save_state(  
                store_name=STORE_NAME,  
                key=f"task-{task_id}",  
                value=task.model_dump_json(),  
                etag=state.etag,  
            )  
      
            event = TaskEvent(  
                event_type=f"task.{status.value}",  
                task_id=task.id,  
                title=task.title,  
                status=status.value,  
                timestamp=task.updated_at,  
            )  
            client.publish_event(  
                pubsub_name=PUBSUB_NAME,  
                topic_name=TOPIC_NAME,  
                data=event.model_dump_json(),  
                data_content_type="application/json",  
            )  
      
            return task  
      
      
    @app.delete("/tasks/{task_id}", status_code=204)  
    def delete_task(task_id: str):  
        """Remove task from state store."""  
        with DaprClient() as client:  
            state = client.get_state(store_name=STORE_NAME, key=f"task-{task_id}")  
            if not state.data:  
                raise HTTPException(status_code=404, detail="Task not found")  
            client.delete_state(store_name=STORE_NAME, key=f"task-{task_id}")  
      
      
    # ── Subscription Handler ───────────────────────────────────────  
      
      
    @dapr_app.subscribe(pubsub=PUBSUB_NAME, topic=TOPIC_NAME)  
    def handle_task_event(event_data: dict):  
        """On task.completed, invoke notification-service via Dapr."""  
        event_type = event_data.get("event_type", "unknown")  
        task_id = event_data.get("task_id", "unknown")  
        print(f"Received event: {event_type} for task {task_id}")  
      
        if event_type == "task.completed":  
            with DaprClient() as client:  
                try:  
                    client.invoke_method(  
                        app_id="notification-service",  
                        method_name="notify",  
                        data=json.dumps({  
                            "type": "task_completed",  
                            "task_id": task_id,  
                            "message": f"Task {task_id} completed",  
                        }),  
                        http_verb="POST",  
                    )  
                    print(f"Notification sent for task {task_id}")  
                except Exception as e:  
                    print(f"Notification failed: {e}")  
      
        return {"status": "SUCCESS"}  
      
      
    # ── Health ──────────────────────────────────────────────────────  
      
      
    @app.get("/health")  
    def health():  
        return {"status": "healthy"}  
      
      
    if __name__ == "__main__":  
        import uvicorn  
        uvicorn.run(app, host="0.0.0.0", port=8000)  
    

Key patterns to notice:

  * **Sync`DaprClient`**: every endpoint uses `with DaprClient() as client`. No async needed for Dapr's HTTP sidecar calls.
  * **`client.wait(timeout_s=30)`** in lifespan blocks FastAPI startup until the sidecar is reachable. Without this, early requests fail.
  * **`@dapr_app.subscribe`** from `dapr-ext-fastapi` registers a programmatic subscription. Dapr calls this endpoint when events arrive on the topic.
  * **ETag on update** : `save_state` with `etag=state.etag` gives you optimistic concurrency for free.
  * **Service invocation** : `invoke_method(app_id="notification-service")` uses Dapr's service discovery. No URL, no port, no DNS lookup in your code.


## Required Components​

Apply all three component YAMLs **before** deploying the application. Dapr needs these to know which backends to use.

`components/statestore.yaml`:
    
    
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
    

`components/pubsub.yaml`:
    
    
    apiVersion: dapr.io/v1alpha1  
    kind: Component  
    metadata:  
      name: pubsub  
      namespace: default  
    spec:  
      type: pubsub.redis  
      version: v1  
      metadata:  
        - name: redisHost  
          value: redis-master.default.svc.cluster.local:6379  
    

`components/secrets.yaml`:
    
    
    apiVersion: dapr.io/v1alpha1  
    kind: Component  
    metadata:  
      name: kubernetes-secrets  
      namespace: default  
    spec:  
      type: secretstores.kubernetes  
      version: v1  
      metadata: []  
    

Apply them:
    
    
    kubectl apply -f components/statestore.yaml \  
                  -f components/pubsub.yaml \  
                  -f components/secrets.yaml  
    
    
    
    component.dapr.io/statestore created  
    component.dapr.io/pubsub created  
    component.dapr.io/kubernetes-secrets created  
    

## Deployment​

This is the capstone, so we use a `Deployment` (not a bare Pod) with 2 replicas and a readiness probe. Dapr annotations on the pod template trigger sidecar injection.

`k8s/deployment.yaml`:
    
    
    apiVersion: apps/v1  
    kind: Deployment  
    metadata:  
      name: task-api  
      namespace: default  
    spec:  
      replicas: 2  
      selector:  
        matchLabels:  
          app: task-api  
      template:  
        metadata:  
          labels:  
            app: task-api  
          annotations:  
            dapr.io/enabled: "true"  
            dapr.io/app-id: "task-api"  
            dapr.io/app-port: "8000"  
            dapr.io/enable-api-logging: "true"  
        spec:  
          containers:  
            - name: task-api  
              image: task-api:latest  
              ports:  
                - containerPort: 8000  
              readinessProbe:  
                httpGet:  
                  path: /health  
                  port: 8000  
                initialDelaySeconds: 5  
                periodSeconds: 10  
              resources:  
                requests:  
                  cpu: "100m"  
                  memory: "128Mi"  
                limits:  
                  cpu: "500m"  
                  memory: "256Mi"  
    ---  
    apiVersion: v1  
    kind: Service  
    metadata:  
      name: task-api  
      namespace: default  
    spec:  
      selector:  
        app: task-api  
      ports:  
        - port: 80  
          targetPort: 8000  
      type: ClusterIP  
    

Two replicas means Kubernetes keeps two pods running. Each pod gets its own Dapr sidecar, so you see `2/2` in the READY column. The readiness probe on `/health` ensures traffic only routes to pods that have finished startup (including the `client.wait` for sidecar readiness).

## Build and Deploy​
    
    
    # Build the container image  
    docker build -t task-api:latest .  
      
    # Load into Docker Desktop Kubernetes  
    docker tag task-api:latest task-api:latest  
      
    # Deploy  
    kubectl apply -f k8s/deployment.yaml  
      
    # Wait for rollout  
    kubectl rollout status deployment/task-api  
      
    # Port-forward for testing  
    kubectl port-forward service/task-api 8000:80  
    

`Dockerfile`:
    
    
    FROM python:3.12-slim  
      
    WORKDIR /app  
      
    COPY requirements.txt .  
    RUN pip install --no-cache-dir -r requirements.txt  
      
    COPY models.py main.py ./  
      
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  
    

`requirements.txt`:
    
    
    fastapi>=0.115.0  
    uvicorn>=0.32.0  
    dapr>=1.13.0  
    dapr-ext-fastapi>=1.13.0  
    

## Validation Checklist​

Run each command to verify your success criteria.

**SC-1: Sidecar injection working**
    
    
    kubectl get pods -l app=task-api  
    
    
    
    NAME                        READY   STATUS    RESTARTS   AGE  
    task-api-7d4b5c6f8-abc12    2/2     Running   0          2m  
    task-api-7d4b5c6f8-def34    2/2     Running   0          2m  
    

Both pods show `2/2`. The second container is the Dapr sidecar.

**SC-2: CRUD with Dapr state and ETag concurrency**
    
    
    # Create  
    curl -s -X POST http://localhost:8000/tasks \  
      -H "Content-Type: application/json" \  
      -d '{"title": "Learn Dapr building blocks", "priority": 2}'  
      
    # Get (use the id from create response)  
    curl -s http://localhost:8000/tasks/{id}  
    

**SC-3: Events published on create and complete**
    
    
    kubectl logs -l app=task-api -c task-api | grep "Received event"  
    
    
    
    Received event: task.created for task abc-123  
    

**SC-4: Service invocation on completion**
    
    
    curl -s -X PUT "http://localhost:8000/tasks/{id}/status?status=completed"  
      
    kubectl logs -l app=task-api -c task-api | grep "Notification"  
    
    
    
    Notification sent for task abc-123  
    

**SC-5: Zero infrastructure imports**
    
    
    grep -E "import redis|import confluent_kafka|import httpx" main.py models.py  
    

No output. No matches. That is the point.

## What You Built​

Building Block| Replaces| API Call  
---|---|---  
State Management| `redis-py`| `client.save_state()` / `client.get_state()`  
Pub/Sub| `confluent-kafka`| `client.publish_event()`  
Service Invocation| `httpx`| `client.invoke_method()`  
Secrets| `os.getenv()`| `client.get_secret()`  
Subscription| Manual consumer loop| `@dapr_app.subscribe()`  
  
Five building blocks, one `DaprClient`, zero infrastructure imports. Swap Redis for PostgreSQL by changing `statestore.yaml`. Swap Redis pub/sub for Kafka by changing `pubsub.yaml`. Your Python code does not change.

* * *

## Reflect on Your Skill​

You built a `dapr-deployment` skill in Lesson 01 and refined it through Lessons 03-08. This capstone is the test.
    
    
    Using my dapr-deployment skill, refactor this FastAPI service to use Dapr:  
    1. Replace redis-py with Dapr state API  
    2. Replace Kafka producer with Dapr pub/sub  
    3. Replace httpx service calls with Dapr service invocation  
    4. Create a Kubernetes Deployment (not bare Pod) with Dapr annotations  
    5. Include sidecar readiness wait in lifespan  
      
    Does my skill produce a complete, deployable service?  
    

If your skill missed the `client.wait()` pattern, the ETag concurrency, or the programmatic subscription via `dapr-ext-fastapi`, update it now. Those are the patterns that separate a working deployment from one that fails intermittently.

* * *

## Try With AI​

**Prompt 1: State migration with concurrency**
    
    
    I have a FastAPI Task API using redis-py directly.  
    Show me how to migrate to Dapr state management with:  
    - save_state / get_state / delete_state replacing redis set/get/delete  
    - ETag-based optimistic concurrency on updates  
    - The statestore component YAML for Redis backend  
    

**What you're learning:** The state migration pattern. ETags give you concurrency control that required manual implementation with raw Redis. Dapr provides it automatically.

**Prompt 2: Pub/sub with programmatic subscription**
    
    
    My Task API saves tasks but publishes no events.  
    Add Dapr pub/sub with:  
    - publish_event after create and status change  
    - A subscription handler using dapr-ext-fastapi @dapr_app.subscribe  
    - Service invocation to notification-service inside the handler  
    - The Redis pub/sub component YAML  
    

**What you're learning:** Event-driven composition. The subscription handler receives events and invokes another service, both through Dapr. Two building blocks composed without a single infrastructure import.

**Prompt 3: Production deployment with sidecar verification**
    
    
    I have a working Dapr-enabled Task API.  
    Deploy it to Kubernetes with:  
    - Deployment resource (2 replicas), not a bare Pod  
    - All required Dapr annotations  
    - Readiness probe on /health  
    - client.wait(timeout_s=30) in FastAPI lifespan  
    - Commands to verify 2/2 READY and test via port-forward  
    

**What you're learning:** Production deployment patterns. The `Deployment` with replicas and readiness probes is how real services run. The sidecar injection via annotations means your application never installs Dapr directly; Kubernetes handles it.

**Safety note:** When migrating production services to Dapr, run both implementations in parallel during the transition period. Direct clients and Dapr can coexist temporarily, letting you migrate one service at a time and roll back if needed.