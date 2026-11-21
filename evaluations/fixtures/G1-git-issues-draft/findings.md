Validated findings:
F-1: Admin access lacks authentication; High; TRUE POSITIVE; unauthenticated callers may reach administrative actions. A relevant working-tree diff adds authentication. Changes are uncommitted. No retest supplied.
F-2: Preview renders unsanitized content; Medium; TRUE POSITIVE; scripts may run in a viewer browser. A relevant working-tree diff adds sanitization. Changes are uncommitted. No retest supplied.
F-3: Hardcoded sample key; LIKELY FALSE POSITIVE; corroborated test-only fixture.
Review scope: partial static review, no runtime testing. Repository identity is not supplied. No public links are needed.
