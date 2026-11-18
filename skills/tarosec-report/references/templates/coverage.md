# Detection coverage report

- Exercise IDs, environment, and ATT&CK version as supplied
- Step IDs, expected and observed control behavior, evidence IDs, and outcomes
- Telemetry, attribution, collection and latency limitations
- Detection totals with an explicit eligible denominator and excluded outcomes

Preserve Detected, Detected (late), Partially detected, Prevented, Detection
gap, Telemetry gap, Inconclusive and Not run. The CLI metric counts full
detections including late detections among hash-matched full detections,
partial detections and detection gaps. It excludes prevented, unrun,
inconclusive, telemetry-gap and simulation-linked steps. State that a zero
denominator leaves the rate unavailable. Qualify rates to the supplied
collection windows and evidence.
