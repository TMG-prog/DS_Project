import matplotlib
matplotlib.use("Agg")

import asyncio
import json
import os

import matplotlib.pyplot as plt

from client import run_load, tally_by_server, count_failures

NUM_REQUESTS = 10_000
RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print(f"Firing {NUM_REQUESTS} requests at the load balancer (N=3 expected)...")
    results = asyncio.run(run_load(NUM_REQUESTS))

    counts = tally_by_server(results)
    failures = count_failures(results)

    print("\nDistribution:")
    for server, count in sorted(counts.items()):
        pct = 100 * count / NUM_REQUESTS
        print(f"  {server}: {count} ({pct:.1f}%)")
    print(f"  Failures/errors: {failures}")

    # Save raw counts as JSON for the README write-up.
    summary = {
        "num_requests": NUM_REQUESTS,
        "counts": dict(counts),
        "failures": failures,
    }
    with open(os.path.join(RESULTS_DIR, "a1_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)

    # Bar chart.
    servers = sorted(counts.keys())
    values = [counts[s] for s in servers]

    plt.figure(figsize=(6, 4))
    plt.bar(servers, values, color="steelblue")
    plt.title(f"A-1: Request distribution across N=3 servers ({NUM_REQUESTS} requests)")
    plt.xlabel("Server")
    plt.ylabel("Requests handled")
    plt.tight_layout()
    chart_path = os.path.join(RESULTS_DIR, "a1_bar.png")
    plt.savefig(chart_path)
    print(f"\nChart saved to {chart_path}")


if __name__ == "__main__":
    main()