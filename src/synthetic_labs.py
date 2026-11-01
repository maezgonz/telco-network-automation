"""Deterministic deployment, resilience, stress and alarm lab scenarios."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LabResult:
    """Result for one synthetic lab scenario."""

    lab: str
    status: str
    detail: str


def run_prechecks(fixture: dict[str, Any]) -> LabResult:
    """Validate deployment prerequisites from a local fixture."""
    required = ("backup_verified", "maintenance_window", "dependencies_ready")
    missing = [key for key in required if fixture.get(key) is not True]
    if missing:
        return LabResult("deployment_prechecks", "FAIL", f"missing prerequisites: {', '.join(missing)}")
    return LabResult("deployment_prechecks", "PASS", "all deployment prerequisites verified")


def run_rollback(fixture: dict[str, Any]) -> LabResult:
    """Validate that a simulated rollback restores the declared baseline."""
    if fixture.get("change_applied") is not True:
        return LabResult("rollback_validation", "FAIL", "change was not applied")
    if fixture.get("restored_state") != fixture.get("baseline_state"):
        return LabResult("rollback_validation", "FAIL", "restored state differs from baseline")
    return LabResult("rollback_validation", "PASS", "baseline state restored")


def run_failover(fixture: dict[str, Any]) -> LabResult:
    """Validate service continuity across a simulated active-node failure."""
    if fixture.get("standby_ready") is not True:
        return LabResult("failover_simulation", "FAIL", "standby node is not ready")
    if fixture.get("service_after_failover") != "available":
        return LabResult("failover_simulation", "FAIL", "service unavailable after failover")
    return LabResult("failover_simulation", "PASS", "standby assumed service without outage")


def run_stress(fixture: dict[str, Any]) -> LabResult:
    """Validate a bounded synthetic load run without opening sockets."""
    offered = int(fixture.get("offered_load", 0))
    capacity = int(fixture.get("capacity", 0))
    error_rate = float(fixture.get("error_rate", 1.0))
    limit = float(fixture.get("max_error_rate", 0.05))
    if offered <= 0 or capacity <= 0:
        return LabResult("controlled_stress", "FAIL", "load and capacity must be positive")
    if offered > capacity or error_rate > limit:
        return LabResult("controlled_stress", "FAIL", "synthetic load exceeded acceptance limits")
    return LabResult("controlled_stress", "PASS", "load remained within synthetic acceptance limits")


def run_alarm_correlation(fixture: dict[str, Any]) -> LabResult:
    """Validate that related fixture alarms resolve to the declared root cause."""
    alarms = fixture.get("alarms", [])
    root_cause = fixture.get("root_cause")
    if not isinstance(alarms, list) or any(not isinstance(alarm, dict) for alarm in alarms):
        return LabResult("alarm_correlation", "FAIL", "alarms must be a list of JSON objects")
    related = [alarm for alarm in alarms if alarm.get("cause") == root_cause]
    if not alarms or not root_cause or len(related) != len(alarms):
        return LabResult("alarm_correlation", "FAIL", "alarm set is not explained by one root cause")
    return LabResult("alarm_correlation", "PASS", f"{len(alarms)} alarms correlated to {root_cause}")


RUNNERS = {
    "deployment_prechecks": run_prechecks,
    "rollback_validation": run_rollback,
    "failover_simulation": run_failover,
    "controlled_stress": run_stress,
    "alarm_correlation": run_alarm_correlation,
}


def run_labs(fixtures: dict[str, Any]) -> list[LabResult]:
    """Run all synthetic labs from their named fixture sections."""
    return [runner(fixtures.get(name, {})) for name, runner in RUNNERS.items()]


def write_report(results: list[LabResult], output: str) -> None:
    """Write a synthetic lab report."""
    payload = {
        "status": "PASS" if all(result.status == "PASS" for result in results) else "FAIL",
        "labs": [asdict(result) for result in results],
    }
    Path(output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run deterministic synthetic telco labs")
    parser.add_argument("--fixtures", required=True, help="Synthetic lab fixture JSON")
    parser.add_argument("--output", default="lab_report.json", help="JSON report path")
    return parser.parse_args()


def main() -> int:
    """Run all labs and return a gating exit code."""
    args = parse_args()
    try:
        with open(args.fixtures, encoding="utf-8") as handle:
            fixtures = json.load(handle)
        if not isinstance(fixtures, dict):
            raise TypeError("fixtures must contain a JSON object")
        results = run_labs(fixtures)
        write_report(results, args.output)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    failed = sum(result.status != "PASS" for result in results)
    print(f"labs={len(results)} failed={failed} status={'PASS' if not failed else 'FAIL'}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
