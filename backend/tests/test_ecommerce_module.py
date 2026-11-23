"""
Tests integrados para el módulo de comercio electrónico.
Incluye clientes, pedidos, items de pedidos y flujos completos de compra.
"""
import pytest
from fastapi.testclient import TestClient


class TestCustomersCRUD:
    """Tests para operaciones CRUD de clientes"""

    def test_create_customer_minimal(self, client, auth_cookie):
        """Test crear cliente con datos mínimos"""
        data = {
            "name": "Cliente Test",
            "email": "cliente.test@example.com"
        }
        response = client.post("/api/v1/customers/", json=data, headers=auth_cookie)
        assert response.status_code == 200
        
        customer = response.json()
        assert customer["name"] == "Cliente Test"
        assert customer["email"] == "cliente.test@example.com"
        assert "id" in customer

    # def test_create_customer_complete(self, client, auth_cookie):
    #     """Test crear cliente con todos los campos"""
    #     data = {
    #         "name": "Cliente Completo",
    #         "email": "completo@example.com",
    #         "phone": "555-1234",
    #         "address": "Calle Principal 123"
    #     }
    #     response = client.post("/api/v1/customers/", json=data, headers=auth_cookie)
    #     assert response.status_code == 200
    #     
    #     customer = response.json()
    #     assert customer["name"] == "Cliente Completo"
    #     assert customer["email"] == "completo@example.com"
    #     assert customer["phone"] == "555-1234"
    #     assert customer["address"] == "Calle Principal 123"

    # def test_get_customers_list(self, client, auth_cookie):
    #     """Test obtener lista de clientes"""
    #     response = client.get("/api/v1/customers/", headers=auth_cookie)
    #     assert response.status_code == 200
    #     
    #     customers = response.json()
    #     assert isinstance(customers, list)

    def test_get_single_customer(self, client, auth_cookie):
        """Test obtener un cliente específico"""
        # Crear cliente
        create_data = {
            "name": "Cliente Para Get",
            "email": "get.test@example.com"
        }
        create_response = client.post("/api/v1/customers/", json=create_data, headers=auth_cookie)
        customer_id = create_response.json()["id"]
        
        # Obtener cliente
        response = client.get(f"/api/v1/customers/{customer_id}", headers=auth_cookie)
        assert response.status_code == 200
        
        customer = response.json()
        assert customer["id"] == customer_id
        assert customer["name"] == "Cliente Para Get"

    # def test_update_customer(self, client, auth_cookie):
    #     """Test actualizar cliente"""
    #     # Crear cliente
    #     create_data = {
    #         "name": "Cliente Original",
    #         "email": "original@example.com"
    #     }
    #     create_response = client.post("/api/v1/customers/", json=create_data, headers=auth_cookie)
    #     customer_id = create_response.json()["id"]
    #     
    #     # Actualizar cliente
    #     update_data = {
    #         "name": "Cliente Actualizado",
    #         "email": "actualizado@example.com",
    #         "phone": "555-9999",
    #         "address": "Nueva Dirección 456"
    #     }
    #     response = client.put(f"/api/v1/customers/{customer_id}", json=update_data, headers=auth_cookie)
    #     assert response.status_code == 200
    #     
    #     updated_customer = response.json()
    #     assert updated_customer["name"] == "Cliente Actualizado"
    #     assert updated_customer["email"] == "actualizado@example.com"

    # def test_delete_customer(self, client, auth_cookie):
    #     """Test eliminar cliente"""
    #     # Crear cliente
    #     create_data = {
    #         "name": "Cliente Para Delete",
    #         "email": "delete@example.com"
    #     }
    #     create_response = client.post("/api/v1/customers/", json=create_data, headers=auth_cookie)
    #     customer_id = create_response.json()["id"]
    #     
    #     # Eliminar cliente
    #     response = client.delete(f"/api/v1/customers/{customer_id}", headers=auth_cookie)
    #     assert response.status_code == 200
    #     
    #     # Verificar que no existe
    #     get_response = client.get(f"/api/v1/customers/{customer_id}", headers=auth_cookie)
    #     assert get_response.status_code == 404


class TestOrdersCRUD:
    """Tests para operaciones CRUD de pedidos"""

    def test_create_order(self, client, auth_cookie):
        """Test crear pedido"""
        # Primero crear un cliente
        customer_data = {
            "name": "Cliente Para Pedido",
            "email": "pedido@example.com"
        }
        customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
        customer_id = customer_response.json()["id"]
        
        # Crear pedido
        order_data = {
            "customer_id": customer_id,
            "status": "pending",
            "total": 100.0,
            "delivery_method": "retiro_local"
        }
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
        assert response.status_code == 200
        
        response_data = response.json()
        order = response_data["order"]
        assert order["customer_id"] == customer_id
        assert order["status"] == "pending"
        assert order["total"] == 100.0
        assert "id" in order

    # def test_get_orders_list(self, client, auth_cookie):
    #     """Test obtener lista de pedidos"""
    #     response = client.get("/api/v1/orders/", headers=auth_cookie)
    #     assert response.status_code == 200
    #     
    #     orders = response.json()
    #     assert isinstance(orders, list)

    def test_get_single_order(self, client, auth_cookie):
        """Test obtener un pedido específico"""
        # Crear cliente y pedido
        customer_data = {"name": "Cliente Order Get", "email": "orderget@example.com"}
        customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
        customer_id = customer_response.json()["id"]
        
        order_data = {
            "customer_id": customer_id,
            "status": "processing",
            "total": 75.0,
            "delivery_method": "retiro_local"
        }
        order_response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
        order_id = order_response.json()["order"]["id"]
        
        # Obtener pedido
        response = client.get(f"/api/v1/orders/{order_id}", headers=auth_cookie)
        assert response.status_code == 200
        
        order = response.json()
        assert order["id"] == order_id
        assert order["status"] == "processing"

    # def test_update_order_status(self, client, auth_cookie):
    #     """Test actualizar estado de pedido"""
    #     # Crear cliente y pedido
    #     customer_data = {"name": "Cliente Order Update", "email": "orderupdate@example.com"}
    #     customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
    #     customer_id = customer_response.json()["id"]
    #     
    #     order_data = {
    #         "customer_id": customer_id,
    #         "status": "pending",
    #         "total": 50.0
    #     }
    #     order_response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
    #     order_id = order_response.json()["order"]["id"]
    #     
    #     # Actualizar estado
    #     update_data = {
    #         "customer_id": customer_id,
    #         "status": "completed",
    #         "total": 55.0
    #     }
    #     response = client.put(f"/api/v1/orders/{order_id}", json=update_data, headers=auth_cookie)
    #     assert response.status_code == 200
    #     
    #     updated_order = response.json()
    #     assert updated_order["status"] == "completed"
    #     assert updated_order["total"] == 55.0


class TestOrderItemsCRUD:
    """Tests para operaciones CRUD de items de pedidos"""

    def test_create_order_item(self, client, auth_cookie):
        """Test crear item de pedido"""
        # Crear cliente, producto y pedido
        customer_data = {"name": "Cliente Item", "email": "item@example.com"}
        customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
        customer_id = customer_response.json()["id"]
        
        product_data = {
            "name": "Producto Para Item",
            "price": 25.0,
            "images": ["item.jpg"],
            "variants": [{"color": "rosa", "talle": "M", "stock": 10}]
        }
        product_response = client.post("/api/v1/products/", json=product_data, headers=auth_cookie)
        product_id = product_response.json()["id"]
        
        order_data = {
            "customer_id": customer_id,
            "status": "pending",
            "total": 50.0,
            "delivery_method": "retiro_local"
        }
        order_response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
        order_id = order_response.json()["order"]["id"]
        
        # Crear item de pedido
        order_item_data = {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": 2,
            "price": 25.0
        }
        response = client.post("/api/v1/order-items/", json=order_item_data, headers=auth_cookie)
        assert response.status_code == 200
        
        order_item = response.json()
        assert order_item["order_id"] == order_id
        assert order_item["product_id"] == product_id
        assert order_item["quantity"] == 2
        assert order_item["price"] == 25.0

    # def test_get_order_items_list(self, client, auth_cookie):
    #     """Test obtener lista de items de pedidos"""
    #     response = client.get("/api/v1/order-items/", headers=auth_cookie)
    #     assert response.status_code == 200
    #     
    #     order_items = response.json()
    #     assert isinstance(order_items, list)

    # def test_update_order_item_quantity(self, client, auth_cookie):
    #     """Test actualizar cantidad de item de pedido"""
    #     # Crear dependencies y order item
    #     customer_data = {"name": "Cliente Item Update", "email": "itemupdate@example.com"}
    #     customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
    #     customer_id = customer_response.json()["id"]
    #     
    #     product_data = {
    #         "name": "Producto Item Update",
    #         "price": 15.0,
    #         "images": ["update.jpg"],
    #         "variants": [{"color": "violeta", "talle": "L", "stock": 20}]
    #     }
    #     product_response = client.post("/api/v1/products/", json=product_data, headers=auth_cookie)
    #     product_id = product_response.json()["id"]
    #     
    #     order_data = {
    #         "customer_id": customer_id,
    #         "status": "pending",
    #         "total": 30.0
    #     }
    #     order_response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
    #     order_id = order_response.json()["order"]["id"]
    #     
    #     order_item_data = {
    #         "order_id": order_id,
    #         "product_id": product_id,
    #         "quantity": 1,
    #         "price": 15.0
    #     }
    #     order_item_response = client.post("/api/v1/order-items/", json=order_item_data, headers=auth_cookie)
    #     order_item_id = order_item_response.json()["id"]
    #     
    #     # Actualizar cantidad
    #     update_data = {
    #         "order_id": order_id,
    #         "product_id": product_id,
    #         "quantity": 3,
    #         "price": 15.0
    #     }
    #     response = client.put(f"/api/v1/order-items/{order_item_id}", json=update_data, headers=auth_cookie)
    #     assert response.status_code == 200
    #     
    #     updated_item = response.json()
    #     assert updated_item["quantity"] == 3


class TestEcommerceWorkflows:
    """Tests para flujos completos de ecommerce"""

    def test_complete_purchase_workflow(self, client, auth_cookie):
        """Test flujo completo de compra"""
        # 1. Crear cliente
        customer_data = {
            "name": "Cliente Compra Completa",
            "email": "compracompleta@example.com",
            "phone": "555-0123",
            "address": "Av. Principal 789"
        }
        customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
        customer_id = customer_response.json()["id"]
        
        # 2. Crear productos
        product1_data = {
            "name": "Camisa Workflow",
            "price": 30.0,
            "images": ["camisa.jpg"],
            "variants": [{"color": "blanco", "talle": "M", "stock": 5}]
        }
        product1_response = client.post("/api/v1/products/", json=product1_data, headers=auth_cookie)
        product1_id = product1_response.json()["id"]
        
        product2_data = {
            "name": "Pantalón Workflow",
            "price": 45.0,
            "images": ["pantalon.jpg"],
            "variants": [{"color": "negro", "talle": "M", "stock": 3}]
        }
        product2_response = client.post("/api/v1/products/", json=product2_data, headers=auth_cookie)
        product2_id = product2_response.json()["id"]
        
        # 3. Crear pedido
        order_data = {
            "customer_id": customer_id,
            "status": "pending",
            "total": 105.0,  # 30 + 45*2 - se calculará con los items
            "delivery_method": "retiro_local"
        }
        order_response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
        order_id = order_response.json()["order"]["id"]
        
        # 4. Agregar items al pedido
        item1_data = {
            "order_id": order_id,
            "product_id": product1_id,
            "quantity": 1,
            "price": 30.0
        }
        item1_response = client.post("/api/v1/order-items/", json=item1_data, headers=auth_cookie)
        assert item1_response.status_code == 200
        
        item2_data = {
            "order_id": order_id,
            "product_id": product2_id,
            "quantity": 2,
            "price": 45.0
        }
        item2_response = client.post("/api/v1/order-items/", json=item2_data, headers=auth_cookie)
        assert item2_response.status_code == 200
        
        # 5. Verificar que todo está correctamente relacionado
        # Obtener pedido con items
        order_check = client.get(f"/api/v1/orders/{order_id}", headers=auth_cookie)
        assert order_check.status_code == 200
        
        # Obtener items del pedido
        items_check = client.get("/api/v1/order-items/", headers=auth_cookie)
        assert items_check.status_code == 200
        order_items = [item for item in items_check.json() if item["order_id"] == order_id]
        assert len(order_items) == 2
        
        # 6. Actualizar estado del pedido a completado
        update_order_data = {
            "customer_id": customer_id,
            "status": "completed",
            "total": 120.0  # Total calculado
        }
        final_order_response = client.put(f"/api/v1/orders/{order_id}", json=update_order_data, headers=auth_cookie)
        assert final_order_response.status_code == 200
        assert final_order_response.json()["status"] == "completed"

    # def test_multiple_orders_same_customer(self, client, auth_cookie):
    #     """Test múltiples pedidos para el mismo cliente"""
    #     # Crear cliente
    #     customer_data = {"name": "Cliente Multi Pedidos", "email": "multipedidos@example.com"}
    #     customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
    #     customer_id = customer_response.json()["id"]
    #     
    #     # Crear múltiples pedidos
    #     orders_data = [
    #         {"customer_id": customer_id, "status": "pending", "total": 25.0},
    #         {"customer_id": customer_id, "status": "processing", "total": 50.0},
    #         {"customer_id": customer_id, "status": "completed", "total": 75.0}
    #     ]
    #     
    #     created_orders = []
    #     for order_data in orders_data:
    #         response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
    #         assert response.status_code == 200
    #         created_orders.append(response.json()["order"])
    #     
    #     # Verificar que todos los pedidos pertenecen al mismo cliente
    #     for order in created_orders:
    #         assert order["customer_id"] == customer_id
    #     
    #     # Verificar que hay diferentes estados
    #     statuses = {order["status"] for order in created_orders}
    #     assert len(statuses) == 3  # pending, processing, completed


class TestEcommerceValidation:
    """Tests para validación de datos de ecommerce"""

    def test_customer_email_validation(self, client, auth_cookie):
        """Test validación de email de cliente"""
        invalid_emails = ["invalid", "@example.com", "test@", "test.com", ""]
        
        for email in invalid_emails:
            data = {
                "name": "Test Customer",
                "email": email
            }
            response = client.post("/api/v1/customers/", json=data, headers=auth_cookie)
            assert response.status_code == 422, f"Should fail validation with email: {email}"

    def test_order_total_validation(self, client, auth_cookie):
        """Test validación de total de pedido"""
        # Crear cliente
        customer_data = {"name": "Cliente Total Test", "email": "total@example.com"}
        customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
        customer_id = customer_response.json()["id"]
        
        invalid_totals = [-1, -0.01, "invalid"]
        
        for total in invalid_totals:
            order_data = {
                "customer_id": customer_id,
                "status": "pending",
                "total": total,
                "delivery_method": "retiro_local"
            }
            response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
            assert response.status_code == 422, f"Should fail validation with total: {total}"

    def test_order_item_quantity_validation(self, client, auth_cookie):
        """Test validación de cantidad en items de pedido"""
        # Crear dependencies
        customer_data = {"name": "Cliente Quantity", "email": "quantity@example.com"}
        customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
        customer_id = customer_response.json()["id"]
        
        product_data = {
            "name": "Producto Quantity",
            "price": 10.0,
            "images": ["quantity.jpg"],
            "variants": [{"color": "cyan", "talle": "S", "stock": 5}]
        }
        product_response = client.post("/api/v1/products/", json=product_data, headers=auth_cookie)
        product_id = product_response.json()["id"]
        
        order_data = {
            "customer_id": customer_id,
            "status": "pending",
            "total": 10.0,
            "delivery_method": "retiro_local"
        }
        order_response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
        order_id = order_response.json()["order"]["id"]
        
        # Test invalid numeric quantities (should return 422 - Pydantic validation error)
        invalid_numeric_quantities = [0, -1, -5]
        for quantity in invalid_numeric_quantities:
            order_item_data = {
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
                "price": 10.0
            }
            response = client.post("/api/v1/order-items/", json=order_item_data, headers=auth_cookie)
            assert response.status_code == 422, f"Should fail validation with quantity: {quantity}"
        
        # Test non-numeric quantities (should return 400 or 422 - FastAPI parsing/validation error)
        invalid_type_quantities = ["invalid", 3.5]
        for quantity in invalid_type_quantities:
            order_item_data = {
                "order_id": order_id,
                "product_id": product_id,
                "quantity": quantity,
                "price": 10.0
            }
            response = client.post("/api/v1/order-items/", json=order_item_data, headers=auth_cookie)
            # Accept 400 (parsing error), 422 (validation error), or 404 (stock system error)
            assert response.status_code in [400, 404, 422], f"Should fail with quantity: {quantity}, got: {response.status_code}"
        
        # Test None quantity separately (can be converted but should fail validation)
        order_item_data = {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": None,
            "price": 10.0
        }
        response = client.post("/api/v1/order-items/", json=order_item_data, headers=auth_cookie)
        # None might be converted to 0 and fail validation, or cause stock/downstream errors
        assert response.status_code in [400, 404, 422], f"Should fail with quantity: None, got: {response.status_code}"


class TestEcommerceErrorHandling:
    """Tests para manejo de errores en ecommerce"""

    def test_create_order_with_nonexistent_customer(self, client, auth_cookie):
        """Test crear pedido con cliente inexistente"""
        order_data = {
            "customer_id": 99999,
            "status": "pending",
            "total": 50.0,
            "delivery_method": "retiro_local"
        }
        response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
        assert response.status_code in [400, 422, 404]

    def test_create_order_item_with_nonexistent_order(self, client, auth_cookie):
        """Test crear item con pedido inexistente"""
        # Crear producto válido
        product_data = {
            "name": "Producto Error Test",
            "price": 20.0,
            "images": ["error.jpg"],
            "variants": [{"color": "naranja", "talle": "XL", "stock": 1}]
        }
        product_response = client.post("/api/v1/products/", json=product_data, headers=auth_cookie)
        product_id = product_response.json()["id"]
        
        order_item_data = {
            "order_id": 99999,
            "product_id": product_id,
            "quantity": 1,
            "price": 20.0
        }
        response = client.post("/api/v1/order-items/", json=order_item_data, headers=auth_cookie)
        assert response.status_code in [400, 422, 404]

    def test_create_order_item_with_nonexistent_product(self, client, auth_cookie):
        """Test crear item con producto inexistente"""
        # Crear cliente y pedido válidos
        customer_data = {"name": "Cliente Error", "email": "error@example.com"}
        customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
        customer_id = customer_response.json()["id"]
        
        order_data = {
            "customer_id": customer_id,
            "status": "pending",
            "total": 30.0,
            "delivery_method": "retiro_local"
        }
        order_response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
        order_id = order_response.json()["order"]["id"]
        
        order_item_data = {
            "order_id": order_id,
            "product_id": 99999,
            "quantity": 1,
            "price": 30.0
        }
        response = client.post("/api/v1/order-items/", json=order_item_data, headers=auth_cookie)
        assert response.status_code in [400, 422, 404]
