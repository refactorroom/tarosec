# Offline Purple exercise and retest

The objective is to check whether an exercise marker in a synthetic process
feed appears in a supplied alert export within 30 seconds. The fixture is inert.

1. [Event marker](purple-marker.json) records a process-start marker on
   `synthetic-host`. [EV-MARKER](evidence.example.json) records its hash and timezone.
2. [Baseline exercise](exercise.example.json) records the event as observed.
   [EV-EXPORT-BASELINE](evidence.baseline.json) points to the supplied record that
   explicitly marks `RULE-MARKER` as not fired. The classifier returns **Detection gap**.
3. [Retest](exercise.retest.json) preserves expectation and step ID `S1`. The
   fixture describes updating the rule to recognize the marker event type.
   [EV-EXPORT-RETEST](evidence.retest.json) points to the record showing that
   `RULE-MARKER` fired on the expected host after 12 seconds. The classifier
   returns **Detected**.
4. [Case](case.example.json) connects the two exercises and their evidence IDs.

```bash
python3 -B skills/tarosec-purple/scripts/classify_exercise.py examples/exercise.example.json --json
python3 -B skills/tarosec-purple/scripts/classify_exercise.py examples/exercise.retest.json --json
python3 -B scripts/validate_record.py schemas/case.schema.json examples/case.example.json
```

Try the [mixed exercise fixture](../evaluations/fixtures/P1-purple-mixed/exercise.json)
for incomplete evidence. In S2 the expected
rule fired on a different host, so attribution is **Inconclusive**. S3 has a
failed execution and S4 has an unhealthy telemetry source. S5 has a correlated
alert after the budget. These fixtures test reporting logic using supplied
observations. Claims about deployed controls require actual telemetry and a
verified collection window.
