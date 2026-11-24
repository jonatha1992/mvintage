import json

import httpx
import pytest

from app.services.payalert_client import PayAlertClient, PayAlertError
from app.controllers.payments_controller import PaymentsController
from app.models.customer import Customer
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product, ProductVariant


def charge(client):
    return client.create_charge(12, 25000, 'cliente', 'https://shop.test/return',
                                title='Pedido #12 - Showroom Isabella',
                                description='Campera (M, Negro) x2', exclude_cash=True)


def test_charge_payload_has_order_details():
    bodies = []

    def handle(request):
        bodies.append(json.loads(request.content))
        return httpx.Response(200, json={'chargeId': 'charge-12'})

    with httpx.Client(transport=httpx.MockTransport(handle)) as http:
        client = PayAlertClient(base_url='https://pay.test', api_key='test-key', http_client=http)
        assert charge(client)['chargeId'] == 'charge-12'
    assert len(bodies) == 1
    assert bodies[0]['title'] == 'Pedido #12 - Showroom Isabella'
    assert bodies[0]['description'] == 'Campera (M, Negro) x2'
    assert bodies[0]['excludeCash'] is True


@pytest.mark.parametrize('status,code,retries', [(400, 'invalid_request', 2), (400, 'invalid_amount', 1), (500, 'invalid_request', 1)])
def test_charge_fallback_only_once_for_old_contract(status, code, retries):
    bodies = []

    def handle(request):
        bodies.append(json.loads(request.content))
        return httpx.Response(status, json={'error': code})

    with httpx.Client(transport=httpx.MockTransport(handle)) as http:
        client = PayAlertClient(base_url='https://pay.test', api_key='test-key', http_client=http)
        with pytest.raises(PayAlertError):
            charge(client)
    assert len(bodies) == retries
    if retries == 2:
        assert not {'title', 'description', 'excludeCash'} & bodies[1].keys()
        assert bodies[1] == {k: v for k, v in bodies[0].items() if k not in ('title', 'description', 'excludeCash')}


def test_charge_fallback_can_succeed():
    bodies = []

    def handle(request):
        bodies.append(json.loads(request.content))
        return httpx.Response(400, json={'error': 'invalid_request'}) if len(bodies) == 1 else httpx.Response(200, json={'chargeId': 'legacy'})

    with httpx.Client(transport=httpx.MockTransport(handle)) as http:
        client = PayAlertClient(base_url='https://pay.test', api_key='test-key', http_client=http)
        assert charge(client)['chargeId'] == 'legacy'
    assert len(bodies) == 2


@pytest.mark.parametrize('long_name', [False, True])
def test_preference_builds_description_for_unique_and_variant(db_session, long_name):
    customer = Customer(name='Cliente', email='cliente@example.com')
    product = Product(name='Campera' if not long_name else 'C' * 300, price=100, is_unique=True, color='Beige', talle='L', stock=5)
    variant_product = Product(name='Blusa', price=100, is_unique=False)
    db_session.add_all([customer, product, variant_product])
    db_session.commit()
    variant = ProductVariant(product_id=variant_product.id, color='Negro', talle='M', stock=3)
    order = Order(customer_id=customer.id, total=300, payment_method='mercadopago')
    db_session.add_all([variant, order])
    db_session.commit()
    db_session.add_all([
        OrderItem(order_id=order.id, product_id=product.id, quantity=2, price=100),
        OrderItem(order_id=order.id, product_id=variant_product.id, variant_id=variant.id, quantity=1, price=100),
    ])
    db_session.commit()
    class Client:
        is_configured = True
        payload = None

        def create_charge(self, **kwargs):
            self.payload = kwargs
            return {'chargeId': 'test', 'checkoutUrl': 'https://pay.test/checkout'}

    client = Client()
    PaymentsController(client).create_preference(order.id, db_session)
    assert client.payload['title'] == f'Pedido #{order.id} - Showroom Isabella'
    expected = f'{product.name} (L, Beige) x2, Blusa (M, Negro) x1'
    assert client.payload['description'] == expected[:255]
    assert client.payload['exclude_cash'] is True
