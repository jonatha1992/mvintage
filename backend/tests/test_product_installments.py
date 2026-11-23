import pytest
from pydantic import ValidationError

from app.models.product import ProductCreate
from app.services.payment_installments import order_max_installments


def _create(**kw):
    return ProductCreate(name="x", price=10, images=[], **kw)


def test_default_is_3():
    assert _create().max_installments == 3


@pytest.mark.parametrize("n", [1, 3])
def test_allowed_values(n):
    assert _create(max_installments=n).max_installments == n


@pytest.mark.parametrize("n", [0, 2, 4, 6, 12, 24, -1])
def test_invalid_values(n):
    with pytest.raises(ValidationError, match="Las cuotas máximas deben ser 1 o 3"):
        _create(max_installments=n)


class P:
    def __init__(self, n=None):
        if n is not None:
            self.max_installments = n


def test_order_min():
    assert order_max_installments([P(12), P(6), P(3)]) == 3
    assert order_max_installments([P(12), P(6)]) == 3
    assert order_max_installments([P(1), P(12)]) == 1


def test_order_missing_defaults_to_3():
    assert order_max_installments([P(), P(12)]) == 3
    assert order_max_installments([{"max_installments": None}]) == 3
    assert order_max_installments([]) == 3
    assert order_max_installments([{"max_installments": 6}, {"max_installments": 12}]) == 3
