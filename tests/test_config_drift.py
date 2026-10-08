"""Unit tests for the config drift detector (fixed samples, no network)."""

import os

import pytest

from src.config_drift import DEFAULT_FLAG_PATTERN, classify, detect_drift, read_config

BASELINE = [
    "hostname router-edge-01",
    "interface GigabitEthernet0/0",
    " ip address 10.0.0.1 255.255.255.0",
    " no shutdown",
    "snmp-server community public RO",
]

RUNNING = [
    "hostname router-edge-01",
    "interface GigabitEthernet0/0",
    " ip address 10.0.0.1 255.255.255.0",
    " shutdown",
    "snmp-server community s3cr3t RW",
    "ip route 0.0.0.0 0.0.0.0 10.0.0.254",
]


def test_classify_sensitive_lines():
    """Security-critical lines must be flagged by the default pattern."""
    assert classify("snmp-server community public RO", DEFAULT_FLAG_PATTERN)
    assert not classify("hostname router-edge-01", DEFAULT_FLAG_PATTERN)


def test_detect_drift_additions_and_removals():
    """Added and removed lines must be reported in order."""
    records = detect_drift(RUNNING, BASELINE, DEFAULT_FLAG_PATTERN)
    kinds = [r.kind for r in records]
    assert "removed" in kinds
    assert "added" in kinds
    added_lines = [r.line for r in records if r.kind == "added"]
    assert "ip route 0.0.0.0 0.0.0.0 10.0.0.254" in added_lines
    removed_lines = [r.line for r in records if r.kind == "removed"]
    assert " no shutdown" in removed_lines


def test_detect_drift_sensitive_flagging():
    """Drift on security-critical lines must be marked sensitive."""
    records = detect_drift(RUNNING, BASELINE, DEFAULT_FLAG_PATTERN)
    sensitive_lines = [r.line for r in records if r.sensitive]
    assert "snmp-server community s3cr3t RW" in sensitive_lines
    assert all(r.sensitive is False or "community" in r.line or "shutdown" not in r.line for r in records)


def test_detect_drift_no_drift():
    """Identical configs must produce zero findings."""
    assert detect_drift(BASELINE, BASELINE, DEFAULT_FLAG_PATTERN) == []


def test_read_config_strips_and_skips_empty(tmp_path):
    """Empty lines must be skipped and surrounding whitespace stripped."""
    file = tmp_path / "config.txt"
    file.write_text("\nline one  \n\nline two\n", encoding="utf-8")
    assert read_config(str(file)) == ["line one", "line two"]


def test_read_config_missing_file():
    """A missing file must raise OSError."""
    with pytest.raises(OSError):
        read_config(str(os.path.join("no", "such", "file.cfg")))
