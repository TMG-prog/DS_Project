import os
import uuid
import random
import threading
import time
import requests
from flask import Flask, jsonify, request

from consistent_hash import ConsistentHashRing

app = Flask(__name__)

M = 512
K = 9
INITIAL_SERVERS = 3
NETWORK_NAME = "net1"
SERVER_IMAGE = "server-image"

ring = ConsistentHashRing(slots=M, virtual_servers_per_instance=K)
servers = []


def spawn_server(hostname):
    cmd = (
        f"docker run -d --name {hostname} "
        f"--network {NETWORK_NAME} "
        f"--network-alias {hostname} "
        f"-e SERVER_ID={hostname} "
        f"{SERVER_IMAGE}"
    )

    result = os.system(cmd)

    if result == 0:
        servers.append(hostname)
        ring.add_server(hostname)
        return True
    return False


def remove_server(hostname):
    os.system(f"docker stop {hostname} > /dev/null 2>&1")
    os.system(f"docker rm {hostname} > /dev/null 2>&1")

    if hostname in servers:
        servers.remove(hostname)
        ring.remove_server(hostname)


for i in range(1, INITIAL_SERVERS + 1):
    spawn_server(f"Server{i}")


def heartbeat_monitor():
    while True:
        time.sleep(5)

        for server in list(servers):
            try:
                r = requests.get(f"http://{server}:5000/heartbeat", timeout=2)
                if r.status_code != 200:
                    raise Exception()
            except Exception:
                print(f"[FAILURE] {server} is down")
                remove_server(server)

                new_name = f"S{uuid.uuid4().hex[:5]}"
                spawn_server(new_name)
                print(f"[RECOVERY] Spawned {new_name}")


threading.Thread(target=heartbeat_monitor, daemon=True).start()


@app.route("/rep", methods=["GET"])
def replicas():
    return jsonify({
        "message": {
            "N": len(servers),
            "replicas": servers
        },
        "status": "successful"
    }), 200


@app.route("/add", methods=["POST"])
def add_servers():
    data = request.get_json()
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:
        return jsonify({
            "message": "<Error> Length of hostname list is more than newly added instances",
            "status": "failure"
        }), 400

    for name in hostnames:
        spawn_server(name)

    for _ in range(n - len(hostnames)):
        spawn_server(f"S{uuid.uuid4().hex[:5]}")

    return jsonify({
        "message": {
            "N": len(servers),
            "replicas": servers
        },
        "status": "successful"
    }), 200


@app.route("/rm", methods=["DELETE"])
def rm_servers():
    data = request.get_json()
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:
        return jsonify({
            "message": "<Error> Length of hostname list is more than removable instances",
            "status": "failure"
        }), 400

    removed = set()

    for name in hostnames:
        if name in servers:
            remove_server(name)
            removed.add(name)

    remaining = n - len(removed)
    candidates = [s for s in servers if s not in removed]
    random.shuffle(candidates)

    for name in candidates[:remaining]:
        remove_server(name)

    return jsonify({
        "message": {
            "N": len(servers),
            "replicas": servers
        },
        "status": "successful"
    }), 200


@app.route("/<path:path>", methods=["GET"])
def forward(path):
    request_id = random.randint(100000, 999999)
    server = ring.get_server(request_id)

    if server is None:
        return jsonify({
            "message": "<Error> No active server replicas",
            "status": "failure"
        }), 500

    try:
        r = requests.get(f"http://{server}:5000/{path}", timeout=5)

        if r.status_code == 404:
            return jsonify({
                "message": f"<Error> '/{path}' endpoint does not exist in server replicas",
                "status": "failure"
            }), 400

        return jsonify(r.json()), r.status_code

    except Exception:
        return jsonify({
            "message": "<Error> Failed to forward request",
            "status": "failure"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)