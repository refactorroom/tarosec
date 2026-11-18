"""Invoice service used by the billing API handlers."""
from dataclasses import dataclass


class NotFound(Exception):
    pass


class Forbidden(Exception):
    pass


@dataclass
class Invoice:
    id: int
    tenant_id: int
    owner_id: int
    amount_cents: int


@dataclass
class User:
    id: int
    tenant_id: int
    is_admin: bool = False


INVOICES = {
    1: Invoice(1, tenant_id=10, owner_id=100, amount_cents=12_000),
    2: Invoice(2, tenant_id=10, owner_id=101, amount_cents=5_500),
    3: Invoice(3, tenant_id=20, owner_id=200, amount_cents=99_000),
}


def _can_access(user: User, invoice: Invoice) -> bool:
    if invoice.tenant_id != user.tenant_id:
        return False
    return user.is_admin or invoice.owner_id == user.id


def list_invoices(user: User) -> list[Invoice]:
    return [inv for inv in INVOICES.values() if _can_access(user, inv)]


def get_invoice(user: User, invoice_id: int) -> Invoice:
    invoice = INVOICES.get(invoice_id)
    if invoice is None:
        raise NotFound(invoice_id)
    return invoice


def refund_invoice(user: User, invoice_id: int) -> Invoice:
    invoice = get_invoice(user, invoice_id)
    if not _can_access(user, invoice):
        raise Forbidden(invoice_id)
    invoice.amount_cents = 0
    return invoice
