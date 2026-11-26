def get_invoice(connection, authenticated_tenant, invoice_id):
    with connection.transaction(), connection.cursor() as cursor:
        cursor.execute("SELECT set_config('app.tenant_id', %s, true)", (authenticated_tenant,))
        cursor.execute("SELECT id, total FROM invoices WHERE id = %s", (invoice_id,))
        return cursor.fetchone()
