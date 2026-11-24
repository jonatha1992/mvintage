import pytest
from fastapi import HTTPException
from app.controllers.cash_controller import cash_controller
from app.models.order import Order
from app.models.customer import Customer


@pytest.mark.parametrize('method', ['cash', 'transfer', 'other', 'credit_card', ''])
def test_rejects_unsupported_new_payments(client, auth_cookie, db_session, method):
    customer = Customer(name='Cliente', email='apitest@example.com')
    db_session.add(customer)
    db_session.commit()
    response = client.post('/api/v1/orders/', headers=auth_cookie, json={
        'customer_id': customer.id, 'total': 1500,
        'payment_method': method, 'delivery_method': 'retiro_local',
    })
    assert response.status_code == 400
    expected = 'Pago en el local no disponible' if method == 'cash' else 'Método de pago no disponible'
    assert response.json()['detail'] == expected
    assert db_session.query(Order).count() == 0


def test_cash_controller_is_disabled(db_session):
    with pytest.raises(HTTPException) as exc:
        cash_controller.create_cash_order(123, db_session)
    assert exc.value.status_code == 410
    assert exc.value.detail == 'Pago en el local no disponible'


def test_historical_cash_orders_remain_readable(client, auth_cookie, db_session):
    customer = Customer(name='Histórico', email='apitest@example.com')
    db_session.add(customer)
    db_session.commit()
    order = Order(customer_id=customer.id, total=500, payment_method='cash')
    db_session.add(order)
    db_session.commit()
    response = client.get(f'/api/v1/orders/{order.id}', headers=auth_cookie)
    assert response.status_code == 200
    assert response.json()['payment_method'] == 'cash'
