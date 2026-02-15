Docker in 5 Minutes — A Beginner's Cheat Sheet

I ran a workshop on Docker basics. Here's everything you need to get your first container running.

--

The Problem:
Your app works on your machine. You send it to someone else — it crashes. Docker fixes this by packaging your app WITH its entire environment into a portable unit called a container.

--

Only 4 concepts to learn:

Dockerfile --> Image --> Container

- Dockerfile = instructions (the recipe)
- Image = built template (the blueprint)
- Container = running instance (the actual app)
- Registry = where images are stored (Docker Hub)

--

Your first Dockerfile (3 lines that matter):

FROM python:3.14-slim
WORKDIR /app
COPY app.py ./
CMD ["python", "-u", "app.py"]

FROM = base image (OS + language)
WORKDIR = set working directory
COPY = move your code in
CMD = what runs when container starts

--

Build and run:

docker build -t my-app .
docker run my-app

That's it. Your app is now running inside Linux, even if you're on Windows.

--

The #1 beginner mistake:

Using RUN instead of CMD.

RUN executes during BUILD (for installing packages)
CMD executes during RUN (for starting your app)

Wrong: RUN ["python", "app.py"]
Right: CMD ["python", "app.py"]

--

Commands you'll use daily:

docker build -t name .        Build image
docker run name               Run container
docker ps                     List running containers
docker ps -a                  List all containers
docker logs container          View logs
docker stop container          Stop container
docker system prune           Clean everything up

--

What's next after this:
- Port mapping (-p 8000:8000)
- Volumes (persist data)
- Docker Compose (multi-container apps)

--

Save this for later. Follow for more cloud-native content.

#Docker #DevOps #Python #CloudNative #Containers #SoftwareEngineering #Workshop
