#!/usr/bin/env python3
"""Run local Semgrep and collect inputs for the Tarosec review."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from init_workspace import ensure_ignored, safe_directory, write_manifest
from validate_record import load_json


MAX_EXTERNAL_REPORT_BYTES = 1024 * 1024
DEFAULT_SEMGREP = {
    "rulesets": [".tarosec/rules/semgrep.yml"],
    "exclude": [],
    "jobs": 2,
    "timeoutSeconds": 300,
}


def save_defaults(path):
    with tempfile.TemporaryDirectory(dir=path.parent) as staging:
        defaults = Path(staging) / path.name
        defaults.write_text(json.dumps({"version": 1, "semgrep": DEFAULT_SEMGREP}, indent=2) + "\n",
                            encoding="utf-8")
        try:
            os.link(defaults, path)
        except FileExistsError:
            pass


def scan_settings(path):
    if not path.exists() and not path.is_symlink():
        save_defaults(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError(".tarosec/tarosec.json must be a regular file")
    with path.open(encoding="utf-8") as stream:
        settings = load_json(stream)
    if (not isinstance(settings, dict) or set(settings) != {"version", "semgrep"}
            or type(settings["version"]) is not int or settings["version"] != 1):
        raise ValueError("tarosec.json requires version 1 and a semgrep settings object")
    options = settings["semgrep"]
    if not isinstance(options, dict) or options.keys() - DEFAULT_SEMGREP.keys():
        raise ValueError("tarosec.json contains unsupported Semgrep settings")
    options = {**DEFAULT_SEMGREP, **options}
    for key in ("rulesets", "exclude"):
        values = options[key]
        if not isinstance(values, list) or not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError(f"semgrep.{key} must be a list of non-empty strings")
    if not options["rulesets"]:
        raise ValueError("semgrep.rulesets must contain at least one ruleset")
    for key in ("jobs", "timeoutSeconds"):
        if type(options[key]) is not int or options[key] < 1:
            raise ValueError(f"semgrep.{key} must be a positive integer")
    return options


def semgrep_configs(project, rulesets, override):
    configs = []
    for ruleset in [override] if override is not None else rulesets:
        path = (project / ruleset if isinstance(ruleset, str) else ruleset).resolve()
        if not path.is_file():
            if isinstance(ruleset, str) and ruleset.startswith("p/"):
                return [], "registry-disabled"
            return [], "rules-unavailable"
        configs.append(str(path))
    return configs, None


def external_report(path):
    if path.suffix.lower() not in {".md", ".txt"} or not path.is_file():
        raise ValueError("the external report must be an existing Markdown or text file")
    with path.open("rb") as stream:
        content = stream.read(MAX_EXTERNAL_REPORT_BYTES + 1)
    if len(content) > MAX_EXTERNAL_REPORT_BYTES:
        raise ValueError("the external report exceeds 1 MiB")
    return content.decode("utf-8")


def summarize(run, exit_code, external, reason):
    status = "not_run" if reason in {"registry-disabled", "rules-unavailable", "scanner-unavailable"} else "failed"
    counts = []
    try:
        scan = json.loads((run / "semgrep.json").read_text(encoding="utf-8"))
        candidates = len(scan["results"])
        warnings = len(scan["errors"])
        scanned = len(scan["paths"]["scanned"])
        counts = [f"- Files scanned: {scanned}", f"- Candidate alerts: {candidates}",
                  f"- Scanner diagnostics: {warnings}"]
        if exit_code == 0 and (run / "semgrep.sarif").is_file():
            status = "completed" if scanned and not warnings else "partial"
    except (OSError, ValueError, KeyError, TypeError):
        pass
    lines = ["# Static scan evidence", "", f"- Semgrep: {status}", *counts]
    if reason:
        lines.append(f"- Scanner status detail: {reason}")
    if exit_code is not None:
        lines.append(f"- Semgrep exit code: {exit_code}")
    lines.append("- Existing Claude-BugHunter report: " + ("supplied" if external else "not supplied"))
    lines += ["", "Source and external claims require review. See `semgrep.log` for scanner diagnostics."]
    (run / "scan-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"status": status, **({"reason": reason} if reason else {})}


def record_evidence(run, filename, source):
    artifact = run / filename
    record = {"schemaVersion": "tarosec.evidence/v1", "id": f"{run.name}-{artifact.stem}",
              "source": source, "collectionMethod": "local scan-report run",
              "collectedAt": datetime.now(timezone.utc).isoformat(timespec="seconds"),
              "originalTimezone": "UTC", "artifactPath": filename,
              "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
              "sensitivity": "internal", "integrity": "hash-recorded"}
    (run / f"{artifact.stem}.evidence.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--bughunter-report", type=Path, help="existing sanitized Markdown or text report")
    parser.add_argument("--config", type=Path, help="trusted local Semgrep rule file")
    parser.add_argument("--update-gitignore", action="store_true", help="add /.tarosec/ to the project ignore file")
    args = parser.parse_args()
    try:
        project = args.project.resolve(strict=True)
        if not project.is_dir():
            raise ValueError("project must be an existing directory")
        report = external_report(args.bughunter_report) if args.bughunter_report else None
        workspace = safe_directory(project / ".tarosec")
        if args.update_gitignore:
            ensure_ignored(project, "/.tarosec/")
        settings = scan_settings(workspace / "tarosec.json")
        configs, reason = semgrep_configs(project, settings["rulesets"], args.config)
        if args.config:
            settings["rulesets"] = [str(args.config.resolve())]
        settings["exclude"] = list(dict.fromkeys([".tarosec", *settings["exclude"]]))
        settings["resolvedRulesets"] = configs
        reports = safe_directory(workspace / "reports")
        run = Path(tempfile.mkdtemp(prefix="run-", dir=reports))
        stages = {"workspace": {"status": "completed"}, "scan": {"status": "not_run"},
                  "audit": {"status": "not_run"}, "report": {"status": "not_run"}}
        write_manifest(run, "scan-report", stages)
        print(run, flush=True)
        (run / "scan-settings.json").write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")
        if report is not None:
            (run / "bughunter-report.md").write_text(report, encoding="utf-8")
            record_evidence(run, "bughunter-report.md", "Supplied external report")
        semgrep = shutil.which("semgrep")
        exit_code = None
        with (run / "semgrep.log").open("wb") as log:
            if reason:
                log.write(f"Semgrep did not run: {reason}.\n".encode())
                if reason == "registry-disabled":
                    log.write(b"Replace Registry pack entries with licensed local rule files or use --config PATH.\n")
            elif not semgrep:
                reason = "scanner-unavailable"
                log.write(b"Semgrep executable was not found on PATH.\n")
            else:
                command = [semgrep, "scan", "--oss-only", "--metrics=off", "--disable-version-check",
                           "--jobs", str(settings["jobs"]),
                           "--json-output", str(run / "semgrep.json"),
                           "--sarif-output", str(run / "semgrep.sarif")]
                for ruleset in configs:
                    command.extend(("--config", ruleset))
                for exclude in settings["exclude"]:
                    command.append(f"--exclude={exclude}")
                scanner_env = {**os.environ, "SEMGREP_LOG_FILE": str(run / "semgrep-internal.log"),
                               "SEMGREP_SETTINGS_FILE": str(run / "semgrep-user-settings.yml")}
                scanner_env.pop("SEMGREP_RULES", None)
                scanner_env.pop("SEMGREP_APP_TOKEN", None)
                # Sandboxed macOS processes can read the PEM bundle without keychain access.
                macos_ca_bundle = Path("/etc/ssl/cert.pem")
                if sys.platform == "darwin" and macos_ca_bundle.is_file():
                    scanner_env.setdefault("SSL_CERT_FILE", str(macos_ca_bundle))
                try:
                    result = subprocess.run([*command, "."], cwd=project, stdout=log, stderr=log,
                                            timeout=settings["timeoutSeconds"], env=scanner_env)
                    exit_code = result.returncode
                except subprocess.TimeoutExpired:
                    reason = "scanner-timeout"
                    log.write(f"\nSemgrep timed out after {settings['timeoutSeconds']} seconds.\n".encode())
                except OSError:
                    reason = "scanner-error"
                    log.write(b"\nSemgrep could not start.\n")
        stages["scan"] = summarize(run, exit_code, report is not None, reason)
        record_evidence(run, "scan-summary.md", "Semgrep scan summary")
        write_manifest(run, "scan-report", stages)
        return 0 if stages["scan"]["status"] in {"completed", "partial"} else 1
    except (OSError, ValueError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    sys.exit(main())
