# Secrets and Configuration

> **Archived from:** <https://agentfactory.panaversity.org/docs/Deploying-Agent-Factories-in-the-Cloud/dapr-core/secrets-configuration>  
> **Wayback snapshot:** 2026-04-22  
> **Status:** retired from the live site — recovered for offline study.

---

## The Credential Leak Problem​

Hardcoded credentials in source code are a security disaster. The progression most teams follow:

  1. **Hardcoded in code** : anyone who reads the repo has your keys.
  2. **Environment variables** : better, but your deployment YAML now has the key in plain text.
  3. **Kubernetes secrets** : access-controlled, but every service needs its own kubectl logic to read them.
  4. **Dapr Secrets API** : one unified API across all secret stores (Kubernetes, Vault, AWS Secrets Manager). Your code never knows which backend is in use.


This lesson teaches step 4: retrieving secrets through Dapr, referencing them in component YAML, and loading them safely at startup.

Prerequisites

You need Dapr, Redis, the statestore component, and pubsub component running from previous lessons. If you stopped your cluster, redeploy those components before continuing.

* * *

## Create Kubernetes Secrets​

Before Dapr can retrieve secrets, they must exist in Kubernetes.

### API Credentials​
    
    
    kubectl create secret generic api-credentials \  
      --from-literal=api-key=my-secret-key-123 \  
      --from-literal=api-secret=my-secret-value-456  
    

**Output:**
    
    
    secret/api-credentials created  
    

### Redis Password​
    
    
    kubectl create secret generic redis-password \  
      --from-literal=password=redis-secret-pass  
    

**Output:**
    
    
    secret/redis-password created  
    

### Verify​
    
    
    kubectl get secret api-credentials -o yaml  
    

**Output:**
    
    
    apiVersion: v1  
    kind: Secret  
    metadata:  
      name: api-credentials  
      namespace: default  
    type: Opaque  
    data:  
      api-key: bXktc2VjcmV0LWtleS0xMjM=  
      api-secret: bXktc2VjcmV0LXZhbHVlLTQ1Ng==  
    

The values are base64-encoded, not encrypted. Kubernetes secrets provide access control, not encryption at rest by default.

* * *

## Secrets Store Component​

Dapr needs a secrets store component to know where to look. The Kubernetes secrets store is built in; no extra installation required.
    
    
    # components/kubernetes-secrets.yaml  
    apiVersion: dapr.io/v1alpha1  
    kind: Component  
    metadata:  
      name: kubernetes-secrets  
      namespace: default  
    spec:  
      type: secretstores.kubernetes  
      version: v1  
      metadata: []  
    

Deploy and verify:
    
    
    kubectl apply -f components/kubernetes-secrets.yaml  
    
    
    
    kubectl get components  
    

**Output:**
    
    
    NAME                  AGE  
    kubernetes-secrets    5s  
    statestore           1h  
    pubsub               1h  
    

* * *

## Retrieve Secrets in Python​

The Secrets API endpoint is `GET /v1.0/secrets/{store}/{key}`. The Python SDK wraps this with `DaprClient.get_secret()`.

### Single Secret​
    
    
    from dapr.clients import DaprClient  
      
    with DaprClient() as client:  
        secret = client.get_secret(  
            store_name="kubernetes-secrets",  
            key="api-credentials",  
        )  
        api_key = secret.secret.get("api-key", "")  
        # Only log prefix — NEVER log full secret values  
        print(f"Got API key: {api_key[:4]}...")  
    

**Output:**
    
    
    Got API key: my-s...  
    

The `secret.secret` dictionary contains every key-value pair stored under that Kubernetes secret name.

### Bulk Secrets​

To retrieve all secrets from a store at once:
    
    
    from dapr.clients import DaprClient  
      
    with DaprClient() as client:  
        secrets = client.get_bulk_secret(store_name="kubernetes-secrets")  
        for name, values in secrets.secrets.items():  
            print(f"{name}: {list(values.keys())}")  
    

**Output:**
    
    
    api-credentials: ['api-key', 'api-secret']  
    redis-password: ['password']  
    

Bulk retrieval is useful for diagnostics and startup validation. In production, retrieve only the secrets your service needs.

* * *

## secretKeyRef in Component YAML​

Hardcoding credentials in component YAML defeats the purpose of a secrets store. Dapr supports `secretKeyRef` to pull values from a secrets store at component load time.

Instead of this:
    
    
    metadata:  
      - name: redisPassword  
        value: "my-plain-text-password" # BAD: exposed in YAML  
    

Use this:
    
    
    metadata:  
      - name: redisPassword  
        secretKeyRef:  
          name: redis-password # Kubernetes secret name  
          key: password # Key within the secret  
    auth:  
      secretStore: kubernetes-secrets # REQUIRED  
    

### Complete Example: Redis State Store​
    
    
    # components/statestore.yaml  
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
          secretKeyRef:  
            name: redis-password  
            key: password  
    auth:  
      secretStore: kubernetes-secrets  
    

Now your state store password comes from Kubernetes secrets, not plain text YAML.

* * *

## auth.secretStore Is Mandatory​

Critical Requirement

When any component uses `secretKeyRef`, the `auth.secretStore` field is **mandatory**. Without it, Dapr does not know which secrets store resolves the references and the component fails to initialize. Every component that references a secret must include this field.
    
    
    # This FAILS silently — missing auth.secretStore  
    spec:  
      metadata:  
        - name: redisPassword  
          secretKeyRef:  
            name: redis-password  
            key: password  
    # No auth block → Dapr cannot resolve the secret  
    
    
    
    # This WORKS — auth.secretStore present  
    spec:  
      metadata:  
        - name: redisPassword  
          secretKeyRef:  
            name: redis-password  
            key: password  
    auth:  
      secretStore: kubernetes-secrets  
    

* * *

## Startup-Load Pattern​

Reading secrets on every request adds latency and hammers the secrets store. The best practice: load secrets once at startup, store them in memory, use them throughout the application lifetime.
    
    
    from contextlib import asynccontextmanager  
    from dataclasses import dataclass, field  
      
    from dapr.clients import DaprClient  
    from fastapi import FastAPI, HTTPException  
      
      
    @dataclass  
    class AppConfig:  
        api_key: str | None = None  
        api_secret: str | None = None  
      
      
    config = AppConfig()  
      
      
    @asynccontextmanager  
    async def lifespan(app: FastAPI):  
        # Load secrets once at startup  
        with DaprClient() as client:  
            secret = client.get_secret(  
                store_name="kubernetes-secrets",  
                key="api-credentials",  
            )  
            config.api_key = secret.secret.get("api-key")  
            config.api_secret = secret.secret.get("api-secret")  
            print(f"Loaded API key: {config.api_key[:4]}...")  
        yield  
      
      
    app = FastAPI(lifespan=lifespan)  
      
      
    @app.get("/config")  
    def get_config():  
        if not config.api_key:  
            raise HTTPException(status_code=500, detail="Secrets not loaded")  
        return {"api_key_prefix": config.api_key[:4] + "..."}  
    

The `lifespan` context manager runs once when the app starts. All route handlers read from the `config` object. No repeated Dapr calls.

* * *

## Secrets vs Configuration​

Data| Use| Rationale  
---|---|---  
Database password| Secrets API| Sensitive, access-controlled  
API key| Secrets API| Sensitive, access-controlled  
Feature flag| Configuration API| Non-sensitive, may change at runtime  
Rate limit value| Configuration API| Non-sensitive, runtime tunable  
Service URL| Configuration API| Non-sensitive, environment-specific  
Encryption key| Secrets API| Highly sensitive  
  
The rule: if the value is sensitive and should be access-controlled, use Secrets. If the value is non-sensitive and may need runtime updates, use Configuration.

* * *

## Configuration API​

The Configuration API handles dynamic, non-sensitive settings. The endpoint:
    
    
    GET /v1.0/configuration/{store}?key=feature-x&key=max-retries  
    

Python SDK usage:
    
    
    from dapr.clients import DaprClient  
      
    with DaprClient() as client:  
        config = client.get_configuration(  
            store_name="configstore",  
            keys=["feature-flag-x", "max-retry-count"],  
        )  
        for item in config.items:  
            print(f"{item.key}: {item.value}")  
    

**Output:**
    
    
    feature-flag-x: enabled  
    max-retry-count: 3  
    

The Configuration API also supports subscriptions for real-time updates, which the Secrets API does not. This makes it the right choice for values that change without redeployment.

* * *

## Security Best Practices​

  1. **Never hardcode secrets** in YAML, code, or Dockerfiles. Use `secretKeyRef` and the Secrets API.
  2. **Log only prefixes** : `api_key[:4] + "..."` reveals enough to confirm the right secret loaded. In production, consider not logging even prefixes.
  3. **Startup-load pattern** : Read secrets once at startup via `lifespan`, not per-request.
  4. **Component scoping** : Restrict which apps can access which secret stores:


    
    
    apiVersion: dapr.io/v1alpha1  
    kind: Component  
    metadata:  
      name: kubernetes-secrets  
    spec:  
      type: secretstores.kubernetes  
      version: v1  
      metadata: []  
    scopes:  
      - payment-service  
      - billing-service  
    

Only `payment-service` and `billing-service` can access this secrets store. All other Dapr apps are denied.

  5. **Always set auth.secretStore** on every component that uses `secretKeyRef`. Missing it causes silent failures.


* * *

## Troubleshooting​

Symptom| Cause| Fix  
---|---|---  
`SECRET_STORE_NOT_FOUND`| Secrets store component not deployed| `kubectl apply -f components/kubernetes-secrets.yaml`  
`ERR_SECRET_GET` with 403| Dapr sidecar lacks RBAC permissions| Check ClusterRole/ClusterRoleBinding for Dapr  
Component fails to initialize| Missing `auth.secretStore`| Add `auth.secretStore: kubernetes-secrets` to component YAML  
Empty secret value| Wrong key name in `secretKeyRef`| Verify with `kubectl get secret <name> -o yaml`  
`get_secret()` returns empty dict| Secret name does not exist in namespace| Create the secret in the correct namespace  
  
* * *

## Cleanup​

When you are done experimenting, remove the secrets and component created in this lesson:
    
    
    kubectl delete secret api-credentials  
    kubectl delete secret redis-password  
    kubectl delete -f components/kubernetes-secrets.yaml  
    

If you plan to continue to the capstone in Lesson 9, keep the `redis-password` secret and the `kubernetes-secrets` component; the capstone uses them.

* * *

## Reflect on Your Skill​

You built a `dapr-deployment` skill in Lesson 0. Test and improve it based on what you learned.

### Test Your Skill​
    
    
    Using my dapr-deployment skill, show me how to retrieve API credentials  
    from Kubernetes secrets using Dapr's sync Python client.  
    

Does your skill include the `get_secret()` pattern? Does it mention `auth.secretStore`?

### Identify Gaps​

Ask yourself:

  * Does my skill explain the Kubernetes secrets store component?
  * Does it show `secretKeyRef` in component YAML?
  * Does it include the startup-load pattern?
  * Does it warn about `auth.secretStore` being mandatory?


### Improve Your Skill​

If you found gaps:
    
    
    My dapr-deployment skill is missing secrets management patterns.  
    Update it to include:  
    1. Kubernetes secrets store component (secretstores.kubernetes)  
    2. DaprClient.get_secret() sync pattern with context manager  
    3. secretKeyRef for referencing secrets in component YAML  
    4. auth.secretStore field is MANDATORY  
    5. Startup-load best practice using FastAPI lifespan  
    6. Component scoping for restricting secret store access  
    

* * *

## Try With AI​

Use these prompts in your AI assistant to apply secrets patterns to your own systems.

### Prompt 1: Secure a Component​
    
    
    I have a Dapr pub/sub component that connects to Kafka with SASL authentication.  
    The username and password are currently hardcoded in the component YAML.  
      
    Refactor this component to:  
    1. Store credentials in a Kubernetes secret  
    2. Reference them using secretKeyRef  
    3. Include auth.secretStore configuration  
    4. Add component scoping so only my order-service and notification-service can use it  
      
    Show me the kubectl command to create the secret, and the complete component YAML.  
    

**What you're learning:** The full workflow from creating a Kubernetes secret to referencing it in component YAML with access controls.

### Prompt 2: Implement Startup-Load​
    
    
    I have a FastAPI application that calls DaprClient.get_secret() inside every  
    route handler. This means every HTTP request makes a Dapr API call to retrieve  
    the same secret.  
      
    Refactor this to use the startup-load pattern:  
    1. Load all secrets once at app startup using FastAPI lifespan  
    2. Store them in a config dataclass  
    3. Make route handlers read from the config object  
    4. Add error handling for missing secrets  
      
    Use the sync DaprClient with a context manager (with DaprClient() as client).  
    

**What you're learning:** The startup-load pattern eliminates per-request secret fetches. The lifespan context manager is the modern FastAPI initialization pattern.

### Prompt 3: Secrets vs Configuration Decision​
    
    
    I have these values to manage in my distributed application:  
    - PostgreSQL connection password  
    - Feature flag: enable-new-checkout (true/false)  
    - Maximum retry count for failed payment API calls  
    - Stripe API secret key  
    - Alert threshold for order processing time (milliseconds)  
      
    For each value, tell me whether to use Dapr's Secrets API or Configuration API,  
    and explain why. Then show me how to retrieve one secret and one configuration  
    value in Python using the sync DaprClient.  
    

**What you're learning:** Secrets are for sensitive, access-controlled data. Configuration is for non-sensitive, runtime-tunable settings. Mixing them up creates either security risks or unnecessary complexity.

### Safety Note​

Never log full secret values. The `api_key[:4] + "..."` pattern shown in this lesson reveals only enough to confirm the right secret loaded. In production, consider removing even prefix logging. An attacker with log access could use partial values alongside timing attacks to reconstruct secrets. Test secret retrieval in development, then strip debug logging before deployment.