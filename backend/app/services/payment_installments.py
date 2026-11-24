"""Cuotas máximas de un pedido: mínimo entre los productos que lo componen."""
from typing import Any, Iterable

from app.models.product import DEFAULT_MAX_INSTALLMENTS


def order_max_installments(products: Iterable[Any]) -> int:
    """Mínimo de max_installments entre productos (objetos o dicts). Default 3 si falta o no hay productos."""
    values = []
    for p in products:
        v = p.get("max_installments") if isinstance(p, dict) else getattr(p, "max_installments", None)
        values.append(v if v is not None else DEFAULT_MAX_INSTALLMENTS)
    return min(min(values, default=DEFAULT_MAX_INSTALLMENTS), 3)
