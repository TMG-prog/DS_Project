# TASK ONE SERVER IMPLEMENTATION

## Overview

This module implements the server component of the distributed load balancing system. The server is responsible for processing client requests forwarded by the load balancer and responding with its unique server identifier. It also provides a heartbeat endpoint that allows the load balancer to monitor the health of each server replica.

---

## Technologies Used

- Python 3
- Flask
- Docker

---

## API Endpoints

### GET /home

Returns the identity of the server handling the request.

**Example Response**

```json
{
    "message": "Hello from Server: 1",
    "status": "successful"
}
```

---

### GET /heartbeat

Returns an HTTP 200 OK response to indicate that the server is active and healthy.

---

## Design Choices

### 1. Flask Framework

The server was implemented using Flask because it is a lightweight Python web framework that simplifies the development of REST APIs. Since the server only provides two endpoints, Flask offers a clean and efficient solution with minimal overhead.

### 2. Environment Variables

The server identifier is obtained from the `SERVER_ID` environment variable instead of being hardcoded.

This design allows the same Docker image to be reused for multiple server replicas. Each replica is assigned a different server ID when the container is started, making the solution scalable and easy to manage.

### 3. Stateless Server

The server was designed to be stateless, meaning it does not store client session information. Every request is processed independently, allowing any server replica to handle incoming requests.

This simplifies scaling and enables failed replicas to be replaced without affecting the system.

### 4. Docker Containerization

The server is packaged inside a Docker container to ensure consistent deployment across different environments.

Containerization provides the following benefits:

- Consistent execution environment
- Easy deployment
- Simplified replication
- Better portability
- Supports horizontal scaling

### 5. Health Monitoring

The `/heartbeat` endpoint allows the load balancer to periodically verify that each server replica is still running. If a server becomes unavailable, the load balancer can detect the failure and create a replacement replica.

---

## Assumptions

- Docker is installed and configured correctly.
- Each server container is assigned a unique `SERVER_ID` environment variable.
- The server communicates with the load balancer using HTTP.
- The application runs on port 5000 inside the Docker container.

---

## Summary

The server component provides the foundation for the distributed load balancing system. It exposes the required REST endpoints, identifies itself using environment variables, supports health monitoring through heartbeat checks, and is containerized using Docker to enable the deployment of multiple server replicas.


## Run locally

python app.py

## Docker

docker build -t server-image .

docker run -p 5000:5000 -e SERVER_ID=1 server-image
