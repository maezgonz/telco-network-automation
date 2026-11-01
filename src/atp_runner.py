"""Run deterministic acceptance checks against synthetic fixtures."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CheckResult:
    """Result for one ATP acceptance check."""

    check_id: str
    check_type: str
    status: str
    detail: str


def load_json(path: str) -> dict[str, Any]:
    """Load a JSON object from a fixture or ATP specification."""
    with open(path, encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain a JSON object")
    return payload


def run_check(check: dict[str, Any], fixture: dict[str, Any]) -> CheckResult:
    """Evaluate one local, deterministic ATP check."""
    check_id = str(check["id"])
    check_type = str(check["type"])
    timeout_ms = int(check.get("timeout_ms", 1000))
    duration_ms = int(check.get("duration_ms", 0))

    if duration_ms > timeout_ms:
        return CheckResult(check_id, check_type, "TIMEOUT", f"{duration_ms}ms > {timeout_ms}ms")

    if check_type == "config_contains":
        expected = str(check["line"])
        config = fixture.get("config", [])
        passed = expected in config
        detail = "expected line present" if passed else "expected line missing"
    elif check_type == "service_state":
        service = str(check["service"])
        expected = str(check["expected"])
        actual = fixture.get("services", {}).get(service)
        passed = actual == expected
        detail = f"{service}={actual!r}, expected={expected!r}"
    elif check_type == "connectivity":
        endpoint = str(check["endpoint"])
        expected = str(check.get("expected", "reachable"))
        actual = fixture.get("connectivity", {}).get(endpoint)
        passed = actual == expected
        detail = f"{endpoint}={actual!r}, expected={expected!r}"
    else:
        raise ValueError(f"unsupported ATP check type: {check_type}")

    return CheckResult(check_id, check_type, "PASS" if passed else "FAIL", detail)


def run_atp(spec: dict[str, Any], fixture: dict[str, Any]) -> list[CheckResult]:
    """Run all checks in an ATP specification."""
    checks = spec.get("checks")
    if not isinstance(checks, list) or not checks:
        raise TypeError("ATP specification must contain a checks list")
    if any(not isinstance(check, dict) for check in checks):
        raise TypeError("each ATP check must be a JSON object")
    return [run_check(check, fixture) for check in checks]


def write_report(results: list[CheckResult], output: str) -> None:
    """Write a JSON ATP report."""
    payload = {
        "status": "PASS" if all(result.status == "PASS" for result in results) else "FAIL",
        "checks": [asdict(result) for result in results],
    }
    Path(output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Run synthetic ATP acceptance checks")
    parser.add_argument("--spec", required=True, help="ATP specification JSON")
    parser.add_argument("--fixture", required=True, help="Synthetic environment fixture JSON")
    parser.add_argument("--output", default="atp_report.json", help="JSON report path")
    return parser.parse_args()


def main() -> int:
    """Run the ATP and return a gating exit code."""
    args = parse_args()
    try:
        results = run_atp(load_json(args.spec), load_json(args.fixture))
        write_report(results, args.output)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    failed = sum(result.status != "PASS" for result in results)
    print(f"checks={len(results)} failed={failed} status={'PASS' if not failed else 'FAIL'}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
