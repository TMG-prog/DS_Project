import os
from flask import Flask, jsonify

app = Flask(__name__)

# Read the server ID from an environment variable.
# If none is provided, default to "Unknown".
SERVER_ID = os.getenv("SERVER_ID", "ServerDefault")


@app.route("/home", methods=["GET"])
def home():
    """
    Returns the identity of the server handling the request.
    """
    return jsonify({
        "message": f"Hello from Server: {SERVER_ID}",
        "status": "successful"
    }), 200


@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    """
    Used by the load balancer to check if this server is alive.
    """
    return "", 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )