# Acceptance Test Procedure (ATP) — Template

> Generic carrier-grade ATP template used for node integration and acceptance. Structure follows industry practice; all values are placeholders.

## 1. Scope

| Field | Value |
|---|---|
| ATP ID | ATP-YYYYMMDD-XXX |
| Node / Site | e.g. BBU-XXX, MGw-XXX |
| Type | Hardware / Functional / Software acceptance |
| Vendor | e.g. vendor-A, vendor-B |
| Baseline release | Rxx / Vxxx |

## 2. Test Environment

- Hardware inventory verified against BoQ (boards, units, cables, power)
- Software/firmware release verified
- Transport/IP connectivity verified (VLANs, routing, latency)

## 3. Hardware Acceptance Tests

| # | Test | Method | Pass criteria | Result |
|---:|---|---|---|---|
| 1 | Cabinet/_subrack inspection | Visual | No damage, correct slotting | ☐ |
| 2 | Power feed | Measurement | Voltage within tolerance | ☐ |
| 3 | Board insertion & state | MML/LMT query | All boards ONLINE | ☐ |
| 4 | Clock synchronization | Status query | Locked to reference | ☐ |
| 5 | Transmission links | Loopback/ethernet test | No errors, expected bandwidth | ☐ |

## 4. Functional Acceptance Tests

| # | Test | Method | Pass criteria | Result |
|---:|---|---|---|---|
| 1 | Cell setup & activation | MML/Tool | Cells ACTIVE | ☐ |
| 2 | Call setup (CS/ VoLTE) | Test call | Setup OK, audio OK | ☐ |
| 3 | Data session (PS) | Test session | Attach + PDP/session OK | ☐ |
| 4 | Handover / mobility | Drive or forced HO | HO success, no drops | ☐ |
| 5 | Alarm reporting | Forced alarm | Alarm raised & cleared in OSS | ☐ |
| 6 | KPI baseline | Counters query | Accessibility/retainability within tolerance | ☐ |

## 5. Acceptance Criteria

- All hardware tests PASS
- All functional tests PASS
- No open critical/major alarms
- KPI baseline recorded and accepted
- Documentation (results, screenshots, logs) attached to the ticket

## 6. Sign-off

| Role | Name | Date | Signature |
|---|---|---|---|
| Tester | | | |
| Vendor witness | | | |
| Operator acceptance | | | |
