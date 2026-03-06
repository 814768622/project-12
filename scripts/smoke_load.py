#!/usr/bin/env python3
"""Simple HTTP smoke load tool using Python standard library.

Usage:
  python scripts/smoke_load.py --base-url http://localhost:8000 --path /v1/health --requests 200 --concurrency 20
"""

from __future__ import annotations

import argparse
import statistics
import threading
import time
import urllib.error
import urllib.request
from queue import Queue



def worker(base_url: str, path: str, timeout: float, jobs: Queue[int], results: list[float], errors: list[str], lock: threading.Lock) -> None:
    while True:
        try:
            jobs.get_nowait()
        except Exception:
            return

        start = time.perf_counter()
        try:
            with urllib.request.urlopen(f"{base_url.rstrip('/')}{path}", timeout=timeout) as resp:
                _ = resp.read()
                if resp.status >= 400:
                    with lock:
                        errors.append(f"HTTP {resp.status}")
        except urllib.error.URLError as exc:
            with lock:
                errors.append(str(exc))
        finally:
            elapsed_ms = (time.perf_counter() - start) * 1000
            with lock:
                results.append(elapsed_ms)
            jobs.task_done()



def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int((len(ordered) - 1) * p)
    return ordered[idx]



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--path", default="/v1/health")
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=20)
    parser.add_argument("--timeout", type=float, default=5.0)
    args = parser.parse_args()

    jobs: Queue[int] = Queue()
    for i in range(args.requests):
        jobs.put(i)

    results: list[float] = []
    errors: list[str] = []
    lock = threading.Lock()

    threads = [
        threading.Thread(
            target=worker,
            args=(args.base_url, args.path, args.timeout, jobs, results, errors, lock),
            daemon=True,
        )
        for _ in range(max(1, args.concurrency))
    ]

    started = time.perf_counter()
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total_s = time.perf_counter() - started

    ok_count = len(results) - len(errors)
    print("=== Smoke Load Result ===")
    print(f"total_requests: {len(results)}")
    print(f"success: {ok_count}")
    print(f"errors: {len(errors)}")
    print(f"duration_s: {total_s:.2f}")
    if results:
        print(f"avg_ms: {statistics.mean(results):.2f}")
        print(f"p95_ms: {percentile(results, 0.95):.2f}")
        print(f"p99_ms: {percentile(results, 0.99):.2f}")
    if errors:
        print("sample_error:", errors[0])


if __name__ == "__main__":
    main()
