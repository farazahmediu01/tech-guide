# Docker for Absolute Beginners — Hands-On Workshop

**Your First Container in 15 Minutes**

---

## Why Docker?

Imagine this: you build a Python app on your laptop. It works perfectly. You send it to a friend — it crashes. *"Works on my machine"* is the most frustrating sentence in software development.

Docker solves this by packaging your app **with its entire environment** — Python version, OS libraries, everything — into a single portable unit called a **container**.

> Think of it like shipping furniture. Without Docker, you ship loose parts and hope the other person has the right tools. With Docker, you ship the **entire assembled room**.

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- A terminal (Command Prompt, PowerShell, or any shell)
- A text editor (VS Code recommended)

Verify Docker is installed:

```bash
docker --version
```

You should see something like `Docker version 27.x.x`

---

## Core Concepts — Only 4 Things to Know

| Concept | What It Is | Real-World Analogy |
|---------|-----------|-------------------|
| **Image** | A blueprint/template for your app | A recipe |
| **Container** | A running instance of an image | The actual cooked dish |
| **Dockerfile** | Instructions to build an image | The recipe card |
| **Registry** | A place to store/share images | A cookbook library (Docker Hub) |

The flow is simple:

```
Dockerfile  -->  Image  -->  Container
 (write)       (build)       (run)
```

---

## Lab 1 — Hello from a Container

### Step 1: The Python App

Create a file called `app.py`:

```python
import time
import platform

def main():
    print("=" * 40)
    print("  Hello from inside a Docker container!")
    print("=" * 40)
    print(f"  Python version : {platform.python_version()}")
    print(f"  OS             : {platform.system()} {platform.release()}")
    print(f"  Architecture   : {platform.machine()}")
    print("=" * 40)

    for i in range(1, 11):
        print(f"  [{i}/10] Container is alive... ")
        time.sleep(1)

    print("\n  Done! Container finished successfully.")

if __name__ == "__main__":
    main()
```

Notice: this app prints system info. When you run it locally you'll see `Windows`. When you run it inside Docker, you'll see `Linux`. That's the magic — Docker runs a **Linux environment** regardless of your OS.

### Step 2: The Dockerfile

Create a file named `Dockerfile` (no extension) in the same folder:

```dockerfile
FROM python:3.14-slim
WORKDIR /app

COPY app.py ./

CMD ["python", "-u", "app.py"]
```

Let's break down each line:

| Line | What It Does |
|------|-------------|
| `FROM python:3.14-slim` | Start from an official Python image (small version) |
| `WORKDIR /app` | Set `/app` as the working directory inside the container |
| `COPY app.py ./` | Copy your file from your machine into the container |
| `CMD ["python", "-u", "app.py"]` | The command to run when the container starts |

> **Why `-u`?** It stands for "unbuffered". Without it, Python buffers print output and you might not see logs in real-time.

### Step 3: Build the Image

Open a terminal in the folder containing your `Dockerfile` and run:

```bash
docker build -t my-first-app .
```

- `-t my-first-app` — tags (names) your image
- `.` — tells Docker to look for the `Dockerfile` in the current directory

You'll see Docker downloading the Python base image and building your image layer by layer.

### Step 4: Run the Container

```bash
docker run my-first-app
```

You should see output like:

```
========================================
  Hello from inside a Docker container!
========================================
  Python version : 3.14.x
  OS             : Linux 6.x.x
  Architecture   : x86_64
========================================
  [1/10] Container is alive...
  [2/10] Container is alive...
  ...
```

**Notice the OS says Linux**, even though you're on Windows/Mac. That's Docker in action.

---

## Lab 2 — Build, Run, Debug Cycle

### Step 1: A Second App

Create a new folder and add `main.py`:

```python
import time

print("=== Docker Workshop Demo ===")
print("Hello from inside a Docker container!\n")

for i in range(1, 11):
    print(f"Processing item {i}/10...")
    time.sleep(1)

print("\nAll done! Container is working correctly.")
print("Container Stop.")
```

### Step 2: The Dockerfile

```dockerfile
FROM python:3.13-alpine

WORKDIR /app

COPY . .

CMD ["python", "-u", "main.py"]
```

Notice two differences from Lab 1:

| Difference | Lab 1 | Lab 2 |
|-----------|-------|-------|
| Base image | `python:3.14-slim` (Debian-based, ~150MB) | `python:3.13-alpine` (Alpine Linux, ~50MB) |
| COPY strategy | `COPY app.py ./` (specific file) | `COPY . .` (entire directory) |

> **`slim` vs `alpine`**: Alpine images are smaller but use `musl` instead of `glibc`. For simple Python scripts, either works. For production apps with C extensions, `slim` is usually safer.

### Step 3: Build and Run

```bash
docker build -t workshop-demo .
docker run workshop-demo
```

---

## Common Mistake: RUN vs CMD

This is the **#1 beginner mistake**. Spot the bug:

```dockerfile
# WRONG
FROM python:3.13-alpine
WORKDIR /app
COPY . .
RUN ["python", "-u", "main.py"]
```

```dockerfile
# CORRECT
FROM python:3.13-alpine
WORKDIR /app
COPY . .
CMD ["python", "-u", "main.py"]
```

| Instruction | When It Executes | Use Case |
|------------|-----------------|----------|
| `RUN` | During **image build** (`docker build`) | Installing packages, setting up the environment |
| `CMD` | When **container starts** (`docker run`) | Running your application |

If you use `RUN` for your app, it will execute during build and the container will have nothing to do when started.

---

## Essential Docker Commands — Cheat Sheet

### Images

```bash
docker build -t <name> .          # Build an image from Dockerfile
docker images                     # List all images
docker rmi <image>                # Remove an image
```

### Containers

```bash
docker run <image>                # Run a container
docker run -d <image>             # Run in background (detached)
docker run --name myapp <image>   # Run with a custom name
docker ps                         # List running containers
docker ps -a                      # List ALL containers (including stopped)
docker stop <container>           # Stop a running container
docker rm <container>             # Remove a stopped container
```

### Debugging

```bash
docker logs <container>           # View container output/logs
docker exec -it <container> sh    # Open a shell inside a running container
docker inspect <container>        # View detailed container info
```

### Cleanup

```bash
docker system prune               # Remove all stopped containers, unused images
```

---

## Understanding the Build Process

When you run `docker build`, Docker processes your Dockerfile **line by line**. Each line creates a **layer**:

```
Layer 4:  CMD ["python", "-u", "main.py"]     <-- metadata only
Layer 3:  COPY . .                             <-- your code
Layer 2:  WORKDIR /app                         <-- directory setup
Layer 1:  FROM python:3.13-alpine              <-- base OS + Python
```

Docker **caches** these layers. If you change only your code (Layer 3), Docker reuses Layers 1-2 from cache. This makes rebuilds fast.

---

## Quick Self-Check

Before you leave, make sure you can answer these:

1. What is the difference between an **image** and a **container**?
2. What does `FROM` do in a Dockerfile?
3. Why do we use `CMD` instead of `RUN` to start our app?
4. What does the `-t` flag do in `docker build -t myapp .`?
5. How do you see all running containers?
6. What is the difference between `python:3.14-slim` and `python:3.13-alpine`?

---

## What's Next?

Once you're comfortable with single containers, the next steps are:

- **Port Mapping** — expose your app to the browser with `-p 8000:8000`
- **Volumes** — persist data beyond container lifetime
- **Docker Compose** — run multi-container apps (API + Database)
- **Multi-Stage Builds** — optimize image size for production

---

*Workshop by [Faraz] | Built with Python + Docker | Part of the AI Agent Factory roadmap*
*Have questions? Drop a comment below.*
