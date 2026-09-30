"""Low-latency TCP reachability prober for network device fleets."""

from __future__ import annotations

import argparse
import csv
import ipaddress
import socket
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass


@dataclass(frozen=True)
class ProbeResult:
    """Outcome of a single TCP reachability probe."""

    host: str
    port: int
    reachable: bool
    latency_ms: float | None


def probe(host: str, port: int, timeout: float = 1.0) -> ProbeResult:
    """Probe a single TCP endpoint and measure connect latency.

    Args:
        host: Target IPv4 address.
        port: Target TCP port.
        timeout: Connect timeout in seconds.

    Returns:
        The probe outcome, including latency when reachable.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            start = time.perf_counter()
            sock.connect((host, port))
        except OSError:
            return ProbeResult(host, port, False, None)
        return ProbeResult(host, port, True, (time.perf_counter() - start) * 1000.0)


def probe_range(cidr: str, port: int, workers: int, timeout: float) -> list[ProbeResult]:
    """Probe every usable host in a CIDR block with a bounded worker pool.

    Args:
        cidr: Network range in CIDR notation (e.g. ``192.168.1.0/24``).
        port: Target TCP port for every host.
        workers: Maximum concurrent probe threads.
        timeout: Connect timeout in seconds.

    Returns:
        Probe outcomes, one per usable host.

    Raises:
        ValueError: If the CIDR block is invalid.
    """
    network = ipaddress.ip_network(cidr, strict=False)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(probe, str(host), port, timeout) for host in network.hosts()]
        return [future.result() for future in futures]


def write_csv(results: list[ProbeResult], output: str) -> None:
    """Write probe results to a CSV file.

    Args:
        results: Probe outcomes to persist.
        output: Destination CSV path.

    Raises:
        OSError: If the destination path cannot be written.
    """
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["host", "port", "reachable", "latency_ms"])
        writer.writerows(
            (
                result.host,
                result.port,
                result.reachable,
                f"{result.latency_ms:.2f}" if result.latency_ms is not None else "",
            )
            for result in results
        )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="TCP reachability prober for device fleets")
    parser.add_argument("--cidr", required=True, help="Network range in CIDR notation")
    parser.add_argument("--port", type=int, default=22, help="TCP port to probe (default: 22)")
    parser.add_argument("--workers", type=int, default=128, help="Concurrent probe threads")
    parser.add_argument("--timeout", type=float, default=1.0, help="Connect timeout in seconds")
    parser.add_argument("--output", default="probe_results.csv", help="Output CSV path")
    return parser.parse_args()


def main() -> int:
    """Entry point. Returns a process exit code."""
    args = parse_args()
    try:
        results = probe_range(args.cidr, args.port, args.workers, args.timeout)
        write_csv(results, args.output)
    except ValueError as exc:
        print(f"error: invalid CIDR block ({exc})", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    reachable = sum(1 for result in results if result.reachable)
    latencies = sorted(result.latency_ms for result in results if result.latency_ms is not None)
    p50 = latencies[len(latencies) // 2] if latencies else 0.0
    print(
        f"probed={len(results)} reachable={reachable} "
        f"p50_latency_ms={p50:.2f} output={args.output}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
