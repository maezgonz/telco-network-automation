"""Configuration drift detection against golden baselines (stdlib only)."""

from __future__ import annotations

import argparse
import csv
import difflib
import re
import sys
from dataclasses import dataclass

DEFAULT_FLAG_PATTERN = r"(?i)(password|secret|snmp|community|tacacs|radius|ssh-key)"


@dataclass(frozen=True)
class DriftRecord:
    """A single configuration drift finding."""

    kind: str
    line: str
    sensitive: bool


def read_config(path: str) -> list[str]:
    """Read a configuration file into stripped, non-empty lines.

    Args:
        path: Path to the config file.

    Returns:
        List of stripped lines.

    Raises:
        OSError: If the file cannot be read.
    """
    with open(path, "r", encoding="utf-8", errors="replace") as handle:
        return [line.rstrip() for line in handle if line.strip()]


def classify(line: str, flag_pattern: str) -> bool:
    """Return True when a config line matches a sensitive pattern.

    Args:
        line: Config line to inspect.
        flag_pattern: Regular expression marking sensitive lines.

    Returns:
        True when the line is security-sensitive.
    """
    return re.search(flag_pattern, line) is not None


def detect_drift(running: list[str], baseline: list[str], flag_pattern: str) -> list[DriftRecord]:
    """Diff a running config against its golden baseline.

    Args:
        running: Lines currently in the device.
        baseline: Golden baseline lines.
        flag_pattern: Regular expression marking sensitive lines.

    Returns:
        Drift records in baseline order: removals first, then additions.
    """
    matcher = difflib.SequenceMatcher(None, baseline, running, autojunk=False)
    records: list[DriftRecord] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "delete":
            records.extend(
                DriftRecord("removed", line, classify(line, flag_pattern))
                for line in baseline[i1:i2]
            )
        elif tag == "insert":
            records.extend(
                DriftRecord("added", line, classify(line, flag_pattern))
                for line in running[j1:j2]
            )
        elif tag == "replace":
            records.extend(
                DriftRecord("removed", line, classify(line, flag_pattern))
                for line in baseline[i1:i2]
            )
            records.extend(
                DriftRecord("added", line, classify(line, flag_pattern))
                for line in running[j1:j2]
            )
    return records


def write_csv(records: list[DriftRecord], output: str) -> None:
    """Write drift records to a CSV report.

    Args:
        records: Findings to persist.
        output: Destination CSV path.

    Raises:
        OSError: If the destination path cannot be written.
    """
    with open(output, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["kind", "sensitive", "line"])
        writer.writerows((r.kind, r.sensitive, r.line) for r in records)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Config drift detection against golden baseline")
    parser.add_argument("--running", required=True, help="Current device config file")
    parser.add_argument("--baseline", required=True, help="Golden baseline config file")
    parser.add_argument("--flag-pattern", default=DEFAULT_FLAG_PATTERN, help="Regex for sensitive lines")
    parser.add_argument("--output", default="drift_report.csv", help="Output CSV path")
    return parser.parse_args()


def main() -> int:
    """Entry point. Returns a process exit code."""
    args = parse_args()
    try:
        running = read_config(args.running)
        baseline = read_config(args.baseline)
        records = detect_drift(running, baseline, args.flag_pattern)
        write_csv(records, args.output)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    sensitive = sum(1 for r in records if r.sensitive)
    added = sum(1 for r in records if r.kind == "added")
    removed = len(records) - added
    print(
        f"drift={len(records)} added={added} removed={removed} "
        f"sensitive={sensitive} output={args.output}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
