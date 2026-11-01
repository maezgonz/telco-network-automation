"""Unit tests for deterministic synthetic telco labs."""

import json

import pytest

from src.synthetic_labs import (
    run_alarm_correlation,
    run_failover,
    run_labs,
    run_prechecks,
    run_rollback,
    run_stress,
    write_report,
)

FIXTURES = {
    "deployment_prechecks": {
        "backup_verified": True,
        "maintenance_window": True,
        "dependencies_ready": True,
    },
    "rollback_validation": {
        "change_applied": True,
        "baseline_state": "v1",
        "restored_state": "v1",
    },
    "failover_simulation": {"standby_ready": True, "service_after_failover": "available"},
    "controlled_stress": {
        "offered_load": 80,
        "capacity": 100,
        "error_rate": 0.02,
        "max_error_rate": 0.05,
    },
    "alarm_correlation": {
        "root_cause": "link-01",
        "alarms": [{"id": "A-1", "cause": "link-01"}],
    },
}


def test_all_synthetic_labs_pass():
    assert [result.status for result in run_labs(FIXTURES)] == ["PASS"] * 5


@pytest.mark.parametrize(
    ("runner", "fixture"),
    [
        (run_prechecks, {"backup_verified": True}),
        (run_rollback, {"change_applied": True, "baseline_state": "v1", "restored_state": "v2"}),
        (run_failover, {"standby_ready": False}),
        (run_stress, {"offered_load": 110, "capacity": 100, "error_rate": 0}),
        (run_alarm_correlation, {"root_cause": "link-01", "alarms": []}),
    ],
)
def test_each_lab_reports_failure(runner, fixture):
    assert runner(fixture).status == "FAIL"


def test_write_report_contains_all_labs(tmp_path):
    output = tmp_path / "labs.json"
    write_report(run_labs(FIXTURES), str(output))
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    assert len(payload["labs"]) == 5


def test_alarm_correlation_rejects_malformed_alarm_fixture():
    result = run_alarm_correlation({"root_cause": "link-01", "alarms": ["malformed"]})
    assert result.status == "FAIL"
    assert "JSON objects" in result.detail
