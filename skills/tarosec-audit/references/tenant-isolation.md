# Tenant isolation

State the invariant for each in-scope operation. An identity authorized for
tenant A may only read, change, or receive results for tenant A unless a
reviewed cross-tenant policy explicitly allows it.

| Boundary | Evidence to inspect |
| --- | --- |
| Go handlers and workers | Where membership and tenant identity are resolved, how they reach storage calls, and what workers recheck when jobs are resumed or retried. |
| PostgreSQL | Tenant predicates on reads, writes, joins and exports. If enforcement relies on row-level security, inspect the policy, effective database role, and transaction-scoped tenant context. |
| Object storage and derived data | Ownership checks for object references and exports, tenant scoping in storage keys and signed access, and controls for writes to caches and derived artifacts. |
| Retrieval and output | Tenant filters on indexing and retrieval, ownership of cached results, and handling of retrieved chunks and citations in the final response. |

Follow one operation end to end and record the deciding guard at each boundary.
Look for a positive control, a known policy violation, and a case where a
missing policy must leave the claim inconclusive. Review supplied test results
or use inert input fixtures for defensive regression testing.
