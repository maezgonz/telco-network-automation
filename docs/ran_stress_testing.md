# RAN Controller Stress Testing & Redundancy Validation — Methodology

> Anonymized methodology write-up from large-scale controller upgrades and migrations (mobile networks, 2G/3G/4G/5G). No vendor or operator data — the workflow is industry practice.

## Objective

Validate that a RAN controller platform (BSC/RNC/eNodeB controller or their successor architectures) sustains **massive traffic surges and component failures while holding service availability above the availability target** (industry-standard: 99.9%).

## 1. Test taxonomy

| Test type | What it validates | Risk addressed |
|---|---|---|
| **Redundancy (failover) test** | Standby unit takes over when active fails | Single point of failure |
| **Stress/load test** | Platform holds service under traffic surge | Capacity cliff during incidents |
| **Recovery (MTTR) test** | Time from injected failure to full service | Downtime duration |
| **Stability (soak) test** | No memory leaks/degradation over sustained load | Latent instability in production |

## 2. The methodology

### Phase 1 — Baseline capture
- Record controller state: CPU/memory/load per unit, board states, transport throughput
- Record KPI baseline: accessibility, retainability, drop rates (24h window)
- Record alarm state (clean, unrelated alarms ticketed)

### Phase 2 — Load generation
- Generate traffic at and beyond expected peak (1× → 1.5× → stress levels)
- Monitor: throughput, CPU, latency, error rates
- **Pass criteria**: service holds with expected degradation curve — no cliff

### Phase 3 — Failure injection (the critical phase)
- Inject redundancy events: pull the active unit, kill processes, saturate transport
- Measure during EVERY injection:
  - **Failover time**: active → standby switchover duration
  - **Service impact**: drop rate spike during switchover
  - **Recovery**: time to full KPI restoration
- **Pass criteria**: switchover within vendor spec, drop spike within tolerance, no stuck sessions

### Phase 4 — Post-test validation
- KPIs return to baseline within tolerance
- No new critical/major alarms
- Controller state clean (no leaked sessions, no failed processes)

### Phase 5 — Report & sign-off
- Results table per test type with measured values vs. pass criteria
- Findings classified: blocking / non-blocking (with workaround) / advisory
- Sign-off by implementer, reviewer and operator acceptance — see `examples/atp_template.md`

## 3. What experience teaches (the parts that don't fit in a table)

- **The failover that works in the lab may fail at scale** — always test at production-like load, not idle load
- **MTTR is dominated by diagnosis, not the switchover** — instrument everything before injecting failures, or you will not know what happened
- **Rollback must be time-boxed** — a rollback that takes longer than the business can tolerate is not a rollback plan
- **Test the boring paths too**: power feeds, clock sync, transport redundancy — most production incidents start at the physical layer, not the application layer (14 years from electrical power systems to 5G core taught this the hard way)

## 4. Tooling in this repository

- `src/subnet_prober.py` — fleet reachability gates before stress campaigns
- `src/config_drift.py` — configuration baseline verification before/after testing
- `examples/atp_template.md` — the acceptance procedure wrapper for these campaigns
