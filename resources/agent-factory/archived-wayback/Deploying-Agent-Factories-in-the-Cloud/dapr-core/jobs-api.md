# Jobs API: Scheduled Tasks

> **Archived from:** <https://agentfactory.panaversity.org/docs/Deploying-Agent-Factories-in-the-Cloud/dapr-core/jobs-api>  
> **Wayback snapshot:** 2026-04-22  
> **Status:** retired from the live site — recovered for offline study.

---

Your Task API needs to clean up completed todos older than 30 days. A cron job on one server handles this fine. Scale to three pods, and you get three cleanup runs. Delete the same records three times. Bill the database three times. The multi-replica cron problem breaks every scheduled task in a distributed system.

Dapr's Jobs API solves this with exactly-once scheduled execution. The Scheduler service, backed by embedded Etcd, tracks every job and triggers exactly one application instance when the time comes. Whether you run one pod or twenty, the cleanup runs once.

Prerequisites

This lesson assumes you have Dapr, Redis, statestore, and pubsub running from previous lessons. If not, revisit Lesson 3 (State Management) to set up your local environment.

* * *

## Jobs API vs Cron Input Binding​

Both can trigger your application on a schedule. The difference is where the schedule lives and what guarantees you get.

Aspect| Jobs API| Cron Input Binding  
---|---|---  
**Defined in**|  Application code (runtime)| YAML component (static)  
**Schedule changes**|  API call to update| Redeploy component YAML  
**One-time jobs**|  Yes (`dueTime`)| No  
**Repeat limits**|  Yes (`repeats: 24`)| No (runs forever)  
**Exactly-once**|  Yes (Scheduler with Etcd)| Per-pod (3 replicas = 3 runs)  
**Use when**|  App decides when to schedule| Fixed schedule, ops-managed  
  
The exactly-once row is the deciding factor. If you run multiple replicas and need a job to fire once across all of them, Jobs API is the only option. Cron bindings trigger independently on every pod.

* * *

Alpha API

The Jobs API endpoint uses `v1.0-alpha1`. The API surface may change in future Dapr releases. Pin your Dapr version in production and test when upgrading.

* * *

## Schedule Format Reference​

Dapr accepts two formats for job schedules.

### Human-Readable Period Strings​

Expression| Meaning  
---|---  
`@yearly` or `@annually`| Once per year (Jan 1, midnight)  
`@monthly`| First day of each month (midnight)  
`@weekly`| Sunday at midnight  
`@daily` or `@midnight`| Every day at midnight  
`@hourly`| Start of every hour  
`@every <duration>`| Custom interval (e.g., `@every 1h30m`, `@every 30s`)  
  
### Cron Expressions (6 fields)​

Dapr uses 6-field cron (not the standard 5-field). The extra field is seconds:
    
    
    ┌───────────── second (0-59)  
    │ ┌─────────── minute (0-59)  
    │ │ ┌───────── hour (0-23)  
    │ │ │ ┌─────── day of month (1-31)  
    │ │ │ │ ┌───── month (1-12)  
    │ │ │ │ │ ┌─── day of week (0-6, 0=Sunday)  
    │ │ │ │ │ │  
    * * * * * *  
    

Expression| Meaning  
---|---  
`0 0 0 * * *`| Every day at midnight  
`0 30 * * * *`| Every hour at the 30-minute mark  
`0 0 9 * * 1`| Every Monday at 9 AM  
`0 0 */2 * * *`| Every 2 hours  
  
* * *

## Build the App​

The Python SDK does not have a typed Jobs client. You talk to the Jobs API through the Dapr HTTP API directly using `httpx`.

### Project Setup​
    
    
    uv init dapr-jobs-demo && cd dapr-jobs-demo  
    uv add fastapi uvicorn httpx  
    

### Application Code​

Create `main.py`:
    
    
    from contextlib import asynccontextmanager  
    from fastapi import FastAPI, Request  
    from datetime import datetime, timedelta  
    import httpx  
    import logging  
    import os  
      
    logging.basicConfig(level=logging.INFO)  
    logger = logging.getLogger("jobs-demo")  
      
    DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")  
    JOBS_URL = f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs"  
      
      
    async def schedule_cleanup_job():  
        """Schedule a recurring cleanup job on startup."""  
        job_data = {  
            "schedule": "@every 30s",   # 30s for demo; use @daily in production  
            "data": {  
                "action": "cleanup-completed-todos",  
                "retention_days": 30,  
            },  
        }  
        async with httpx.AsyncClient() as client:  
            response = await client.post(  
                f"{JOBS_URL}/daily-cleanup", json=job_data  
            )  
            if response.status_code == 204:  
                logger.info("Cleanup job scheduled successfully")  
            else:  
                logger.error("Failed to schedule job: %s %s",  
                             response.status_code, response.text)  
      
      
    @asynccontextmanager  
    async def lifespan(app: FastAPI):  
        await schedule_cleanup_job()  
        yield  
      
      
    app = FastAPI(lifespan=lifespan)  
      
      
    @app.post("/job/daily-cleanup")  
    async def handle_cleanup_job(request: Request):  
        """Dapr calls this endpoint when the job triggers."""  
        job_data = await request.json()  
        action = job_data.get("action", "unknown")  
        retention_days = job_data.get("retention_days", 30)  
      
        cutoff = datetime.utcnow() - timedelta(days=retention_days)  
        logger.info("JOB TRIGGERED: %s, cleaning records before %s", action, cutoff)  
      
        # Your database cleanup logic goes here  
        return {"status": "SUCCESS"}  
      
      
    @app.get("/health")  
    async def health():  
        return {"status": "healthy"}  
    

Two things to notice:

  1. **`lifespan`** schedules the job when the app starts. The Dapr sidecar is ready by the time your app's lifespan hook runs.
  2. **`/job/daily-cleanup`** is the handler endpoint. The path pattern `/job/{job-name}` is how Dapr knows where to deliver the trigger. The name in the URL must match the name you used when scheduling.


### Dockerfile​
    
    
    FROM python:3.12-slim  
      
    COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv  
      
    WORKDIR /app  
    COPY pyproject.toml uv.lock ./  
    RUN uv sync --frozen --no-dev  
      
    COPY main.py .  
      
    EXPOSE 8000  
    CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]  
    

### Kubernetes Deployment​
    
    
    # deployment.yaml  
    apiVersion: apps/v1  
    kind: Deployment  
    metadata:  
      name: jobs-demo  
    spec:  
      replicas: 3 # Three replicas — job still fires once  
      selector:  
        matchLabels:  
          app: jobs-demo  
      template:  
        metadata:  
          labels:  
            app: jobs-demo  
          annotations:  
            dapr.io/enabled: "true"  
            dapr.io/app-id: "jobs-demo"  
            dapr.io/app-port: "8000"  
        spec:  
          containers:  
            - name: app  
              image: jobs-demo:latest  
              ports:  
                - containerPort: 8000  
    

### Deploy and Verify​
    
    
    docker build -t jobs-demo:latest .  
    kubectl apply -f deployment.yaml  
    

Watch for job triggers across all three replicas:
    
    
    kubectl logs -l app=jobs-demo -f --all-containers  
    

You will see `JOB TRIGGERED` in the logs of exactly one pod every 30 seconds. Not three. That is the exactly-once guarantee at work.

* * *

## One-Time Jobs​

Schedule a job that runs once at a specific time using `dueTime` instead of `schedule`:
    
    
    async def schedule_one_time_report():  
        job_data = {  
            "dueTime": "2026-04-15T09:00:00Z",  
            "data": {  
                "action": "generate-quarterly-report",  
                "quarter": "Q1-2026",  
            },  
        }  
        async with httpx.AsyncClient() as client:  
            response = await client.post(  
                f"{JOBS_URL}/q1-report", json=job_data  
            )  
    

The job fires once at the specified timestamp, then Dapr removes it automatically.

* * *

## Recurring Jobs with Limits​

Combine `schedule` with `repeats` to cap how many times a recurring job fires:
    
    
    async def schedule_limited_sync():  
        job_data = {  
            "schedule": "@hourly",  
            "repeats": 24,          # Stop after 24 executions  
            "data": {  
                "action": "sync-external-system",  
            },  
        }  
        async with httpx.AsyncClient() as client:  
            response = await client.post(  
                f"{JOBS_URL}/hourly-sync", json=job_data  
            )  
    

After 24 triggers, Dapr stops scheduling the job. Useful for migration tasks, trial syncs, or any work with a known end.

* * *

## Job Management​

### Check If a Job Exists​
    
    
    async def get_job(job_name: str) -> dict | None:  
        async with httpx.AsyncClient() as client:  
            response = await client.get(f"{JOBS_URL}/{job_name}")  
            if response.status_code == 200:  
                return response.json()  
            return None  
    

### Delete a Job​
    
    
    async def delete_job(job_name: str) -> bool:  
        async with httpx.AsyncClient() as client:  
            response = await client.delete(f"{JOBS_URL}/{job_name}")  
            return response.status_code == 204  
    

### Update a Job​

To change a job's schedule, POST to the same job name. Dapr overwrites the existing job:
    
    
    async def update_cleanup_schedule(new_schedule: str):  
        job_data = {  
            "schedule": new_schedule,  
            "data": {  
                "action": "cleanup-completed-todos",  
                "retention_days": 30,  
            },  
        }  
        async with httpx.AsyncClient() as client:  
            response = await client.post(  
                f"{JOBS_URL}/daily-cleanup", json=job_data  
            )  
            return response.status_code == 204  
    

* * *

## Handler Response Codes​

Your handler tells Dapr what to do next through the response body:

Response| Dapr Behavior  
---|---  
`{"status": "SUCCESS"}`| Job completed. No retry.  
`{"status": "RETRY"}`| Job failed. Retry per failure policy.  
`{"status": "DROPPED"}`| Permanent failure. Do not retry.  
  
A handler that distinguishes transient from permanent failures:
    
    
    @app.post("/job/daily-cleanup")  
    async def handle_cleanup_job(request: Request):  
        job_data = await request.json()  
        try:  
            # Attempt cleanup  
            deleted = await cleanup_old_todos(job_data.get("retention_days", 30))  
            logger.info("Cleaned up %d records", deleted)  
            return {"status": "SUCCESS"}  
        except ConnectionError:  
            logger.warning("Database unreachable, will retry")  
            return {"status": "RETRY"}  
        except Exception as e:  
            logger.error("Permanent failure: %s", e)  
            return {"status": "DROPPED"}  
    

* * *

## Troubleshooting​

Symptom| Cause| Fix  
---|---|---  
Job never triggers| Handler path mismatch| Ensure `/job/{name}` matches the name used in `POST /jobs/{name}`  
404 on job schedule| Wrong API version| Use `v1.0-alpha1`, not `v1.0`  
Job triggers on every pod| Using cron binding, not Jobs API| Switch to Jobs API for exactly-once  
Sidecar not ready at startup| App starts before Dapr| Dapr injects a readiness check; if running locally, add a startup delay  
  
* * *

## Cleanup​

Remove the demo resources when done:
    
    
    kubectl delete -f deployment.yaml  
    

If you built the Docker image locally:
    
    
    docker rmi jobs-demo:latest  
    

* * *

## Reflect on Your Skill​

You built a `dapr-deployment` skill in Lesson 0. Test and extend it with what you learned.

### Test Your Skill​
    
    
    Using my dapr-deployment skill, schedule a job that runs every hour  
    to check for stale tasks. What endpoint do I need to implement?  
    

### Identify Gaps​

  * Does your skill explain when to use Jobs API vs cron bindings?
  * Does it include the handler endpoint pattern (`/job/{name}`)?
  * Does it mention `httpx` for the Jobs API (no typed SDK client)?
  * Does it note the `v1.0-alpha1` path?


### Improve Your Skill​
    
    
    My dapr-deployment skill doesn't cover the Jobs API.  
    Update it to include:  
    1. Jobs API for exactly-once scheduling (vs bindings for external triggers)  
    2. HTTP pattern: POST /v1.0-alpha1/jobs/{name} with schedule and data  
    3. Handler pattern: POST /job/{name} returns {"status": "SUCCESS"}  
    4. Use httpx — Python SDK has no typed Jobs client  
    5. Alpha API caveat — pin your Dapr version  
    

* * *

## Try With AI​

### Prompt 1: Build a Job-Scheduled Notifier​
    
    
    Create a Dapr Jobs API app that schedules a daily digest email  
    at 8 AM. Use httpx to hit the v1.0-alpha1 jobs endpoint.  
    Include the FastAPI lifespan hook for scheduling on startup  
    and the /job/{name} handler that returns SUCCESS or RETRY.  
    

**What you're learning:** The full Jobs API lifecycle: scheduling via HTTP, receiving triggers, and communicating outcomes back to Dapr through response codes.

### Prompt 2: Multi-Replica Cron Audit​
    
    
    I have a FastAPI app running 5 replicas in Kubernetes.  
    Currently I use a Dapr cron input binding to run a nightly  
    database backup. What goes wrong? Rewrite it using the  
    Jobs API so the backup runs exactly once.  
    

**What you're learning:** The core problem Jobs API solves. You will see how cron bindings trigger independently per pod and how migrating to Jobs API eliminates duplicate execution.

### Prompt 3: Job Lifecycle Management​
    
    
    Build a FastAPI endpoint that lets users schedule, check,  
    and cancel their own reminder jobs through the Dapr Jobs API.  
    Include POST /reminders (schedule), GET /reminders/{id} (check),  
    and DELETE /reminders/{id} (cancel). Use httpx against  
    the v1.0-alpha1 jobs endpoint.  
    

**What you're learning:** Job management patterns beyond fire-and-forget. Real applications need to list, inspect, and cancel jobs dynamically.

* * *

Alpha API Stability

The Jobs API is `v1.0-alpha1` as of Dapr 1.14+. It is functional and safe for production use behind a pinned version, but the endpoint path and request format may change when it graduates to stable. Track the [Dapr Jobs API docs](<https://docs.dapr.io/developing-applications/building-blocks/jobs/>) for updates.