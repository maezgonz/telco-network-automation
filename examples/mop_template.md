# Method of Procedure (MOP) — Template

> Generic carrier-grade MOP template distilled from 10+ years of network operations in mobile networks (2G/3G/4G/5G). Structure follows industry practice; all values are placeholders.

## 1. Document Control

| Field | Value |
|---|---|
| Procedure ID | MOP-YYYYMMDD-XXX |
| Title | e.g. BBU upgrade to release Rxx |
| Network domain | RAN / Core / Transport |
| Vendor | e.g. vendor-A, vendor-B |
| Impact window | Maintenance window (low traffic) |
| Risk level | Low / Medium / High |

## 2. Preconditions

- [ ] Change ticket approved and scheduled
- [ ] Current software/firmware level recorded
- [ ] Latest configuration backup taken and verified restorable
- [ ] Alarm list clean (no pending critical alarms unrelated to the change)
- [ ] Rollback plan validated and time-boxed
- [ ] Stakeholders notified (NOC, RF, core, customer care if subscriber-visible)

## 3. Procedure Steps

| Step | Command / Action | Expected result | Done |
|---:|---|---|---|
| 1 | Record current state (`mml: LST ...` / equivalent) | Output archived to ticket | ☐ |
| 2 | Put site/node in maintenance mode | Alarms suppressed, traffic drained | ☐ |
| 3 | Apply change (upgrade / reconfiguration) | New release active, no failed steps | ☐ |
| 4 | Post-change validation (state + KPIs) | All validation checks pass | ☐ |
| 5 | Restore normal operation | Alarms re-enabled, traffic restored | ☐ |

## 4. Post-change Validation

- Node state: all boards/units operational
- Alarms: no new critical/major alarms
- KPIs: accessibility, retainability and mobility within tolerance vs. baseline (compare 24h before vs. 2h after)
- Subscriber-impacting checks: call setups, session continuity, data sessions

## 5. Rollback Plan

| Trigger | Action | Time box |
|---|---|---|
| Validation fails | Roll back to previous release from backup | e.g. 60 min |
| KPI degradation beyond tolerance | Roll back and escalate to vendor | e.g. 2 h |

## 6. Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| Implementer | | | |
| Reviewer (NOC) | | | |
| Approver | | | |
