"""Unit tests for deterministic synthetic ATP checks."""

import json

import pytest

from src.atp_runner import run_atp, write_report

SPEC = {
    "checks": [
        {"id": "CFG-001", "type": "config_contains", "line": "uplink enabled"},
        {
            "id": "SVC-001",
            "type": "service_state",
            "service": "transport",
            "expected": "ready",
        },
        {
            "id": "NET-001",
            "type": "connectivity",
            "endpoint": "core-sim",
            "expected": "reachable",
        },
    ]
}
FIXTURE = {
    "config": ["uplink enabled"],
    "services": {"transport": "ready"},
    "connectivity": {"core-sim": "reachable"},
}


def test_run_atp_passes_synthetic_fixture():
    assert [result.status for result in run_atp(SPEC, FIXTURE)] == ["PASS"] * 3


def test_run_atp_reports_failed_acceptance_check():
    fixture = {**FIXTURE, "services": {"transport": "degraded"}}
    results = run_atp(SPEC, fixture)
    assert [result.status for result in results] == ["PASS", "FAIL", "PASS"]


def test_run_atp_reports_timeout_without_sleeping():
    spec = {"checks": [{**SPEC["checks"][0], "duration_ms": 101, "timeout_ms": 100}]}
    result = run_atp(spec, FIXTURE)[0]
    assert result.status == "TIMEOUT"


def test_write_report_contains_summary(tmp_path):
    output = tmp_path / "atp.json"
    write_report(run_atp(SPEC, FIXTURE), str(output))
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert len(payload["checks"]) == 3


def test_unknown_check_type_is_rejected():
    with pytest.raises(ValueError, match="unsupported ATP check type"):
        run_atp({"checks": [{"id": "X", "type": "unknown"}]}, FIXTURE)


def test_empty_check_list_is_rejected():
    with pytest.raises(TypeError, match="checks list"):
        run_atp({"checks": []}, FIXTURE)
