# Docker Workshop: From Zero to Containerized APIs

> **Duration:** ~2 hours
> **Prerequisites:** Docker Desktop installed and running
> **Audience:** Beginners who want to understand Docker by doing

---

## Table of Contents

1. [What is Docker and Why Should You Care?](#part-1-what-is-docker-and-why-should-you-care)
2. [Docker Basics — Images and Containers](#part-2-docker-basics--images-and-containers)
3. [Hands-On: Your First Python Container](#part-3-hands-on-your-first-python-container)
4. [Understanding the Dockerfile](#part-4-understanding-the-dockerfile)
5. [Working with Containers — Essential Commands](#part-5-working-with-containers--essential-commands)
6. [Port Mapping — Connecting to Your Container](#part-6-port-mapping--connecting-to-your-container)
7. [Hands-On: Containerizing a FastAPI Application](#part-7-hands-on-containerizing-a-fastapi-application)
8. [Multi-Stage Builds — Optimizing Image Size](#part-8-multi-stage-builds--optimizing-image-size)
9. [Running Multiple Containers](#part-9-running-multiple-containers)
10. [Quick Reference Cheat Sheet](#quick-reference-cheat-sheet)

---

## Part 1: What is Docker and Why Should You Care?

Imagine you build an app on your machine. It works perfectly. You send it to a friend — it crashes. Different Python version, missing packages, wrong OS. Sound familiar?

**Docker solves this.** It packages your app + its entire environment into a **container** that runs the same everywhere.

```
Without Docker:
  "It works on my machine" → breaks everywhere else

With Docker:
  "It works in a container" → runs the same everywhere
```

### Key Terms

| Term | What It Is | Real-World Analogy |
|------|-----------|-------------------|
| **Image** | A blueprint/template for your app | A recipe |
| **Container** | A running instance of an image | A dish made from the recipe |
| **Dockerfile** | Instructions to build an image | The recipe steps |
| **Docker Hub** | Online registry of images | An app store for images |

> You can create **many containers** from **one image**, just like you can cook the same dish multiple times from one recipe.

---

## Part 2: Docker Basics — Images and Containers

### Verify Docker is Installed

```bash
docker --version
```

Expected output: `Docker version 24.x.x` or similar.

### Pulling Images from Docker Hub

Docker Hub has thousands of pre-built images. Let's pull the official Python image:

```bash
docker pull python:3.13-slim
```

> **Common mistake:** Watch your spelling! `python:3.13-silm` (typo) will give you:
> ```
> Error: docker.io/library/python:3.13-silm: not found
> ```
> Docker error messages are literal — read them carefully.

### Python Image Variants

| Tag | Base OS | Size | Use Case |
|-----|---------|------|----------|
| `python:3.13` | Debian Bookworm (full) | ~1 GB | Need build tools (gcc, etc.) |
| `python:3.13-slim` | Debian Bookworm (minimal) | ~150 MB | Most apps (recommended) |
| `python:3.13-alpine` | Alpine Linux | ~50 MB | Smallest possible image |

> **What OS is inside `python:3.13-slim`?**
> It's **Debian 12 (Bookworm)** — a minimal installation. Verify it yourself:
> ```bash
> docker run --rm python:3.13-slim cat /etc/os-release
> ```

### Listing and Removing Images

```bash
# List all images on your machine
docker images

# Remove an image by name:tag
docker rmi python:3.13-slim

# Force remove (if a container is using it)
docker rmi -f python:3.13-slim
```

---

## Part 3: Hands-On: Your First Python Container

### Step 1: Create the Project

Create a folder called `docker-basics` and add a simple Python script:

**`app.py`**
```python
import time

print("=== Docker Workshop Demo ===")
print("Hello from inside a Docker container!")
print()

for i in range(1, 6):
    print(f"Processing item {i}/5...")
    time.sleep(1)

print()
print("All done! Container is working correctly.")
```

### Step 2: Write the Dockerfile

Create a file named `Dockerfile` (no extension) in the same folder:

**`Dockerfile`**
```dockerfile
FROM python:3.13-slim
WORKDIR /app

COPY app.py ./

CMD ["python", "-u", "app.py"]
```

**Line-by-line breakdown:**

| Line | What It Does |
|------|-------------|
| `FROM python:3.13-slim` | Start from the Python 3.13 slim image |
| `WORKDIR /app` | Create and switch to `/app` directory inside the container |
| `COPY app.py ./` | Copy `app.py` from your machine into the container |
| `CMD ["python", "-u", "app.py"]` | Run this command when the container starts |

> **Why `-u` flag?** Python buffers output inside Docker. Without `-u`, you won't see `print()` output in real-time — it all dumps at the end. The `-u` flag disables buffering.

### Step 3: Build the Image

```bash
docker build -t my-first-app .
```

| Part | Meaning |
|------|---------|
| `docker build` | Build an image from a Dockerfile |
| `-t my-first-app` | Tag/name the image as "my-first-app" |
| `.` | Use the current directory as build context |

> **Always tag your images!** If you don't use `-t`, Docker assigns a random ID instead of a name. This makes it harder to identify your images later.

### Step 4: Run the Container

```bash
docker run --rm my-first-app
```

Expected output:
```
=== Docker Workshop Demo ===
Hello from inside a Docker container!

Processing item 1/5...
Processing item 2/5...
Processing item 3/5...
Processing item 4/5...
Processing item 5/5...

All done! Container is working correctly.
```

> `--rm` automatically removes the container after it stops, keeping things clean.

---

## Part 4: Understanding the Dockerfile

A Dockerfile is a set of instructions that Docker reads **top to bottom** to build an image. Each instruction creates a **layer**.

### Common Instructions

| Instruction | Purpose | Example |
|------------|---------|---------|
| `FROM` | Base image to start from | `FROM python:3.13-slim` |
| `WORKDIR` | Set working directory | `WORKDIR /app` |
| `COPY` | Copy files from host to container | `COPY . .` |
| `RUN` | Execute command during build | `RUN pip install flask` |
| `CMD` | Default command when container starts | `CMD ["python", "app.py"]` |
| `EXPOSE` | Document which port the app uses | `EXPOSE 8000` |
| `ENV` | Set environment variables | `ENV PYTHONUNBUFFERED=1` |
| `LABEL` | Add metadata to the image | `LABEL VERSION="1.0"` |

### Python Buffering — Important for Docker

Always add one of these to your Python Dockerfiles:

```dockerfile
# Option 1: Environment variable (recommended — applies to all Python processes)
ENV PYTHONUNBUFFERED=1

# Option 2: Pass -u flag in CMD (applies to one command only)
CMD ["python", "-u", "app.py"]
```

Without this, your `print()` statements won't appear in `docker logs` until the container stops.

### Image Naming Rules

- **Allowed:** lowercase letters, numbers, hyphens (`-`), underscores (`_`)
- **Not allowed:** spaces or uppercase letters
- **Tagging:** Use `name:tag` format (e.g., `my-app:v1`, `my-app:dev`)
- **Default tag:** If you omit the tag, Docker uses `latest`

```bash
docker build -t my-app .         # Tagged as my-app:latest
docker build -t my-app:v1 .      # Tagged as my-app:v1
docker build -t my-app:dev .     # Tagged as my-app:dev
```

---

## Part 5: Working with Containers — Essential Commands

### `docker run` vs `docker start`

| Command | What It Does |
|---------|-------------|
| `docker run` | Creates a **new** container from an image and starts it |
| `docker start` | Restarts an **existing** stopped container |

> Use `docker run` the first time. After that, use `docker start <name>` to restart the same container without creating a duplicate.

### Foreground vs Detached Mode

**Foreground (default):**
```bash
docker run -p 8000:8000 my-app
# Terminal is locked — you see logs here
# Ctrl+C stops the container
```

**Detached mode (`-d`):**
```bash
docker run -d -p 8000:8000 my-app
# Prints container ID and returns your terminal immediately
# Container runs in the background
```

Think of it like running a program in your terminal vs running it as a background service.

### Managing Detached Containers

```bash
# See running containers
docker ps

# See ALL containers (including stopped)
docker ps -a

# View logs of a detached container
docker logs <container-name>

# Follow logs in real-time (like tail -f)
docker logs -f <container-name>

# Stop a container
docker stop <container-name>

# Start a stopped container (with terminal attached)
docker start -a <container-name>

# Remove a stopped container
docker rm <container-name>
```

### Naming Your Containers

```bash
# Without a name — Docker assigns a random name
docker run -d my-app
# Container name: quirky_einstein (random)

# With a name — you choose
docker run -d --name my-api-container my-app
# Container name: my-api-container
```

### Docker Desktop — Image ID vs Name

If you run a container using the **image ID** instead of the **image name**, Docker Desktop will show the ID in the image column:

```bash
# Shows image NAME in Docker Desktop
docker run --name api book-api:dev

# Shows image ID in Docker Desktop
docker run --name api 823baca1ca4d
```

It's the same image — just a display difference. Always use `image:tag` format for clarity.

---

## Part 6: Port Mapping — Connecting to Your Container

Containers are **isolated**. By default, you can't access anything running inside them from your machine. Port mapping creates a tunnel.

### How `-p` Works

```
-p HOST_PORT:CONTAINER_PORT

Your PC (Host)              Docker Container
──────────────              ────────────────
localhost:8000  ──────────► port 8000 (your app)
```

```bash
docker run -p 8000:8000 my-api
# Access at: http://localhost:8000
```

> **Critical:** Your app inside the container must listen on `0.0.0.0`, not `127.0.0.1`:
> ```python
> # CORRECT — accessible from outside the container
> uvicorn main:app --host 0.0.0.0 --port 8000
>
> # WRONG — only accessible inside the container
> uvicorn main:app --host 127.0.0.1 --port 8000
> ```

### What Happens with Duplicate Ports?

One host port can only be used by **one container** at a time:

```bash
docker run -d -p 8000:8000 --name api-1 my-api   # Works
docker run -d -p 8000:8000 --name api-2 my-api   # ERROR: port already in use
```

### Running Multiple Containers — Use Different Host Ports

```bash
docker run -d -p 8000:8000 --name api-1 my-api   # localhost:8000
docker run -d -p 8001:8000 --name api-2 my-api   # localhost:8001
docker run -d -p 8002:8000 --name api-3 my-api   # localhost:8002
```

```
Your PC (Host)              Docker Containers
──────────────              ──────────────────
localhost:8000  ──────────► port 8000  (api-1)
localhost:8001  ──────────► port 8000  (api-2)
localhost:8002  ──────────► port 8000  (api-3)
```

All three containers run on port 8000 **internally**, but your PC accesses them on different ports.

---

## Part 7: Hands-On: Containerizing a FastAPI Application

Now let's build something real — a FastAPI application in a Docker container.

### Step 1: Project Structure

Create a folder called `fastapi-docker` with this structure:

```
fastapi-docker/
├── app/
│   └── main.py
├── requirements.txt
└── Dockerfile
```

### Step 2: Create the Application

**`app/main.py`**
```python
from fastapi import FastAPI

app = FastAPI(
    title="Workshop API",
    description="A containerized FastAPI application",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Hello from Docker!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/items/{item_id}")
def get_item(item_id: int):
    return {"item_id": item_id, "name": f"Item {item_id}"}
```

**`requirements.txt`**
```
fastapi==0.115.0
uvicorn==0.30.0
```

### Step 3: Write the Dockerfile

**`Dockerfile`**
```dockerfile
# Base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variable for real-time Python logs
ENV PYTHONUNBUFFERED=1

# Copy and install dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Document the port
EXPOSE 8000

# Image metadata
LABEL NAME="Workshop FastAPI App" \
      VERSION="1.0" \
      AUTHOR="Your Name"

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Why copy `requirements.txt` before `COPY . .`?**

Docker caches each layer. If your code changes but `requirements.txt` doesn't, Docker **reuses the cached dependency layer** instead of reinstalling everything. This makes rebuilds much faster.

```
Layer 1: FROM python:3.13-slim          ← cached
Layer 2: COPY requirements.txt .        ← cached (file didn't change)
Layer 3: RUN pip install ...            ← cached (requirements same)
Layer 4: COPY . .                       ← rebuilt (code changed)
```

### Step 4: Build and Run

```bash
# Build the image
docker build -t workshop-api:v1 .

# Run the container
docker run -d -p 8000:8000 --name workshop-api workshop-api:v1
```

### Step 5: Test It

Open your browser:

- **API Root:** http://localhost:8000
- **Swagger Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Get Item:** http://localhost:8000/items/42

Or use curl:
```bash
curl http://localhost:8000
curl http://localhost:8000/health
curl http://localhost:8000/items/42
```

### Step 6: Check Image Size

```bash
docker images workshop-api
```

You'll see it's around **200-250 MB**. We can do better with multi-stage builds.

---

## Part 8: Multi-Stage Builds — Optimizing Image Size

A normal Dockerfile puts everything (build tools, temp files, dependencies) into one image. Multi-stage builds let you **build in one stage** and **copy only what you need** to a smaller final image.

### Single-Stage (What We Have Now)

```dockerfile
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Multi-Stage (Optimized)

Create a new file called `Dockerfile.multistage`:

```dockerfile
# ============================================
# Stage 1: Builder — install dependencies here
# ============================================
FROM python:3.13 AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --target=/app/dependencies -r requirements.txt

# ============================================
# Stage 2: Final — slim image with only what we need
# ============================================
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Copy installed packages from builder stage
COPY --from=builder /app/dependencies /usr/local/lib/python3.13/site-packages/

# Copy application code
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**How it works:**

```
Stage 1 (builder):                    Stage 2 (final):
┌─────────────────────────┐          ┌─────────────────────────┐
│ python:3.13 (full ~1GB) │          │ python:3.13-slim (~150MB)│
│                         │          │                         │
│ - gcc, build tools      │          │ - No build tools        │
│ - pip, setuptools       │  COPY    │ - Installed packages ──►│ copied from Stage 1
│ - installed packages ───┼──────────│ - App code              │
│ - temp build files      │          │                         │
│                         │          │ MUCH SMALLER!           │
└─────────────────────────┘          └─────────────────────────┘
        THROWN AWAY                        FINAL IMAGE
```

### Build and Compare

```bash
# Build multi-stage version
docker build -f Dockerfile.multistage -t workshop-api:v2 .

# Compare sizes
docker images workshop-api
```

```
REPOSITORY     TAG    SIZE
workshop-api   v1     250MB   ← single-stage
workshop-api   v2     165MB   ← multi-stage (smaller!)
```

**Why smaller images matter:**
- Faster deployments (less to upload/download)
- Less storage cost
- Smaller attack surface (fewer tools for hackers to exploit)

---

## Part 9: Running Multiple Containers

### Scenario: Run 3 Instances of Your API

```bash
docker run -d -p 8000:8000 --name api-instance-1 workshop-api:v2
docker run -d -p 8001:8000 --name api-instance-2 workshop-api:v2
docker run -d -p 8002:8000 --name api-instance-3 workshop-api:v2
```

Now you have 3 APIs running:
- http://localhost:8000/docs
- http://localhost:8001/docs
- http://localhost:8002/docs

### Verify All Are Running

```bash
docker ps
```

```
NAME             IMAGE              PORTS
api-instance-1   workshop-api:v2   0.0.0.0:8000->8000/tcp
api-instance-2   workshop-api:v2   0.0.0.0:8001->8000/tcp
api-instance-3   workshop-api:v2   0.0.0.0:8002->8000/tcp
```

### Clean Up All Containers

```bash
# Stop all three
docker stop api-instance-1 api-instance-2 api-instance-3

# Remove all three
docker rm api-instance-1 api-instance-2 api-instance-3
```

---

## Quick Reference Cheat Sheet

### Images

| Action | Command |
|--------|---------|
| Pull an image | `docker pull python:3.13-slim` |
| List images | `docker images` |
| Build an image | `docker build -t name:tag .` |
| Build with custom Dockerfile | `docker build -f Dockerfile.dev -t name:tag .` |
| Tag an existing image | `docker tag <image-id> name:tag` |
| Remove an image | `docker rmi name:tag` |
| Force remove | `docker rmi -f name:tag` |

### Containers

| Action | Command |
|--------|---------|
| Run (foreground) | `docker run -p 8000:8000 image` |
| Run (detached) | `docker run -d -p 8000:8000 image` |
| Run (with name) | `docker run --name my-api image` |
| Run (auto-remove on stop) | `docker run --rm image` |
| List running containers | `docker ps` |
| List all containers | `docker ps -a` |
| Stop a container | `docker stop <name>` |
| Start a stopped container | `docker start <name>` |
| Start with output attached | `docker start -a <name>` |
| Remove a container | `docker rm <name>` |
| View logs | `docker logs <name>` |
| Follow logs live | `docker logs -f <name>` |

### Dockerfile Instructions

| Instruction | Purpose |
|------------|---------|
| `FROM` | Base image |
| `WORKDIR` | Set working directory |
| `COPY` | Copy files into image |
| `RUN` | Execute command during build |
| `CMD` | Default run command |
| `EXPOSE` | Document port |
| `ENV` | Set environment variable |
| `LABEL` | Add metadata |

---

## Common Mistakes to Avoid

| Mistake | Fix |
|---------|-----|
| Typos in image names (`silm` vs `slim`) | Read error messages carefully — they're literal |
| App listening on `127.0.0.1` | Use `0.0.0.0` inside containers |
| Not seeing Python `print()` output | Add `ENV PYTHONUNBUFFERED=1` to Dockerfile |
| Running two containers on the same host port | Map to different host ports: `-p 8001:8000` |
| Not tagging images | Always use `docker build -t name:tag .` |
| Using `docker run` instead of `docker start` | `run` creates new containers, `start` restarts existing |
| Large image sizes | Use `slim` base images or multi-stage builds |

---

## Part 10: Docker Layers — Understanding the Build Cache

Every instruction in a Dockerfile creates a **layer**. Understanding layers is key to writing fast, efficient Dockerfiles.

```
┌─────────────────────────┐
│ Layer 5: COPY . .       │  ← changes often (rebuild)
├─────────────────────────┤
│ Layer 4: RUN pip install│  ← cached if requirements unchanged
├─────────────────────────┤
│ Layer 3: COPY req.txt   │  ← cached if file unchanged
├─────────────────────────┤
│ Layer 2: WORKDIR /app   │  ← never changes
├─────────────────────────┤
│ Layer 1: FROM python    │  ← never changes
└─────────────────────────┘
```

### Three Key Rules

1. **Layers are read-only and shared** — multiple images using the same base share that layer on disk (saves storage)
2. **Cache breaks top-to-bottom** — if Layer 3 changes, everything below it (4, 5) also rebuilds
3. **Order matters** — put things that change rarely at the top, things that change often at the bottom

### See Layers Yourself

```bash
docker history workshop-api:v1
```

> This is why we copy `requirements.txt` before `COPY . .` — so changing your code doesn't force a full reinstall of packages.

---

## Part 11: Multi-Stage Builds with uv (Production FastAPI)

The earlier multi-stage example used pip. Here's the **production-ready version using uv**:

### Single-Stage (works but not optimized)

```dockerfile
FROM python:3.13-slim
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Problem: `uv` (~30MB) stays in the final image. You only need it during install, not at runtime.

### Multi-Stage with uv (optimized)

```dockerfile
# Stage 1: Install packages
FROM python:3.13-slim AS builder
WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Stage 2: Clean final image
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"
COPY --from=builder /app/.venv /app/.venv
COPY . .
EXPOSE 8000
CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]
```

**How it works:**
- `AS builder` — names Stage 1 so we can reference it
- `COPY --from=builder` — grabs the `.venv` folder from Stage 1 into Stage 2
- `ENV PATH=...` — lets the shell find `fastapi`/`uvicorn` without typing full paths
- Stage 1 is **thrown away** — only Stage 2 becomes the final image

```
Stage 1 (builder)                    Stage 2 (final)
┌──────────────────────┐            ┌──────────────────────┐
│  pip, uv, build tools│            │  NO pip, NO uv       │
│  .venv/ (packages) ──┼── COPY ───►  .venv/ (packages)   │
│                      │            │  your FastAPI code   │
└──────────────────────┘            └──────────────────────┘
     THROWN AWAY                        FINAL IMAGE (smaller)
```

---

## Part 12: Volumes — Persisting Data

Containers are **ephemeral** — delete a container, all data inside is lost. Volumes solve this by storing data **outside** the container.

### Without Volumes (dangerous)

```bash
docker rm my-database    # 💀 all data gone forever
```

### With Volumes (safe)

```bash
docker run -d \
  --name my-postgres \
  -v my-data:/var/lib/postgresql/data \
  -p 5432:5432 \
  postgres:16
```

```
Your Host Machine          Container
┌──────────────┐          ┌──────────────┐
│              │          │              │
│  my-data/  ◄─────────────► /var/lib/   │
│  (persists)  │          │  postgresql/ │
│              │          │              │
└──────────────┘          └──────────────┘
                          Delete container →
                          data survives on host
```

### Accessing Data Inside a Container

```bash
# Open a shell inside a running container
docker exec -it my-postgres bash

# Run a specific command
docker exec -it my-postgres psql -U postgres
```

| Flag | Meaning |
|------|---------|
| `-i` | Interactive (keep stdin open) |
| `-t` | Allocate a terminal |
| `-it` | Both — gives you a live shell |

### Volume Commands

| Action | Command |
|--------|---------|
| List volumes | `docker volume ls` |
| Inspect a volume | `docker volume inspect my-data` |
| Remove a volume | `docker volume rm my-data` |
| Remove all unused | `docker volume prune` |

> **Rule of thumb:** Any container that stores data (databases, uploads, logs) should use a volume.

---

## What's Next?

After mastering these fundamentals, your next steps are:

1. **Docker Compose** — define and run multi-container apps (e.g., FastAPI + PostgreSQL) with a single `docker-compose.yml` file
2. **Docker Networking** — connect containers to each other
3. **Deploying Docker containers** — Railway, Render, Fly.io, Google Cloud Run (free tiers available)
4. **Kubernetes** — orchestrate containers at scale

---

> **Workshop created by Faraz Ahmed**
> Built while learning from [The AI Agent Factory — Panaversity](https://agentfactory.panaversity.org/)
