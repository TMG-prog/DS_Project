import json
import os
import subprocess
import time

import requests

LB_BASE_URL = "http://localhost:5000"
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")

log_lines = []


def log(msg):
    print(msg)
    log_lines.append(str(msg))


def get_rep():
    r = requests.get(f"{LB_BASE_URL}/rep", timeout=5)
    return r.status_code, r.json()


def test_rep():
    log("\nGET /rep")
    status, body = get_rep()
    log(f"-> {status}: {body}")
    return body["message"]["replicas"]


def test_add_valid():
    log("\nPOST /add (valid: n=1, hostnames=[TestServerA])")
    r = requests.post(
        f"{LB_BASE_URL}/add",
        json={"n": 1, "hostnames": ["TestServerA"]},
        timeout=30,
    )
    log(f"-> {r.status_code}: {r.json()}")


def test_add_error():
    log("\nPOST /add (error case: hostnames longer than n)")
    r = requests.post(
        f"{LB_BASE_URL}/add",
        json={"n": 1, "hostnames": ["X", "Y"]},
        timeout=10,
    )
    log(f"-> {r.status_code}: {r.json()}")


def test_rm_valid(hostname):
    log(f"\nDELETE /rm (valid: n=1, hostnames=[{hostname}])")
    r = requests.delete(
        f"{LB_BASE_URL}/rm",
        json={"n": 1, "hostnames": [hostname]},
        timeout=60,
    )
    log(f"-> {r.status_code}: {r.json()}")


def test_rm_error():
    log("\nDELETE /rm (error case: hostnames longer than n)")
    r = requests.delete(
        f"{LB_BASE_URL}/rm",
        json={"n": 1, "hostnames": ["X", "Y"]},
        timeout=10,
    )
    log(f"-> {r.status_code}: {r.json()}")


def test_forward_valid():
    log("\nGET /home (valid forwarded endpoint)")
    r = requests.get(f"{LB_BASE_URL}/home", timeout=10)
    log(f"-> {r.status_code}: {r.json()}")


def test_forward_invalid():
    log("\nGET /doesnotexist (invalid forwarded endpoint)")
    r = requests.get(f"{LB_BASE_URL}/doesnotexist", timeout=10)
    log(f"-> {r.status_code}: {r.json()}")


def test_failure_recovery(timeout=30):
    log("\nFailure recovery test")
    replicas = get_rep()[1]["message"]["replicas"]
    if not replicas:
        log("No replicas available to kill, skipping.")
        return None

    target = replicas[0]
    expected_n = len(replicas)
    log(f"Killing container '{target}' directly via docker kill (expected N stays at {expected_n})")

    start = time.time()
    subprocess.run(["docker", "kill", target], check=True, capture_output=True)

    recovered = False
    current = replicas
    while time.time() - start < timeout:
        _, body = get_rep()
        current = body["message"]["replicas"]
        if target not in current and len(current) == expected_n:
            recovered = True
            break
        time.sleep(1)

    elapsed = time.time() - start
    if recovered:
        log(f"Recovered in {elapsed:.1f}s. New replicas: {current}")
        return elapsed
    else:
        log(f"Did NOT recover within {timeout}s. Current replicas: {current}")
        return None


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    test_rep()
    test_add_valid()
    test_add_error()
    replicas = test_rep()
    if "TestServerA" in replicas:
        test_rm_valid("TestServerA")
    test_rm_error()
    test_forward_valid()
    test_forward_invalid()

    recovery_time = test_failure_recovery()

    summary = {"recovery_time_seconds": recovery_time, "log": log_lines}
    summary_path = os.path.join(RESULTS_DIR, "a3_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    log(f"\nSaved summary to {summary_path}")


if __name__ == "__main__":
    main()