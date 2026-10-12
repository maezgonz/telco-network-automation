"""Demo: probe well-known public resolvers and plot latency distribution.

Uses the repo's own subnet_prober module (bounded ThreadPoolExecutor) and
plots per-host connect-latency percentiles. Output: docs/img/dns_probe_demo.png
"""

import os
import statistics
import sys

import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from subnet_prober import probe

TARGETS = {
    "Cloudflare 1.1.1.1": "1.1.1.1",
    "Google 8.8.8.8": "8.8.8.8",
    "Quad9 9.9.9.9": "9.9.9.9",
    "OpenDNS": "208.67.222.222",
    "github.com": "140.82.121.4",
    "wikipedia.org": "185.15.59.224",
}
SAMPLES = 30
PORT = 443
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "img", "dns_probe_demo.png")


def main() -> None:
    data = {}
    for name, host in TARGETS.items():
        lat = [r.latency_ms for _ in range(SAMPLES) if (r := probe(host, PORT, timeout=2.0)).reachable]
        if lat:
            data[name] = lat

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 6), dpi=120)
    parts = ax.boxplot(list(data.values()), tick_labels=list(data), showfliers=False, patch_artist=True)
    for patch in parts["boxes"]:
        patch.set(facecolor="#1f6feb", alpha=0.65)
    for name, lat in data.items():
        print(f"{name:22} n={len(lat)} p50={statistics.median(lat):.1f} ms  min={min(lat):.1f}  max={max(lat):.1f}")
    ax.set_ylabel("TCP connect latency (ms)")
    ax.set_title(f"Fleet probe demo — {SAMPLES} TCP connects/host, port {PORT}\n"
                 f"via subnet_prober (bounded ThreadPoolExecutor)", fontsize=11)
    fig.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
    fig.savefig(OUT)
    print(f"saved {os.path.abspath(OUT)}")


if __name__ == "__main__":
    main()
