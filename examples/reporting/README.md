# Offline reporting example

The synthetic queue review cites a marker whose digest matches and a missing
alert export. The [generated report](bundle/report.md) retains the finding
and keeps assessment confidence unknown.

Agent requests include `$tarosec report ./cases`, `$tarosec-report technical ./cases`,
`$tarosec-report executive ./cases`, `$tarosec-report coverage ./exercises`,
`$tarosec-report compare ./baseline ./retest` with explicit baseline and retest
IDs, and `$tarosec-report validate ./reports/report.json`.

From the repository root, reproduce the bundle with these Python commands.

```bash
python3 -B skills/tarosec-report/scripts/generate_report.py examples/reporting/records --type technical --output ./queue-report
python3 -B skills/tarosec-report/scripts/validate_report.py ./queue-report/report.json --bundle --input examples/reporting/records
```
