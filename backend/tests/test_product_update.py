from app.main import app
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import ProductVariant
from sqlmodel import select


def _create_jean_product(client, auth_cookie):
    payload = {
        "name": "Jean Azul Denim",
        "description": "Jean clásico tiro alto",
        "price": 45000.0,
        "genero": "femenino",
        "estado": "nuevo",
        "categoria": "Jeans",
        "is_unique": False,
        "color": None,
        "talle": None,
        "stock": None,
        "images": ["https://img.tecnofusion.dev/productos/jean1.webp"],
        "variants": [
            {"color": "AZUL DENIM", "talle": "38", "stock": 1},
            {"color": "AZUL DENIM", "talle": "40", "stock": 1},
            {"color": "AZUL DENIM", "talle": "42", "stock": 1},
            {"color": "AZUL DENIM", "talle": "44", "stock": 1},
        ],
        "has_discount": False,
        "max_installments": 3,
    }
    response = client.post("/api/v1/products/", json=payload, headers=auth_cookie)
    assert response.status_code == 200, response.text
    return response.json()


def _admin_form_payload(product_json, *, include_ids=True, **overrides):
    variants = []
    for v in product_json["variants"]:
        item = {"color": v["color"], "talle": v["talle"], "stock": v["stock"]}
        if include_ids:
            item["id"] = v["id"]
        variants.append(item)
    payload = {
        "name": product_json["name"],
        "description": product_json["description"],
        "price": product_json["price"],
        "genero": product_json["genero"],
        "estado": product_json["estado"],
        "categoria": product_json["categoria"],
        "is_unique": product_json["is_unique"],
        "color": product_json["color"],
        "talle": product_json["talle"],
        "stock": product_json["stock"],
        "images": [img["image_url"] for img in product_json["images"]],
        "variants": variants,
        "has_discount": product_json["has_discount"],
        "max_installments": product_json["max_installments"],
    }
    payload.update(overrides)
    return payload


def test_update_name_and_price_preserves_variant_ids(client, auth_cookie):
    created = _create_jean_product(client, auth_cookie)
    original_ids = [v["id"] for v in created["variants"]]

    payload = _admin_form_payload(created, name="Jean Azul Denim Editado", price=49000.0)
    response = client.put(f"/api/v1/products/{created['id']}", json=payload, headers=auth_cookie)
    assert response.status_code == 200, response.text

    updated = response.json()
    assert updated["name"] == "Jean Azul Denim Editado"
    assert updated["price"] == 49000.0
    assert [v["id"] for v in updated["variants"]] == original_ids


def test_update_admin_payload_without_variant_ids_preserves_existing_ids(client, auth_cookie):
    created = _create_jean_product(client, auth_cookie)
    original_by_size = {v["talle"]: v["id"] for v in created["variants"]}

    payload = _admin_form_payload(created, include_ids=False, name="Jean Sin IDs")
    response = client.put(f"/api/v1/products/{created['id']}", json=payload, headers=auth_cookie)
    assert response.status_code == 200, response.text

    updated = response.json()
    assert updated["name"] == "Jean Sin IDs"
    assert {v["talle"]: v["id"] for v in updated["variants"]} == original_by_size


def test_update_variant_stock_preserves_ids(client, auth_cookie):
    created = _create_jean_product(client, auth_cookie)
    original_ids = [v["id"] for v in created["variants"]]

    payload = _admin_form_payload(created)
    payload["variants"][1]["stock"] = 7
    response = client.put(f"/api/v1/products/{created['id']}", json=payload, headers=auth_cookie)
    assert response.status_code == 200, response.text

    updated = response.json()
    assert [v["id"] for v in updated["variants"]] == original_ids
    talle_40 = next(v for v in updated["variants"] if v["talle"] == "40")
    assert talle_40["stock"] == 7


def test_add_new_size_preserves_existing_variants(client, auth_cookie):
    created = _create_jean_product(client, auth_cookie)
    original_ids = {v["id"] for v in created["variants"]}

    payload = _admin_form_payload(created)
    payload["variants"].append({"color": "AZUL DENIM", "talle": "46", "stock": 2})
    response = client.put(f"/api/v1/products/{created['id']}", json=payload, headers=auth_cookie)
    assert response.status_code == 200, response.text

    updated = response.json()
    assert len(updated["variants"]) == 5
    updated_ids = {v["id"] for v in updated["variants"]}
    assert original_ids.issubset(updated_ids)
    talle_46 = next(v for v in updated["variants"] if v["talle"] == "46")
    assert talle_46["stock"] == 2


def test_remove_size_without_orders_deletes_only_removed_variant(client, auth_cookie, db_session):
    created = _create_jean_product(client, auth_cookie)
    removed_id = created["variants"][-1]["id"]
    kept_ids = [v["id"] for v in created["variants"][:-1]]

    payload = _admin_form_payload(created)
    payload["variants"] = payload["variants"][:-1]
    response = client.put(f"/api/v1/products/{created['id']}", json=payload, headers=auth_cookie)
    assert response.status_code == 200, response.text

    updated = response.json()
    assert [v["id"] for v in updated["variants"]] == kept_ids
    assert db_session.get(ProductVariant, removed_id) is None


def test_remove_size_with_orders_returns_409_and_keeps_data_intact(client, auth_cookie, db_session):
    created = _create_jean_product(client, auth_cookie)
    used_variant = created["variants"][0]

    customer = Customer(name="Clienta Test", email="clienta@example.com")
    db_session.add(customer)
    db_session.flush()
    order = Order(customer_id=customer.id, status="paid", total=45000.0)
    db_session.add(order)
    db_session.flush()
    db_session.add(
        OrderItem(
            order_id=order.id,
            product_id=created["id"],
            variant_id=used_variant["id"],
            quantity=1,
            price=45000.0,
        )
    )
    db_session.commit()

    payload = _admin_form_payload(created, name="No Debe Guardarse")
    payload["variants"] = [v for v in payload["variants"] if v["id"] != used_variant["id"]]
    response = client.put(f"/api/v1/products/{created['id']}", json=payload, headers=auth_cookie)
    assert response.status_code == 409
    assert "pedidos asociados" in response.json()["detail"].lower()

    remaining = db_session.exec(
        select(ProductVariant).where(ProductVariant.product_id == created["id"])
    ).all()
    assert len(remaining) == 4
    get_resp = client.get(f"/api/v1/products/{created['id']}")
    assert get_resp.json()["name"] == "Jean Azul Denim"


def test_unhandled_500_includes_cors_headers(client):
    @app.get("/api/v1/_test_boom_500")
    def _boom():
        raise RuntimeError("boom")

    try:
        origin = "http://localhost:5173"
        response = client.get("/api/v1/_test_boom_500", headers={"Origin": origin})
        assert response.status_code == 500
        assert response.json() == {"detail": "Error interno del servidor"}
        assert response.headers.get("access-control-allow-origin") == origin
        assert response.headers.get("access-control-allow-credentials") == "true"
    finally:
        app.router.routes[:] = [
            r for r in app.router.routes if getattr(r, "path", None) != "/api/v1/_test_boom_500"
        ]
