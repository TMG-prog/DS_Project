import asyncio
import re
import time
from collections import Counter

import aiohttp

LB_BASE_URL = "http://localhost:5000"
SERVER_NAME_RE = re.compile(r"Hello from Server: (\S+)")


async def fetch_one(session, path="/home"):
    """
    Fire a single request through the load balancer.
    Returns (server_name, status_code, elapsed_seconds).
    server_name is None if the request failed or the response
    didn't match the expected 'Hello from Server: <id>' format.
    """
    url = f"{LB_BASE_URL}/{path.lstrip('/')}"
    start = time.perf_counter()
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            status = resp.status
            try:
                data = await resp.json()
            except Exception:
                data = {}
            message = str(data.get("message", ""))
            match = SERVER_NAME_RE.search(message)
            server_name = match.group(1) if match else None
            elapsed = time.perf_counter() - start
            return server_name, status, elapsed
    except Exception:
        elapsed = time.perf_counter() - start
        return None, None, elapsed


async def run_load(num_requests, concurrency=200, path="/home"):
    """
    Fire `num_requests` total requests at the load balancer, with at
    most `concurrency` in flight at once.
    Returns a list of (server_name, status_code, elapsed_seconds) tuples,
    one per request, in completion order.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def bound_fetch(session):
        async with semaphore:
            return await fetch_one(session, path)

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(bound_fetch(session)) for _ in range(num_requests)]
        return [await coro for coro in asyncio.as_completed(tasks)]


def tally_by_server(results):
    """Count successful (status 200) requests per server name."""
    return Counter(server for server, status, _ in results if server and status == 200)


def count_failures(results):
    """Count requests that errored or returned a non-200 status."""
    return sum(1 for _, status, _ in results if status != 200)


if __name__ == "__main__":
    # Smoke test: fire 100 requests and print the distribution.
    results = asyncio.run(run_load(100))
    counts = tally_by_server(results)
    print("Distribution over 100 requests:")
    for server, count in sorted(counts.items()):
        print(f"  {server}: {count}")
    failures = count_failures(results)
    if failures:
        print(f"  {failures} requests failed or errored")