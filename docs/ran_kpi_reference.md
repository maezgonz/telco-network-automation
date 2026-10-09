# RAN KPI Reference — 3GPP-Standard Definitions

> Industry-standard KPI definitions for mobile network quality (GSM/UMTS/LTE/NR), following 3GPP performance measurement frameworks. Targets shown are typical industry values — every operator tunes their own.

## Why KPIs matter for engineering

KPIs translate raw network counters into engineering decisions: accessibility tells you if subscribers can connect, retainability if they stay connected, mobility if the network moves them seamlessly. Every optimization, upgrade or swap is validated against KPI baselines — a change that degrades KPIs beyond tolerance rolls back, no matter how well it "worked".

## 1. Accessibility — can subscribers connect?

| KPI | Formula (3GPP) | Typical target |
|---|---|---:|
| RRC Setup Success Rate (LTE/NR) | successful RRC setups / attempts | > 99.5% |
| E-RAB / QoS Flow Setup Success Rate | successful E-RAB setups / attempts | > 99.5% |
| CS Call Setup Success Rate (2G/3G) | successful call setups / attempts | > 99% |

**Engineering drivers:** radio coverage (RSSI/RSRP/RSRQ), congestion (PRB/license limits), signaling failures (core-side), parameter errors (RACH config, admission control).

## 2. Retainability — do subscribers stay connected?

| KPI | Formula (3GPP) | Typical target |
|---|---|---:|
| E-RAB Drop Rate (LTE/NR) | abnormal E-RAB releases / successful setups | < 0.5% |
| Call Drop Rate (CS) | abnormal releases / successful calls | < 1% |

**Engineering drivers:** coverage holes, neighbor relation gaps (missing/incorrect ANR), interference, hardware faults (TRX/clock), transport instability.

## 3. Mobility — does the network move subscribers seamlessly?

| KPI | Formula (3GPP) | Typical target |
|---|---|---:|
| Intra-frequency HO Success Rate | successful HO / attempts | > 99% |
| Inter-frequency HO Success Rate | successful HO / attempts | > 98% |
| Inter-RAT HO Success Rate (LTE↔UMTS/GSM) | successful HO / attempts | > 98% |

**Engineering drivers:** neighbor lists (ANR efficiency), HO thresholds (A3/A5 events and hysteresis), coverage imbalances, PCI confusion (LTE/NR).

## 4. Utilization & Capacity — is there headroom?

| KPI | Formula | Healthy range |
|---|---|---|
| PRB Utilization (DL/UL) | used PRBs / available PRBs | < 70% peak |
| Cell Availability | available time / total time | > 99.9% |
| Active users per cell | connected users / cell | vendor/license dependent |

**Engineering drivers:** traffic growth vs. capacity planning, spectrum refarming opportunities, carrier adds, load balancing parameters (mobility-based balancing).

## 5. The KPI workflow in practice

1. **Baseline**: record 24h KPI before any change
2. **Change**: upgrade, swap, reconfiguration, refarm
3. **Post-check**: compare KPIs vs. baseline (2h immediate + 24h full)
4. **Tolerance**: degradation beyond tolerance (e.g. > 0.2% drop-rate increase) → rollback
5. **Trend analysis**: weekly/monthly degradation trends drive optimization priorities

## How this maps to the tooling in this repository

- `src/config_drift.py` catches configuration drift that silently degrades KPIs (missing neighbors, altered thresholds)
- `src/subnet_prober.py` gates deployments on fleet reachability before changes
- `examples/mop_template.md` embeds the baseline/post-check/tolerance workflow into change management
