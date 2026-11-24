"""Regresiones para política de retiro local al crear pedidos."""


def create_customer(client, auth_cookie):
    response = client.post(
        "/api/v1/customers/",
        json={"name": "Cliente Retiro", "email": "apitest@example.com"},
        headers=auth_cookie,
    )
    assert response.status_code == 200, response.text
    return response.json()["id"]


def test_create_order_accepts_local_pickup(client, auth_cookie):
    customer_id = create_customer(client, auth_cookie)

    response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer_id,
            "total": 1500,
            "payment_method": "bank_transfer",
            "delivery_method": "retiro_local",
        },
        headers=auth_cookie,
    )

    assert response.status_code == 200, response.text
    assert response.json()["order"]["delivery_method"] == "retiro_local"


def test_create_order_rejects_shipping_method(client, auth_cookie):
    customer_id = create_customer(client, auth_cookie)

    response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer_id,
            "total": 1500,
            "payment_method": "bank_transfer",
            "delivery_method": "envio_andreani",
        },
        headers=auth_cookie,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "La única modalidad disponible es retiro en el local."


def test_create_order_rejects_missing_delivery_method(client, auth_cookie):
    customer_id = create_customer(client, auth_cookie)

    response = client.post(
        "/api/v1/orders/",
        json={
            "customer_id": customer_id,
            "total": 1500,
            "payment_method": "bank_transfer",
        },
        headers=auth_cookie,
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "La única modalidad disponible es retiro en el local."
