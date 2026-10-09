# Alarm Management & Correlation — Patterns for RAN Operations

> Industry-standard alarm management patterns for RAN/core operations, distilled from large-scale NOC practice. Severity taxonomy follows ITU-T X.733 / 3GPP TS 32.111.

## 1. Severity taxonomy (ITU-T X.733)

| Severity | Meaning | Response |
|---|---|---|
| **Critical** | Service down / imminent failure | Immediate action — pager/SMS escalation |
| **Major** | Service degraded, redundancy lost | Fast action — queue with SLA |
| **Minor** | Functional fault, service not impacted | Same-day triage |
| **Warning** | Latent condition (e.g. approaching threshold) | Preventive maintenance backlog |

## 2. Alarm lifecycle

```text
raised ──▶ acknowledged ──▶ (diagnosis + action) ──▶ cleared
                     │                                │
                     └── escalated if SLA breached ───┘
```

- **Raised → Acknowledged**: ownership taken; SLA clock runs
- **Acknowledged → Cleared**: diagnosis, action, verification
- **Unacknowledged alarms** are the NOC's biggest operational risk — they mean nobody owns the incident

## 3. Correlation patterns — finding the root cause in alarm storms

A single physical fault can raise dozens of downstream alarms. The skill is reading the storm top-down:

### Dependency cascade (the most common pattern)
```text
Transport link down  ──▶  BBU/Node unreachable  ──▶  all cells down  ──▶  HO failures on neighbors
     (ROOT CAUSE)              (symptom)                (symptom)            (symptom)
```
**Rule**: fix the root, the cascade clears itself. Acting on symptoms (restarting units) masks the fault and burns MTTR.

### Time-based correlation
- Alarms raised within the same second/minute window share a probable cause
- A storm starting right after a change → suspect the change (that is why MOPs require pre/post alarm captures)

### Topological correlation
- Alarms across all cells on one subrack → hardware/power at that subrack
- Alarms on cells sharing one transport route → transport fault
- Alarms on one frequency band only → RF/interference issue (interference, not hardware)

### KPI-based confirmation
- Correlate the alarm window with KPI degradation: a real fault shows in accessibility/retainability
- Alarm storms WITHOUT KPI impact often point to faulty sensors or marginal (not service-affecting) conditions

## 4. From reactive alarms to proactive KPIs

Mature operations move from alarm-reactive to KPI-proactive:

1. **Threshold alerts on KPI trends** catch degradation BEFORE it becomes an alarm storm
2. **Configuration drift detection** (see `src/config_drift.py` in this repo) catches silent misconfigurations
3. **Fleet reachability probing** (see `src/subnet_prober.py`) validates devices before they fail in production
4. **Post-change KPI verification** (see `examples/mop_template.md`) prevents change-induced storms

## 5. The operational metric that matters: MTTR

Mean Time To Restore = detection + diagnosis + action + verification. Everything in this document exists to compress it: correct severity → correct ownership → root-cause correlation → fix once.
