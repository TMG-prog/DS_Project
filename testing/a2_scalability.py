import matplotlib
matplotlib.use("Agg")

import asyncio
import json
import os
import statistics
import time

import matplotlib.pyplot as plt
import requests

from client import run_load, tally_by_server, count_failures

LB_BASE_URL = "http://localhost:5000"
N_VALUES = [2, 3, 4, 5, 6]
REQUESTS_PER_N = 2000
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def get_current_replicas():
    r = requests.get(f"{LB_BASE_URL}/rep", timeout=5)
    r.raise_for_status()
    return r.json()["message"]["replicas"]


def scale_to(target_n, timeout=30):
    """
    Scale the load balancer to target_n replicas via /add or /rm,
    then poll /rep until the count matches (or raise on timeout).

    Note: /rm calls docker stop synchronously per container, and since
    the Flask dev server doesn't handle SIGTERM gracefully, Docker waits
    its full default 10s grace period before force-killing each one.
    So /rm needs a generous timeout, scaled to how many containers
    might be removed in one call.
    """
    current = get_current_replicas()
    delta = target_n - len(current)

    if delta > 0:
        resp = requests.post(f"{LB_BASE_URL}/add", json={"n": delta}, timeout=30)
        resp.raise_for_status()
    elif delta < 0:
        rm_timeout = max(30, 10 * (-delta) + 10)
        resp = requests.delete(f"{LB_BASE_URL}/rm", json={"n": -delta}, timeout=rm_timeout)
        resp.raise_for_status()

    deadline = time.time() + timeout
    while time.time() < deadline:
        replicas = get_current_replicas()
        if len(replicas) == target_n:
            time.sleep(3)  # grace period for newly spawned Flask containers to be ready
            return replicas
        time.sleep(1)

    raise RuntimeError(f"Timed out waiting for N={target_n}; still at {get_current_replicas()}")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    starting_replicas = get_current_replicas()
    print(f"Starting replicas: {starting_replicas}")

    means, stddevs, all_counts = [], [], {}

    for n in N_VALUES:
        print(f"\nScaling to N={n}...")
        replicas = scale_to(n)
        print(f"  Now at: {replicas}")

        print(f"  Firing {REQUESTS_PER_N} requests...")
        results = asyncio.run(run_load(REQUESTS_PER_N))
        counts = tally_by_server(results)
        failures = count_failures(results)

        values = [counts.get(server, 0) for server in replicas]
        mean = statistics.mean(values) if values else 0
        stddev = statistics.stdev(values) if len(values) > 1 else 0

        print(f"  Per-server counts: {dict(counts)}  (failures: {failures})")
        print(f"  Mean: {mean:.1f}, StdDev: {stddev:.1f}")

        means.append(mean)
        stddevs.append(stddev)
        all_counts[n] = {"replicas": replicas, "counts": dict(counts), "failures": failures}

    print("\nRestoring to N=3 baseline...")
    scale_to(3)

    summary = {
        "n_values": N_VALUES,
        "requests_per_n": REQUESTS_PER_N,
        "means": means,
        "stddevs": stddevs,
        "details": all_counts,
    }
    with open(os.path.join(RESULTS_DIR, "a2_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    plt.figure(figsize=(6, 4))
    plt.errorbar(N_VALUES, means, yerr=stddevs, marker="o", capsize=4, color="darkorange")
    plt.title(f"A-2: Avg requests/server vs N ({REQUESTS_PER_N} requests each)")
    plt.xlabel("Number of servers (N)")
    plt.ylabel("Avg requests per server")
    plt.xticks(N_VALUES)

    plt.tight_layout()
    chart_path = os.path.join(RESULTS_DIR, "a2_line.png")
    plt.savefig(chart_path)
    print(f"\nChart saved to {chart_path}")


if __name__ == "__main__":
    main()