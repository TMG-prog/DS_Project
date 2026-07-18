import matplotlib
matplotlib.use("Agg")

import asyncio
import json
import os
import statistics

import matplotlib.pyplot as plt

from client import run_load, tally_by_server, count_failures

NUM_REQUESTS = 10_000
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Firing {NUM_REQUESTS} requests at the load balancer (N=3, modified hash function)...")
    results = asyncio.run(run_load(NUM_REQUESTS))

    counts = tally_by_server(results)
    failures = count_failures(results)

    print("\nDistribution (modified hash):")
    for server, count in sorted(counts.items()):
        pct = 100 * count / NUM_REQUESTS
        print(f"  {server}: {count} ({pct:.1f}%)")
    print(f"  Failures/errors: {failures}")

    summary = {
        "num_requests": NUM_REQUESTS,
        "counts": dict(counts),
        "failures": failures,
    }
    with open(os.path.join(RESULTS_DIR, "a4_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    servers = sorted(counts.keys())
    values = [counts[s] for s in servers]

    plt.figure(figsize=(6, 4))
    plt.bar(servers, values, color="seagreen")
    plt.title(f"A-4: Distribution with modified hash function ({NUM_REQUESTS} requests)")
    plt.xlabel("Server")
    plt.ylabel("Requests handled")
    plt.tight_layout()
    chart_path = os.path.join(RESULTS_DIR, "a4_bar.png")
    plt.savefig(chart_path)
    print(f"\nChart saved to {chart_path}")

    baseline_path = os.path.join(RESULTS_DIR, "a1_summary.json")
    if os.path.exists(baseline_path):
        with open(baseline_path) as f:
            baseline = json.load(f)

        print("\nComparison vs. original hash (A-1 baseline):")
        print(f"{'Server':<12}{'Original':>12}{'Modified':>12}")
        all_servers = sorted(set(baseline["counts"].keys()) | set(counts.keys()))
        for server in all_servers:
            orig = baseline["counts"].get(server, 0)
            new = counts.get(server, 0)
            print(f"{server:<12}{orig:>12}{new:>12}")

        orig_values = list(baseline["counts"].values())
        orig_std = statistics.stdev(orig_values) if len(orig_values) > 1 else 0
        new_std = statistics.stdev(values) if len(values) > 1 else 0
        print(f"\nStdDev (original hash): {orig_std:.1f}")
        print(f"StdDev (modified hash): {new_std:.1f}")


if __name__ == "__main__":
    main()