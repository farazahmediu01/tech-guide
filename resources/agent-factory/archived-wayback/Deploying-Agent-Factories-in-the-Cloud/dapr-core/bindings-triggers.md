# Bindings and Triggers

> **Archived from:** <https://agentfactory.panaversity.org/docs/Deploying-Agent-Factories-in-the-Cloud/dapr-core/bindings-triggers>  
> **Wayback snapshot:** 2026-04-20  
> **Status:** retired from the live site — recovered for offline study.

---

In Lesson 5, you used pub/sub to connect Dapr services to each other. Both publisher and subscriber were applications running inside your cluster. But production systems talk to the outside world: a cron schedule fires a cleanup job at midnight, a webhook arrives from a payment provider, your app pushes alerts to PagerDuty. None of these are Dapr applications. Pub/sub cannot reach them.

**Bindings** bridge this gap. An **input binding** lets an external event trigger your code (cron tick, S3 upload, incoming webhook). An **output binding** lets your code invoke an external system (HTTP POST, send email, write to S3). The API is the same pattern you have been using all chapter: configure a YAML component, call a Dapr endpoint.

Prerequisites

You need the Dapr environment from Lessons 3-5: `dapr`, `docker`, Redis running, and the `pubsub` component from Lesson 5. If you skipped ahead, go back and complete Lesson 3 first.

* * *

## Bindings vs Pub/Sub​

One question before you build anything: when do you use bindings instead of pub/sub?

Question| Answer| Use  
---|---|---  
Is the other system a Dapr-enabled microservice?| Yes| Pub/Sub  
Is the other system external (cron, S3, webhook, email)?| Yes| Bindings  
  
That is the entire decision. Pub/sub connects your microservices. Bindings connect to everything else.

* * *

## Lab A: Cron Input Binding​

A cron input binding makes Dapr call your application on a schedule. No external infrastructure required. You configure the schedule in YAML, and Dapr POSTs to your endpoint every time it fires.

### Step 1: Create the Component​

Create `components/cron-binding.yaml`:
    
    
    apiVersion: dapr.io/v1alpha1  
    kind: Component  
    metadata:  
      name: cleanup-cron  
    spec:  
      type: bindings.cron  
      version: v1  
      metadata:  
        - name: schedule  
          value: "@every 30s"  
        - name: direction  
          value: "input"  
    

The component name is `cleanup-cron`. Remember this name.

### Step 2: Write the Handler​

Create `app.py`:
    
    
    from fastapi import FastAPI  
    from datetime import datetime  
    import logging  
      
    logging.basicConfig(level=logging.INFO)  
    logger = logging.getLogger(__name__)  
      
    app = FastAPI()  
      
    @app.post("/cleanup-cron")  # MUST match component metadata.name  
    async def handle_cron():  
        logger.info(f"CRON TRIGGERED at {datetime.now().isoformat()}")  
        return {"status": "OK"}  
    

Critical Gotcha

The endpoint path **must** match the component's `metadata.name` exactly. The component is named `cleanup-cron`, so the endpoint must be `POST /cleanup-cron`. If these don't match, Dapr will call an endpoint that doesn't exist and you will see 404 errors in the sidecar logs with no indication of what went wrong.

### Step 3: Create the Dockerfile​
    
    
    FROM python:3.12-slim  
    WORKDIR /app  
    RUN pip install fastapi uvicorn  
    COPY app.py .  
    CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]  
    

### Step 4: Build and Deploy​
    
    
    # Build the image  
    docker build -t cron-binding-app .  
      
    # Run with Dapr sidecar  
    dapr run \  
      --app-id cron-app \  
      --app-port 8000 \  
      --resources-path ./components \  
      -- uvicorn app:app --host 0.0.0.0 --port 8000  
    

### Step 5: Watch the Logs​

Within 30 seconds, you should see output like:
    
    
    == APP == INFO:     CRON TRIGGERED at 2025-12-29T10:30:00.123456  
    == APP == INFO:     CRON TRIGGERED at 2025-12-29T10:30:30.124789  
    == APP == INFO:     CRON TRIGGERED at 2025-12-29T10:31:00.125012  
    

Every 30 seconds, Dapr sends a POST request to `/cleanup-cron`. Your application does not poll. It does not maintain a timer. It just handles incoming requests.

Stop the app with `Ctrl+C` when you have seen at least two triggers.

* * *

## Cron Schedule Reference​

Dapr uses **6-field cron expressions** (with seconds), not the standard 5-field format. The fields are: `second minute hour day-of-month month day-of-week`.

Expression| Meaning  
---|---  
`@every 30s`| Every 30 seconds  
`@every 5m`| Every 5 minutes  
`@hourly`| Once per hour  
`@daily`| Once per day at midnight  
`@midnight`| Same as `@daily`  
`0 30 * * * *`| Every hour at :30  
`0 0 2 * * *`| Daily at 2:00 AM  
`0 0 9 * * 1`| Every Monday at 9:00 AM  
  
The leading `0` is the seconds field. If you paste a 5-field expression from crontab.guru, it will either fail silently or fire at the wrong time.

* * *

## Lab B: HTTP Output Binding​

An output binding goes the other direction: your code invokes an external system through Dapr. You configure the target URL once in YAML, then call `invoke_binding` in your code.

### Step 1: Create the Component​

Create `components/http-binding.yaml`:
    
    
    apiVersion: dapr.io/v1alpha1  
    kind: Component  
    metadata:  
      name: monitoring-webhook  
    spec:  
      type: bindings.http  
      version: v1  
      metadata:  
        - name: url  
          value: "https://httpbin.org/post"  
        - name: direction  
          value: "output"  
    

This targets `httpbin.org/post`, a public echo service that returns whatever you send it. Good for testing.

### Step 2: Write the Code​

Add to `app.py`:
    
    
    from dapr.clients import DaprClient  
    import json  
      
    @app.post("/tasks/{task_id}/complete")  
    async def complete_task(task_id: str):  
        """Mark task complete and notify external monitoring."""  
      
        with DaprClient() as client:  
            client.invoke_binding(  
                binding_name="monitoring-webhook",  
                operation="post",  
                data=json.dumps({  
                    "event": "task.completed",  
                    "task_id": task_id  
                }),  
            )  
      
        return {"task_id": task_id, "status": "notified"}  
    

Note: `DaprClient()` uses `with`, not `async with`. The synchronous context manager is the correct pattern for the Python SDK.

### Step 3: Update Dockerfile and Deploy​

Update the pip install line to include the Dapr SDK:
    
    
    RUN pip install fastapi uvicorn dapr  
    

Rebuild and run:
    
    
    docker build -t cron-binding-app .  
      
    dapr run \  
      --app-id cron-app \  
      --app-port 8000 \  
      --resources-path ./components \  
      -- uvicorn app:app --host 0.0.0.0 --port 8000  
    

### Step 4: Test the Output Binding​

In a separate terminal:
    
    
    curl -X POST http://localhost:8000/tasks/task-42/complete  
    

Expected response:
    
    
    { "task_id": "task-42", "status": "notified" }  
    

Dapr sent your JSON payload to `https://httpbin.org/post` without your code managing HTTP clients, retries, or connection pooling. Change the URL in the YAML component to point at a real monitoring endpoint, and nothing in your Python code changes.

### Operations by Binding Type​

Different binding types support different operations:

Binding Type| Supported Operations  
---|---  
`bindings.http`| `get`, `post`, `put`, `delete`  
`bindings.aws.s3`| `create`, `get`, `delete`, `list`  
`bindings.smtp`| `create` (sends email)  
`bindings.cron`| Input only (no operations)  
  
* * *

## Combined Pattern: Cron + Pub/Sub + Output Binding​

Real systems combine these building blocks. Here is a cleanup handler that fires on a cron schedule, notifies internal services via pub/sub, and alerts external monitoring via an output binding:
    
    
    @app.post("/cleanup-cron")  
    async def handle_cleanup():  
        """Cron fires → find expired tasks → pub/sub internal + webhook external."""  
        expired_tasks = find_expired_tasks()  
      
        with DaprClient() as client:  
            for task_id in expired_tasks:  
                # Pub/Sub: notify internal Dapr services  
                client.publish_event(  
                    pubsub_name="pubsub",  
                    topic_name="task-events",  
                    data=json.dumps({"event": "task.expired", "task_id": task_id}),  
                )  
      
                # Output Binding: alert external monitoring  
                client.invoke_binding(  
                    binding_name="monitoring-webhook",  
                    operation="post",  
                    data=json.dumps({"alert": "task_expired", "task_id": task_id}),  
                )  
      
        return {"status": "OK", "expired_count": len(expired_tasks)}  
    

Three building blocks, one handler. The cron input binding triggers it. Pub/sub reaches internal services. The output binding reaches the outside world. Each is configured in its own YAML file and swappable independently.

* * *

## Troubleshooting​

Symptom| Cause| Fix  
---|---|---  
Endpoint never called| Path doesn't match component `metadata.name`| `/cleanup-cron` must match `name: cleanup-cron` exactly  
404 in daprd logs| Wrong HTTP method| Input bindings use POST, not GET  
Cron never triggers| Bad schedule syntax| Dapr uses 6-field format (with seconds), not 5-field  
Output binding fails| Wrong operation for binding type| Check supported operations table above  
`invoke_binding` hangs| Using `async with DaprClient()`| Use sync `with DaprClient()` instead  
  
Check Dapr sidecar logs for binding-related errors:
    
    
    dapr logs --app-id cron-app | grep -i binding  
    

* * *

## Cleanup​

Stop all running Dapr apps:
    
    
    dapr stop --app-id cron-app  
    

Keep the component files in `components/`. You will use them in Lesson 7.

* * *

## Reflect on Your Skill​

You built a `dapr-deployment` skill in Lesson 0. Test and improve it based on what you learned.

### Test Your Skill​
    
    
    Using my dapr-deployment skill, create a cron binding that triggers  
    every 5 minutes. Show me the component YAML, the FastAPI handler,  
    and the Dockerfile.  
    

Does your skill get the endpoint name right? Does it use 6-field cron syntax? Does it include the Dockerfile?

### Identify Gaps​

  * Does it warn about the endpoint-name-must-match-component-name rule?
  * Does it use `with DaprClient()` (sync) rather than `async with DaprClient()`?
  * Can it explain when to use bindings vs pub/sub?


### Improve Your Skill​
    
    
    My dapr-deployment skill needs binding patterns. Add these:  
    1. Input bindings: endpoint path MUST match component metadata.name  
    2. Output bindings: use sync DaprClient context manager  
    3. Dapr cron uses 6-field format with seconds, not standard 5-field  
    4. Use bindings for external systems, pub/sub for internal services  
    

* * *

## Try With AI​

Apply binding patterns to your own integration scenarios.

**Setup:** Open Claude Code or your preferred AI assistant in your Dapr project directory.

* * *

**Prompt 1: Debug a Silent Binding**
    
    
    My Dapr cron binding never fires. The component YAML has  
    name: nightly-cleanup and schedule: "0 0 2 * * *".  
    My FastAPI handler is @app.post("/nightly_cleanup").  
    The app starts with no errors. Why is nothing happening?  
    

**What you're learning:** The most common binding failure is a name mismatch between the component and the endpoint. The underscore vs hyphen difference (`nightly_cleanup` vs `nightly-cleanup`) is exactly the kind of silent failure that wastes hours in production.

* * *

**Prompt 2: Build a Two-Binding System**
    
    
    Build a Dapr application with:  
    1. A cron input binding that fires every 60 seconds  
    2. An HTTP output binding that POSTs to https://httpbin.org/post  
      
    When the cron fires, collect system stats and send them  
    to the monitoring endpoint via the output binding.  
      
    Give me: both component YAMLs, the Python code, and the Dockerfile.  
    Use sync DaprClient (with, not async with).  
    

**What you're learning:** Combining input and output bindings in a single application. The cron triggers your code; the HTTP binding sends data out. Two YAML files, one handler, zero external client libraries.

* * *

**Prompt 3: Bindings vs Pub/Sub**
    
    
    I have four integration needs:  
    1. Run database cleanup every night at midnight  
    2. Notify my Notification Service (a Dapr app) when tasks are created  
    3. Send alerts to PagerDuty when tasks fail  
    4. Receive webhooks from Stripe for payment events  
      
    For each one, tell me: bindings or pub/sub? What component type?  
    Why?  
    

**What you're learning:** The decision rule is simple: is the other end a Dapr application? If yes, pub/sub. If no, bindings. This prompt forces you to apply that rule across different scenarios until it becomes automatic.

* * *

**Safety Note:** When configuring bindings that receive webhooks from external sources, validate the sender. Add authentication (API keys, HMAC signatures) to prevent unauthorized actors from triggering your endpoints. Consult the Dapr documentation for your specific binding type's security options.