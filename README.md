# telco-network-automation

![License](https://img.shields.io/badge/License-MIT-blue)
![Language](https://img.shields.io/badge/Python-stdlib%20%7C%20concurrent-3776AB)
![CI](https://github.com/maezgonz/telco-network-automation/actions/workflows/ci.yml/badge.svg)

## Objective

Network automation tooling distilled from **10+ years of carrier-grade telecom engineering** at Telefónica Argentina (2G/3G/4G/5G, core and access, Ericsson/Huawei/ZTE). The repository applies the performance discipline of HPC to network operations: bounded concurrency, strict timeouts and measurable latency — not fire-and-forget scripts.

## Architecture

```text
┌───────────────────┐    ┌──────────────────────┐    ┌───────────────┐
│  device fleet     │───▶│  src/ (probers, IaC) │───▶│  CSV reports  │
│  RAN / core nodes │    │  bounded thread pool │    │  latency p50  │
└───────────────────┘    └──────────────────────┘    └───────────────┘
```

- **`src/`** — stdlib-only, dependency-light automation modules that run on any jump host or CI runner.
- Every network interaction is bounded by explicit timeouts and a capped worker pool to protect production networks.

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ (stdlib only) |
| Concurrency | `concurrent.futures` (bounded `ThreadPoolExecutor`) |
| Networking | `socket`, `ipaddress` |
| Reporting | CSV export, latency percentile summaries |
| CI | GitHub Actions (ruff lint + smoke test) |

## Repository Layout

```text
telco-network-automation/
├── src/
│   ├── __init__.py
│   └── subnet_prober.py      # parallel TCP reachability prober with latency stats
├── requirements-free         # stdlib only: no pip install needed
└── .github/workflows/ci.yml
```

## Execution

```bash
python -m src.subnet_prober --cidr 192.168.1.0/24 --port 22 --workers 128
# probed=254 reachable=12 p50_latency_ms=1.84 output=probe_results.csv
```

Useful for fleet health checks before configuration rollouts:

```bash
# gate a deployment on fleet reachability
python -m src.subnet_prober --cidr 10.20.0.0/22 --port 830 --output netconf_gate.csv
```

## Results

Sample run against a simulated /24 fleet (SSH port 22):

| Metric | Value |
|---|---:|
| Hosts probed | 254 |
| Reachable | TBD |
| p50 connect latency | TBD |

![Fleet reachability](results/fleet_reachability.png)

> Reports are exported as CSV per run; figures are populated as case studies are added.

## Roadmap

- [ ] NETCONF/RESTCONF configuration push with dry-run validation
- [ ] Device inventory collection from controller REST APIs
- [ ] Configuration drift detection against golden baselines
- [ ] Alarm correlation for RAN KPI degradation

## License

[MIT](LICENSE) — Matias Gonzalez
