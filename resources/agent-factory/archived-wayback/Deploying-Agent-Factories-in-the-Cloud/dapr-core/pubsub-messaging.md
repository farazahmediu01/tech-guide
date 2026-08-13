# Pub/Sub Messaging

> **Archived from:** <https://agentfactory.panaversity.org/docs/Deploying-Agent-Factories-in-the-Cloud/dapr-core/pubsub-messaging>  
> **Wayback snapshot:** 2026-04-22  
> **Status:** retired from the live site — recovered for offline study.

---

Service invocation solves one-to-one communication: service A calls service B and waits for a response. Many real workloads need a different pattern. When a task is created, you might need to notify an analytics service, trigger an email, and update a dashboard. The publisher should not know or care which services are listening.

Dapr's pub/sub building block decouples publishers from subscribers. Your app publishes an event to a topic. Zero, one, or twenty services can subscribe to that topic independently. The broker (Redis, Kafka, RabbitMQ) is configured in YAML, never in application code.

In this lesson you will build two separate apps: a **publisher** (task-api) that fires events when tasks are created, and a **subscriber** (task-worker) that receives those events. You will deploy both to Kubernetes, test the full flow, and then see how swapping Redis for Kafka requires zero code changes.

Prerequisite Check

Dapr, Redis, and the state store component must still be running from Lesson 3. Verify:
    
    
    kubectl get pods -l app=redis  
    dapr components -k  
    

You should see the Redis pod running and the `statestore` component listed. If not, re-apply them from Lesson 3 before continuing.

## Pub/Sub vs Service Invocation​

Aspect| Service Invocation| Pub/Sub  
---|---|---  
Pattern| Request/Response (sync)| Fire-and-forget (async)  
Coupling| Caller knows target app-id| Publisher doesn't know subscribers  
Use case| "Call notification service now"| "Announce task was created"  
Scaling| 1-to-1| 1-to-many  
  
Service invocation: "Hey notification-service, send this email." Pub/sub: "A task was created. Anyone who cares, here it is."

## Step 1: Create the Pub/Sub Component​

Redis is already running from the state management lesson. Create a pub/sub component that reuses it:
    
    
    # pubsub.yaml  
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
    

Apply it:
    
    
    kubectl apply -f pubsub.yaml  
    
    
    
    component.dapr.io/pubsub created  
    

Component Before Pods

Apply the pub/sub component **before** deploying your app pods. If pods start before the component exists, the Dapr sidecar cannot find the `pubsub` component and will log errors. The sidecar does not retry component discovery after startup.

## Step 2: Build the Publisher (task-api)​

### Project setup​
    
    
    mkdir task-api && cd task-api  
    uv init .  
    uv add "fastapi[standard]" dapr  
    

Package Name

The pip package is `dapr`, not `dapr-client`. Installing `dapr-client` gives you an older, incompatible version.

### Application code​
    
    
    # task-api/main.py  
    from dapr.clients import DaprClient  
    from fastapi import FastAPI  
    from pydantic import BaseModel  
    import json  
    import uuid  
      
    app = FastAPI()  
      
    class Task(BaseModel):  
        title: str  
      
    @app.post("/tasks")  
    async def create_task(task: Task):  
        task_id = str(uuid.uuid4())  
        with DaprClient() as client:  
            client.publish_event(  
                pubsub_name="pubsub",  
                topic_name="task-events",  
                data=json.dumps({  
                    "event_type": "task.created",  
                    "task_id": task_id,  
                    "title": task.title,  
                }),  
                data_content_type="application/json",  
            )  
        return {"id": task_id, "title": task.title, "event": "published"}  
    

Note the pattern: `with DaprClient() as client:` (synchronous context manager). Not `async with`. The Dapr Python SDK's `DaprClient` uses a synchronous gRPC channel.

### Dockerfile​
    
    
    # task-api/Dockerfile  
    FROM python:3.12-slim  
    COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv  
    WORKDIR /app  
    COPY pyproject.toml uv.lock ./  
    RUN uv sync --frozen --no-dev  
    COPY main.py .  
    CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  
    

### Deployment YAML​
    
    
    # task-api-deployment.yaml  
    apiVersion: apps/v1  
    kind: Deployment  
    metadata:  
      name: task-api  
      namespace: default  
    spec:  
      replicas: 1  
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
        spec:  
          containers:  
            - name: task-api  
              image: task-api:latest  
              imagePullPolicy: Never  
              ports:  
                - containerPort: 8000  
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
    

### Build and deploy​
    
    
    docker build -t task-api:latest ./task-api  
    kubectl apply -f task-api-deployment.yaml  
    
    
    
    deployment.apps/task-api created  
    service/task-api created  
    

Verify the pod is running with both containers (app + daprd sidecar):
    
    
    kubectl get pods -l app=task-api  
    
    
    
    NAME                        READY   STATUS    RESTARTS   AGE  
    task-api-7d4f8b6c9-x2k4m   2/2     Running   0          30s  
    

`2/2` confirms the Dapr sidecar injected successfully.

## Step 3: Build the Subscriber (task-worker)​

Dapr supports two subscription approaches. You will see both.

### Approach A: Declarative Subscription (Kubernetes CRD)​

Define the subscription as a Kubernetes resource:
    
    
    # task-subscription.yaml  
    apiVersion: dapr.io/v2alpha1  
    kind: Subscription  
    metadata:  
      name: task-subscription  
      namespace: default  
    spec:  
      pubsubname: pubsub  
      topic: task-events  
      routes:  
        default: /events/todo  
    

The subscriber app just needs a plain FastAPI endpoint at that route:
    
    
    # task-worker/main.py (declarative approach)  
    from fastapi import FastAPI  
    import logging  
      
    logging.basicConfig(level=logging.INFO)  
    logger = logging.getLogger(__name__)  
      
    app = FastAPI()  
      
    @app.post("/events/todo")  
    async def handle_task_event(event_data: dict):  
        data = event_data.get("data", event_data)  
        logger.info(f"EVENT RECEIVED: {data}")  
        return {"status": "SUCCESS"}  
    

Apply both the subscription CRD and deploy the app. The CRD tells Dapr which topic maps to which route; your code never references Dapr directly.

### Approach B: Programmatic Subscription (dapr-ext-fastapi)​

No CRD needed. The subscription is declared in code:
    
    
    uv add dapr-ext-fastapi  
    
    
    
    # task-worker/main.py (programmatic approach)  
    from fastapi import FastAPI  
    from dapr.ext.fastapi import DaprApp  
    import logging  
      
    logging.basicConfig(level=logging.INFO)  
    logger = logging.getLogger(__name__)  
      
    app = FastAPI()  
    dapr_app = DaprApp(app)  
      
    @dapr_app.subscribe(pubsub="pubsub", topic="task-events")  
    async def handle_task_event(event_data: dict):  
        logger.info(f"EVENT RECEIVED: {event_data}")  
        return {"status": "SUCCESS"}  
    

The `@dapr_app.subscribe` decorator registers the subscription with the Dapr sidecar at startup. When Dapr queries the app for subscriptions (via `/dapr/subscribe`), the extension responds automatically.

**Which approach to use:**

Approach| Best for  
---|---  
**Declarative (CRD)**|  GitOps, ops-managed routing, subscription changes without redeploying code  
**Programmatic**|  Developer-controlled, subscription lives with handler code, simpler deploys  
  
For this lesson, use the **programmatic approach** so everything is visible in one file.

### Subscriber Dockerfile and deployment​
    
    
    # task-worker/Dockerfile  
    FROM python:3.12-slim  
    COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv  
    WORKDIR /app  
    COPY pyproject.toml uv.lock ./  
    RUN uv sync --frozen --no-dev  
    COPY main.py .  
    CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]  
    
    
    
    # task-worker-deployment.yaml  
    apiVersion: apps/v1  
    kind: Deployment  
    metadata:  
      name: task-worker  
      namespace: default  
    spec:  
      replicas: 1  
      selector:  
        matchLabels:  
          app: task-worker  
      template:  
        metadata:  
          labels:  
            app: task-worker  
          annotations:  
            dapr.io/enabled: "true"  
            dapr.io/app-id: "task-worker"  
            dapr.io/app-port: "8001"  
        spec:  
          containers:  
            - name: task-worker  
              image: task-worker:latest  
              imagePullPolicy: Never  
              ports:  
                - containerPort: 8001  
    

### Build and deploy​
    
    
    mkdir task-worker && cd task-worker  
    uv init .  
    uv add "fastapi[standard]" dapr dapr-ext-fastapi  
    # (create main.py and Dockerfile as shown above)  
      
    docker build -t task-worker:latest ./task-worker  
    kubectl apply -f task-worker-deployment.yaml  
    

Verify both pods are running:
    
    
    kubectl get pods -l 'app in (task-api, task-worker)'  
    
    
    
    NAME                           READY   STATUS    RESTARTS   AGE  
    task-api-7d4f8b6c9-x2k4m      2/2     Running   0          2m  
    task-worker-5b8c7d3a1-r9n2p   2/2     Running   0          30s  
    

## Step 4: Test End-to-End​

Port-forward to the publisher:
    
    
    kubectl port-forward svc/task-api 8000:80  
    

In another terminal, publish a task:
    
    
    curl -X POST http://localhost:8000/tasks \  
      -H "Content-Type: application/json" \  
      -d '{"title": "Learn Dapr pub/sub"}'  
    
    
    
    { "id": "a1b2c3d4-...", "title": "Learn Dapr pub/sub", "event": "published" }  
    

Check the subscriber logs:
    
    
    kubectl logs -l app=task-worker -c task-worker --tail=20  
    
    
    
    INFO:__main__:EVENT RECEIVED: {'event_type': 'task.created', 'task_id': 'a1b2c3d4-...', 'title': 'Learn Dapr pub/sub'}  
    

The publisher and subscriber have no knowledge of each other. The publisher calls `publish_event` on its local Dapr sidecar. The subscriber's sidecar pulls from Redis and delivers to the `/events/todo` handler. Redis is the only shared dependency, and neither app imports a Redis client.

## Subscription Response Patterns​

Your handler's return value tells Dapr what to do with the message:

Status| Dapr behavior  
---|---  
`SUCCESS`| Message acknowledged, removed from broker  
`RETRY`| Message redelivered after backoff  
`DROP`| Message discarded permanently, no retry  
      
    
    @dapr_app.subscribe(pubsub="pubsub", topic="task-events")  
    async def handle_task_event(event_data: dict):  
        try:  
            process_event(event_data)  
            return {"status": "SUCCESS"}  
        except TransientError:  
            return {"status": "RETRY"}    # network blip, try again  
        except PermanentError:  
            return {"status": "DROP"}     # bad data, discard  
    

Default to `RETRY` over `DROP` for anything that matters. Let the broker's dead-letter handling catch truly unprocessable messages.

## CloudEvents Format​

Dapr wraps every published message in [CloudEvents](<https://cloudevents.io/>) format automatically.

**What you publish:**
    
    
    { "event_type": "task.created", "task_id": "abc-123", "title": "Learn Dapr" }  
    

**What the subscriber receives:**
    
    
    {  
      "specversion": "1.0",  
      "type": "com.dapr.event.sent",  
      "source": "task-api",  
      "id": "unique-event-id",  
      "datacontenttype": "application/json",  
      "data": {  
        "event_type": "task.created",  
        "task_id": "abc-123",  
        "title": "Learn Dapr"  
      }  
    }  
    

Your original payload is nested inside `data`. The outer envelope adds traceability (`id`, `source`, `time`) and interoperability (any CloudEvents-aware system can parse it). You never construct this envelope yourself; Dapr handles it.

When using `dapr-ext-fastapi`, the extension unwraps the CloudEvents envelope and passes only the `data` field to your handler. With the declarative CRD approach, your handler receives the full envelope, so access the payload via `event_data.get("data", event_data)`.

## Swapping Brokers: Redis to Kafka​

Replace the component YAML. Application code stays identical.
    
    
    # pubsub-kafka.yaml  
    apiVersion: dapr.io/v1alpha1  
    kind: Component  
    metadata:  
      name: pubsub  
      namespace: default  
    spec:  
      type: pubsub.kafka  
      version: v1  
      metadata:  
        - name: brokers  
          value: kafka-bootstrap.kafka.svc.cluster.local:9092  
        - name: consumerGroup  
          value: task-service  
        - name: authType  
          value: none  
    
    
    
    kubectl apply -f pubsub-kafka.yaml  
    kubectl rollout restart deployment task-api task-worker  
    

Same `publish_event()` call. Same `@dapr_app.subscribe()` decorator. Different broker. This is why Dapr matters for production systems that need to evolve infrastructure without touching application code.

Broker| Use case  
---|---  
**Redis**|  Dev/local, simple pub/sub, low latency  
**Kafka**|  Production event streaming, replay, high throughput  
**RabbitMQ**|  Complex routing, message queuing patterns  
**Cloud (SNS/SQS, GCP Pub/Sub)**|  Managed infrastructure  
  
## Troubleshooting​

Symptom| Cause| Fix  
---|---|---  
`ERR_PUBSUB_NOT_FOUND` in sidecar logs| Component not applied or wrong name| `kubectl get components` and verify `pubsub` exists  
Publisher returns 500| Sidecar not ready, pod shows 1/2 containers| Wait for `2/2 READY` or check `dapr.io/enabled` annotation  
Subscriber never receives events| Subscription not registered| Check `dapr.io/app-port` matches your app's actual port  
Events delivered but handler returns 404| Route mismatch| CRD route must match your `@app.post` path exactly  
`connection refused` on publish| DaprClient can't reach sidecar| Verify sidecar is running: `kubectl describe pod <name>`  
Duplicate events after restart| Redis redelivering unacknowledged messages| Return `SUCCESS` from your handler; check for handler exceptions  
  
## Cleanup​

Delete the publisher and subscriber deployments:
    
    
    kubectl delete -f task-api-deployment.yaml  
    kubectl delete -f task-worker-deployment.yaml  
    kubectl delete -f task-subscription.yaml 2>/dev/null  # if you applied the CRD  
    

**Keep the following for the next lesson** (Bindings and Triggers):

  * The Dapr installation
  * Redis and the `pubsub` component
  * The `statestore` component from Lesson 3


* * *

## Reflect on Your Skill​

You built a `dapr-deployment` skill in Lesson 0. Test and improve it based on what you learned.

### Test Your Skill​
    
    
    Using my dapr-deployment skill, add pub/sub messaging to a new service:  
    1. Create a Redis pub/sub component  
    2. Publish events using DaprClient (sync context manager)  
    3. Implement a subscription handler using dapr-ext-fastapi  
      
    Does my skill use `with DaprClient()` (not `async with`)?  
    Does it show the full build/deploy pipeline (Dockerfile + deployment YAML)?  
    

### Identify Gaps​

Ask yourself:

  * Did my skill warn that the pubsub component must exist before pods start?
  * Did it show subscription response patterns (SUCCESS, RETRY, DROP)?
  * Did it include the broker-swap pattern (Redis to Kafka, zero code changes)?


### Improve Your Skill​

If you found gaps:
    
    
    My dapr-deployment skill is missing pub/sub patterns.  
    Update it to include:  
    - with DaprClient() as client: publish_event() (sync pattern)  
    - dapr-ext-fastapi @dapr_app.subscribe() decorator  
    - Redis and Kafka component YAML examples  
    - Subscription response status meanings (SUCCESS/RETRY/DROP)  
    - Warning: apply component YAML before deploying app pods  
    

* * *

## Try With AI​

**Setup:** You have two services that currently communicate via direct HTTP calls. You want to decouple them using Dapr pub/sub.

**Prompt 1: Build a publisher from scratch**
    
    
    Build a FastAPI publisher service that fires events through Dapr pub/sub.  
      
    Requirements:  
    - POST /orders endpoint accepts {"product": "...", "quantity": N}  
    - Publishes an "order.created" event to a "order-events" topic  
    - Uses with DaprClient() as client: (sync context manager)  
    - Include the Redis pubsub component YAML  
    - Include Dockerfile and Kubernetes deployment YAML with Dapr annotations  
    

**What you're learning:** The full publisher pipeline from code to cluster. You are practicing the component-first, then code, then deploy ordering that prevents the `ERR_PUBSUB_NOT_FOUND` error.

* * *

**Prompt 2: Add a subscriber with error handling**
    
    
    Build a subscriber service for my "order-events" topic using dapr-ext-fastapi.  
      
    Requirements:  
    - @dapr_app.subscribe decorator (programmatic, no CRD)  
    - Handle events with SUCCESS/RETRY/DROP response patterns  
    - Return RETRY for transient errors, DROP for validation failures  
    - Include Dockerfile and deployment YAML  
    - Show me how to verify events are flowing via kubectl logs  
    

**What you're learning:** Subscription wiring and resilience patterns. The response statuses give you control over message lifecycle without touching broker-specific configuration.

* * *

**Prompt 3: Swap Redis for Kafka**
    
    
    I have a working Dapr pub/sub setup using Redis. Show me exactly what changes  
    to switch to Kafka as the broker.  
      
    Show:  
    1. Current Redis component YAML  
    2. New Kafka component YAML (same component name)  
    3. The kubectl commands to apply the swap  
    4. Confirmation that zero application code changes are needed  
    

**What you're learning:** Infrastructure portability through configuration. The component name stays `pubsub`, the application code references `pubsub`, and only the YAML spec changes. This is the core value proposition of Dapr's building block abstraction.

**Safety note:** When testing pub/sub in shared environments, use isolated topic names (e.g., `task-events-dev-yourname`). Publishing to production topics during development can trigger real workflows: notifications sent, orders processed, analytics skewed.