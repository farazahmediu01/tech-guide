# Service Invocation

> **Archived from:** <https://agentfactory.panaversity.org/docs/Deploying-Agent-Factories-in-the-Cloud/dapr-core/service-invocation>  
> **Wayback snapshot:** 2026-05-21  
> **Status:** retired from the live site — recovered for offline study.

---

Your todo-api saves state to Redis through Dapr. It works. One service, one sidecar, one store.

Real systems don't stop there. When a task is created, someone needs to be notified. When a task completes, a billing service needs to know. Microservices talk to each other constantly, and every call raises the same questions: How do I find the other service? What if it moved? How do I secure the traffic? What if it's temporarily down?

Dapr answers all of them with one API call. Your code says `invoke_method(app_id='notification-service', method_name='notify')`. Dapr handles discovery, load balancing, mTLS encryption, and retries. You never know where the target service lives or how to reach it securely.

By the end of this lesson, your todo-api will call a notification-service through Dapr, and you'll have built, containerized, and deployed both services on your cluster.

Prerequisite

This lesson assumes Dapr and Redis are still running from Lesson 3. If you cleaned up, re-deploy them before continuing. You also need the `dapr-state-app` pattern from L03 as a reference.

## Build the Notification Service​

You are building a second microservice. Same pipeline as L03: write the code, containerize it, deploy it with Dapr annotations.

### Step 1: Create the Project​
    
    
    uv init notification-service  
    cd notification-service  
    uv add "fastapi[standard]" dapr  
    

Package Name

Use `dapr`, not `dapr-client`. The `dapr-client` package on PyPI is an abandoned beta that only contains `proto/` stubs. The correct SDK is `dapr>=1.14`.

### Step 2: The App Code​

Create `notification-service/main.py`:
    
    
    # main.py  
    from fastapi import FastAPI  
    from pydantic import BaseModel  
    import logging  
      
    logging.basicConfig(level=logging.INFO)  
    logger = logging.getLogger(__name__)  
      
    app = FastAPI()  
      
    class NotificationRequest(BaseModel):  
        message: str  
        task_id: str | None = None  
      
    @app.post("/notify")  
    async def notify(request: NotificationRequest):  
        """Receive notification from other services."""  
        logger.info(f"Notification received: {request.message}")  
        # In production: send email, push notification, Slack message  
        return {  
            "status": "delivered",  
            "message": request.message  
        }  
      
    @app.get("/health")  
    async def health():  
        return {"status": "healthy"}  
    

Nothing Dapr-specific in this code. It's a plain FastAPI service on port 8001. Dapr's sidecar handles all the distributed systems concerns.

### Step 3: Containerize​

Create `notification-service/Dockerfile`:
    
    
    FROM python:3.12-slim AS builder  
      
    COPY --from=ghcr.io/astral-sh/uv:0.7 /uv /usr/local/bin/uv  
      
    WORKDIR /app  
    COPY pyproject.toml uv.lock ./  
    RUN uv sync --no-dev --no-install-project --frozen  
    COPY main.py .  
    RUN uv sync --no-dev --frozen  
      
      
    FROM python:3.12-slim  
      
    RUN addgroup --system --gid 1001 appgroup && \  
        adduser --system --uid 1001 --ingroup appgroup appuser  
      
    WORKDIR /app  
    COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv  
    COPY --chown=appuser:appgroup main.py .  
      
    ENV PATH="/app/.venv/bin:$PATH"  
    USER appuser  
    EXPOSE 8001  
      
    CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]  
    

### Step 4: Build and Load​
    
    
    docker build -t notification-service:latest .  
    

If you're running k3s instead of Docker Desktop Kubernetes, you need to import the image into containerd:
    
    
    # k3s only — Docker Desktop Kubernetes uses Docker's image store directly  
    docker save notification-service:latest | sudo k3s ctr images import -  
    

### Step 5: Deploy with Dapr Annotations​

Create `notification-service/deployment.yaml`:
    
    
    apiVersion: apps/v1  
    kind: Deployment  
    metadata:  
      name: notification-service  
      labels:  
        app: notification-service  
    spec:  
      replicas: 1  
      selector:  
        matchLabels:  
          app: notification-service  
      template:  
        metadata:  
          labels:  
            app: notification-service  
          annotations:  
            dapr.io/enabled: "true"  
            dapr.io/app-id: "notification-service"  
            dapr.io/app-port: "8001"  
        spec:  
          containers:  
            - name: app  
              image: notification-service:latest  
              imagePullPolicy: Never  
              ports:  
                - containerPort: 8001  
    

Deployment, not Pod

Use `kind: Deployment`, not a bare `Pod`. On Dapr 1.17+, the operator only auto-creates the `<app-id>-dapr` headless Service (which `invoke_method` resolves via DNS) for workloads managed by a Deployment or StatefulSet. Deploying as a bare Pod leaves callers failing with `no such host` on `notification-service-dapr.default.svc.cluster.local`.

Three annotations make this a Dapr-enabled service:

Annotation| Purpose  
---|---  
`dapr.io/enabled: "true"`| Triggers sidecar injection  
`dapr.io/app-id: "notification-service"`| Unique name for service discovery  
`dapr.io/app-port: "8001"`| Port your app listens on (sidecar forwards traffic here)  
  
Deploy and verify:
    
    
    kubectl apply -f deployment.yaml  
    kubectl rollout status deployment/notification-service  
    kubectl get pods -l app=notification-service  
    

**Output:**
    
    
    NAME                                    READY   STATUS    RESTARTS   AGE  
    notification-service-xxxxxxxxxx-yyyyy   2/2     Running   0          30s  
    

`2/2` means two containers: your app and the Dapr sidecar. If you see `1/2`, the sidecar is still starting. If `0/2`, check logs (grab the pod name from `kubectl get pods -l app=notification-service`):
    
    
    POD=$(kubectl get pod -l app=notification-service -o jsonpath='{.items[0].metadata.name}')  
    kubectl logs "$POD" -c app  
    kubectl logs "$POD" -c daprd  
    

Verify the Dapr operator created the headless Service that `invoke_method` resolves:
    
    
    kubectl get svc notification-service-dapr  
    # NAME                        TYPE        CLUSTER-IP   PORT(S)  
    # notification-service-dapr   ClusterIP   None         80/TCP,50001/TCP,50002/TCP,9090/TCP  
    

If that Service is missing, the workload is likely a bare Pod — convert it to a Deployment.

## Call It from Todo-API​

Now update `dapr-state-app` to call notification-service when a todo is created. This is the `invoke_method()` pattern.

Open `dapr-state-app/main.py` (the app you built in L03) and add the invocation to `create_todo`:
    
    
    # main.py  (additions shown — keep the rest of your L03 code)  
    from dapr.clients import DaprClient  
    import json  
    import uuid  
      
    @app.post("/todos")  
    def create_todo(todo: Todo):  
        todo.id = str(uuid.uuid4())  
      
        with DaprClient() as client:  
            # Save state (from L03)  
            client.save_state(  
                store_name=STORE,  
                key=f"todo-{todo.id}",  
                value=todo.model_dump_json(),  
            )  
      
            # Notify via service invocation  
            response = client.invoke_method(  
                app_id="notification-service",  
                method_name="notify",  
                http_verb="POST",  
                data=json.dumps({  
                    "message": f"Todo created: {todo.title}",  
                    "task_id": todo.id,  
                }),  
                content_type="application/json",  
            )  
      
            print(f"Notification response: {response.text()}")  
      
        return todo  
    

The `invoke_method()` parameters:

Parameter| Value| What It Does  
---|---|---  
`app_id`| `'notification-service'`| Target service's `dapr.io/app-id`  
`method_name`| `'notify'`| Endpoint path on target service  
`http_verb`| `'POST'`| HTTP method  
`data`| JSON string| Request body  
`content_type`| `'application/json'`| Content-Type header  
  
Rebuild, redeploy, and test:
    
    
    # Rebuild dapr-state-app  
    cd ../dapr-state-app  
    docker build -t dapr-state-app:latest .  
      
    # For k3s: docker save dapr-state-app:latest | sudo k3s ctr images import -  
      
    # Restart to pick up the new image  
    kubectl rollout restart deployment/dapr-state-app  
    kubectl rollout status deployment/dapr-state-app  
    

Once both workloads show `2/2`:
    
    
    # Port-forward to dapr-state-app  
    kubectl port-forward deployment/dapr-state-app 8000:8000 &  
      
    # Create a todo — this triggers the notification  
    curl -X POST http://localhost:8000/todos \  
      -H "Content-Type: application/json" \  
      -d '{"title": "Buy groceries"}'  
    

**Output:**
    
    
    { "id": "a1b2c3d4-...", "title": "Buy groceries", "status": "pending" }  
    

Check the notification-service received it:
    
    
    NOTIF_POD=$(kubectl get pod -l app=notification-service -o jsonpath='{.items[0].metadata.name}')  
    kubectl logs "$NOTIF_POD" -c app  
    

**Output:**
    
    
    INFO:     Notification received: Todo created: Buy groceries  
    

Two services. One `invoke_method()` call. No hardcoded URLs, no certificate management, no service registry configuration.

## How It Works Behind the Scenes​

You've seen it work. Here's what Dapr did for you.

### Service Discovery​

When todo-api calls `invoke_method(app_id='notification-service')`, the request flows through two sidecars:
    
    
    todo-api (app) → todo-api sidecar → [name resolution] → notification-service sidecar → notification-service (app)  
    

On Kubernetes, each service announces itself using its `dapr.io/app-id` annotation. Dapr resolves `notification-service` to the correct pod automatically. If notification-service scales to 10 replicas, Dapr load-balances across them. You change nothing in your code.

### Automatic mTLS​

Every call between sidecars is encrypted. The **Dapr Sentry** service acts as a Certificate Authority: when each sidecar starts, it requests a certificate from Sentry, and all sidecar-to-sidecar traffic uses mTLS. Certificate rotation happens automatically. You write zero TLS code.

## Alternative: HTTP with dapr-app-id Header​

If you prefer raw HTTP over the Python SDK, use the `dapr-app-id` header:
    
    
    import httpx  
    import os  
      
    DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")  
      
    async def notify_via_http(message: str, task_id: str):  
        """Call notification-service using HTTP with dapr-app-id header."""  
        async with httpx.AsyncClient() as client:  
            response = await client.post(  
                f"http://localhost:{DAPR_HTTP_PORT}/notify",  
                json={"message": message, "task_id": task_id},  
                headers={"dapr-app-id": "notification-service"}  
            )  
            return response.json()  
    

The `dapr-app-id` header tells your sidecar which service to route to. This is equivalent to the `/v1.0/invoke/{app-id}/method/{method}` endpoint pattern. Both approaches go through the sidecar; pick whichever fits your codebase.

## Troubleshooting​

When `invoke_method()` fails, the error tells you what went wrong:

Symptom| Cause| Fix  
---|---|---  
`ERR_DIRECT_INVOKE: app-id notification-service not found`| Target service not running or wrong app-id| `kubectl get pods`, verify `dapr.io/app-id` annotation spelling  
`connection refused`| Target service's app-port incorrect| Verify `dapr.io/app-port` matches the port your app listens on  
`DEADLINE_EXCEEDED`| Target service too slow to respond| Check target health; increase timeout  
Pod shows `1/2` Ready| Sidecar injected but app container crashing| `kubectl logs <pod> -c app` for the Python traceback  
Pod shows `0/2` Error| Both containers failing| Check daprd logs first: `kubectl logs <pod> -c daprd`  
`ModuleNotFoundError: No module named 'dapr.clients'`| Wrong PyPI package installed| Use `dapr`, not `dapr-client`  
  
Enable API logging to trace invocation details:
    
    
    annotations:  
      dapr.io/enable-api-logging: "true"  
    

Then check sidecar logs:
    
    
    kubectl logs deployment/dapr-state-app -c daprd | grep invoke  
    

**Output:**
    
    
    level=info msg="HTTP API Called" method=POST app_id=notification-service method=notify  
    

## Cleanup​

Remove the notification-service when you're done. Keep Dapr and Redis running for Lesson 5.
    
    
    kubectl delete deployment notification-service  
      
    # Verify  
    kubectl get pods  
    # Should show only dapr-state-app (2/2) and redis  
    

* * *

## Reflect on Your Skill​

You built a `dapr-deployment` skill in Lesson 0. Update it with service invocation patterns.

### Add to Your Skill​
    
    
    Update my dapr-deployment skill with service invocation patterns:  
    1. invoke_method() Python SDK usage  
    2. Required annotations: dapr.io/enabled, dapr.io/app-id, dapr.io/app-port  
    3. Alternative: dapr-app-id HTTP header pattern  
    4. Common errors: ERR_DIRECT_INVOKE, connection refused  
    5. Debugging: enable-api-logging annotation  
    

### Test Your Improved Skill​
    
    
    Using my dapr-deployment skill, generate code for a billing-service  
    that todo-api calls when a task is marked complete. Include:  
    - The full build/deploy pipeline (code, Dockerfile, Pod YAML)  
    - invoke_method() call from todo-api  
    - Error handling for invocation failures  
    

* * *

## Try With AI​

### Prompt 1: Deploy Both Services​
    
    
    My todo-api (from Lesson 3) needs to call notification-service when  
    a todo is created. Walk me through the full pipeline:  
    1. notification-service code (FastAPI, port 8001)  
    2. Dockerfile and build command  
    3. Pod YAML with Dapr annotations  
    4. invoke_method() call from todo-api  
    5. How to verify the call worked (logs from both sides)  
    

**What you're learning:** The complete service invocation pattern from code through deployment. One line of Python replaces pages of service mesh configuration. The sidecar handles discovery, encryption, and retries.

### Prompt 2: Debug a Broken Invocation​
    
    
    My invoke_method() call fails with:  
    "ERR_DIRECT_INVOKE: app-id notification-service not found"  
      
    But kubectl get pods shows notification-service running. Walk me  
    through systematic debugging:  
    1. What to check first  
    2. How to verify sidecar injection  
    3. How to check annotation spelling  
    4. How to use daprd logs to trace the invocation path  
    

**What you're learning:** The pod running doesn't mean the Dapr sidecar is healthy or that the app-id matches. You'll learn to verify sidecar injection (`2/2` Ready), check annotation spelling, and use `kubectl logs <pod> -c daprd` to trace failures.

### Prompt 3: Add a Third Service​
    
    
    I have todo-api calling notification-service. Now I want to add a  
    billing-service that todo-api calls when a task is marked complete.  
    Generate:  
    - billing-service code (port 8002)  
    - Dockerfile and deployment YAML  
    - Updated todo-api with invoke_method() to billing-service  
    - How to verify all three services can communicate  
    

**What you're learning:** Adding a third service is the same pattern repeated. Same annotations, same `invoke_method()`, same sidecar injection. Dapr scales horizontally because every service follows identical conventions.

**Safety note:** When testing service invocation between different namespaces, Dapr scopes invocation to the same namespace by default. Cross-namespace calls require explicit configuration in your Dapr configuration resource.