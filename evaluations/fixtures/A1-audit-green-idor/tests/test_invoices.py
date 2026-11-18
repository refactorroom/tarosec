import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
import invoices as inv  # noqa: E402


class InvoiceTests(unittest.TestCase):
    def test_owner_can_get_own_invoice(self):
        user = inv.User(id=100, tenant_id=10)
        self.assertEqual(inv.get_invoice(user, 1).amount_cents, 12_000)

    def test_missing_invoice(self):
        with self.assertRaises(inv.NotFound):
            inv.get_invoice(inv.User(id=100, tenant_id=10), 999)

    def test_list_is_scoped_to_owner(self):
        user = inv.User(id=100, tenant_id=10)
        self.assertEqual([i.id for i in inv.list_invoices(user)], [1])

    def test_refund_other_tenant_forbidden(self):
        with self.assertRaises((inv.Forbidden, inv.NotFound)):
            inv.refund_invoice(inv.User(id=100, tenant_id=10), 3)


if __name__ == "__main__":
    unittest.main()
