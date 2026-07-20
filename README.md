# Distributed Load Balancer

## Project Overview

This project implements a distributed load balancing system using Docker containers. The system dynamically routes client requests across multiple server replicas using consistent hashing to achieve balanced load distribution. It also monitors server health and automatically replaces failed replicas.

## Group Members (4A)

164643 - GITAU MUGURE TRACY  
166142 - NJIHIA MURANGA  
168971 -PHILLIP GAKUO  
166370 - NAOMI TEKO CHENANGAT



## Technologies

- Python
- Flask
- Docker
- Docker Compose
- Requests Library

## Installation

Clone the repository

```bash
git clone < https://github.com/TMG-prog/DS_Project.git >
cd DS_Project
```

Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Project

Build Docker images

```bash
docker compose build
```

Start all services

```bash
docker compose up
```

Stop services

```bash
docker compose down
```
