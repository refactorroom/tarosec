# Invoice tenant isolation

Every invoice lookup must enforce caller membership for the invoice's tenant.
This source snapshot omits deployment database policies and role grants. The
deployment is intended to enforce tenant isolation in its database policy.
