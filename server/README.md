# Server

Simple Flask server used by the Distributed Load Balancer.

## Endpoints

GET /home

Returns

{
    "message": "Hello from Server: X",
    "status": "successful"
}

GET /heartbeat

Returns HTTP 200 if the server is alive.

## Run locally

python app.py

## Docker

docker build -t server-image .

docker run -p 5000:5000 -e SERVER_ID=1 server-image