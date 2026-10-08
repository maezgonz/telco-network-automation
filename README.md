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
│   ├── subnet_prober.py      # parallel TCP reachability prober with latency stats
│   └── config_drift.py       # config drift detection vs golden baseline (difflib)
├── tests/
│   └── test_config_drift.py  # unit tests with fixed config samples
├── examples/
│   ├── baseline.cfg          # golden baseline sample
│   └── running.cfg           # drifted running-config sample
├── pyproject.toml            # ruff lint config
├── .pre-commit-config.yaml
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

### Config drift detection

Diff a running config against its golden baseline: added/removed lines with security-critical patterns (`password`, `snmp`, `tacacs`, `ssh-key`, ...) flagged, exported as CSV:

```bash
python -m src.config_drift --running examples/running.cfg --baseline examples/baseline.cfg
# drift=9 added=6 removed=3 sensitive=2 output=drift_report.csv
```

## Results

Sample drift run (examples/ vs golden baseline):

| Metric | Value |
|---|---:|
| Drift findings | 9 |
| Lines added / removed | 6 / 3 |
| Security-sensitive findings | 2 (SNMP community + HTTP server) |

## Roadmap

- [x] Configuration drift detection against golden baselines
- [ ] NETCONF/RESTCONF configuration push with dry-run validation
- [ ] Device inventory collection from controller REST APIs
- [ ] Alarm correlation for RAN KPI degradation

## License

[MIT](LICENSE) — Matias Gonzalez
