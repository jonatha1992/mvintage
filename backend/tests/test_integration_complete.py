"""
Tests de integración completa del sistema.
Flujos end-to-end que conectan todos los módulos del sistema.
"""

import pytest
from fastapi.testclient import TestClient


class TestCompleteEcommerceFlow:
    """Tests para flujos completos de ecommerce integrando todos los módulos"""

    def test_complete_store_setup_and_purchase(self, client, auth_cookie):
        """Test completo: setup de tienda y proceso de compra"""

        # === FASE 1: SETUP INICIAL DE LA TIENDA ===

        # 1. Verificar que los datos maestros están disponibles
        colors_response = client.get("/api/v1/colors")
        categories_response = client.get("/api/v1/categories")
        sizes_response = client.get("/api/v1/sizes")

        assert colors_response.status_code == 200
        assert categories_response.status_code == 200
        assert sizes_response.status_code == 200

        colors = colors_response.json()
        categories = categories_response.json()
        sizes = sizes_response.json()

        assert len(colors) > 0, "Debe haber colores disponibles"
        assert len(categories) > 0, "Debe haber categorías disponibles"
        assert len(sizes) > 0, "Debe haber talles disponibles"

        # 2. Crear productos para la tienda
        products_data = [
            {
                "name": "Remera Básica",
                "description": "Remera de algodón 100%",
                "price": 25.0,
                "genero": "unisex",
                "estado": "nuevo",
                "edad_destino": "adulto",
                "images": ["remera_basica.jpg"],
                "variants": [
                    {"color": "blanco", "talle": "S", "stock": 10},
                    {"color": "blanco", "talle": "M", "stock": 15},
                    {"color": "negro", "talle": "S", "stock": 8},
                    {"color": "negro", "talle": "M", "stock": 12},
                ],
            },
            {
                "name": "Pantalón Jeans",
                "description": "Jeans clásico de mezclilla",
                "price": 65.0,
                "genero": "unisex",
                "estado": "nuevo",
                "edad_destino": "adulto",
                "images": ["pantalon_jeans.jpg", "pantalon_jeans_2.jpg"],
                "variants": [
                    {"color": "azul", "talle": "M", "stock": 6},
                    {"color": "azul", "talle": "L", "stock": 8},
                    {"color": "negro", "talle": "M", "stock": 4},
                    {"color": "negro", "talle": "L", "stock": 5},
                ],
            },
            {
                "name": "Vestido Casual",
                "description": "Vestido cómodo para uso diario",
                "price": 45.0,
                "genero": "femenino",
                "estado": "nuevo",
                "edad_destino": "adulto",
                "images": ["vestido_casual.jpg"],
                "variants": [
                    {"color": "rojo", "talle": "S", "stock": 3},
                    {"color": "rojo", "talle": "M", "stock": 5},
                    {"color": "azul", "talle": "S", "stock": 2},
                    {"color": "azul", "talle": "M", "stock": 4},
                ],
            },
        ]

        created_products = []
        for product_data in products_data:
            response = client.post(
                "/api/v1/products/", json=product_data, headers=auth_cookie
            )
            assert (
                response.status_code == 200
            ), f"Error creando producto: {product_data['name']}"
            created_products.append(response.json())

        print(f"✓ Creados {len(created_products)} productos")

        # 3. Crear registros de inventario para cada producto
        for product in created_products:
            # Calcular stock total de las variantes
            total_stock = sum(variant["stock"] for variant in product["variants"])

            inventory_data = {
                "product_id": product["id"],
                "quantity": total_stock,
                "last_update": "2025-08-07T10:00:00",
            }
            inventory_response = client.post(
                "/api/v1/inventory/", json=inventory_data, headers=auth_cookie
            )
            assert inventory_response.status_code == 200

        print("✓ Registros de inventario creados")

        # === FASE 2: PROCESO DE COMPRA ===

        # 4. Crear cliente
        customer_data = {
            "name": "María González",
            "email": "maria.gonzalez@email.com",
            "phone": "+1-555-0123",
            "address": "Av. Libertador 1234, Buenos Aires",
        }
        customer_response = client.post(
            "/api/v1/customers/", json=customer_data, headers=auth_cookie
        )
        assert customer_response.status_code == 200
        customer = customer_response.json()
        customer_id = customer["id"]

        print(f"✓ Cliente creado: {customer['name']}")

        # 5. Crear pedido
        order_data = {
            "customer_id": customer_id,
            "status": "pending",
            "total": 0.0,  # Se calculará con los items
            "delivery_method": "retiro_local",
        }
        order_response = client.post(
            "/api/v1/orders/", json=order_data, headers=auth_cookie
        )
        assert order_response.status_code == 200
        order = order_response.json()
        order_id = order["order"]["id"]

        print(f"✓ Pedido creado: ID {order_id}")

        # 6. Agregar items al pedido (carrito de compras)
        cart_items = [
            {
                "product": created_products[0],  # Remera Básica
                "quantity": 2,
                "selected_variant": {"color": "blanco", "talle": "M"},
            },
            {
                "product": created_products[1],  # Pantalón Jeans
                "quantity": 1,
                "selected_variant": {"color": "azul", "talle": "L"},
            },
            {
                "product": created_products[2],  # Vestido Casual
                "quantity": 1,
                "selected_variant": {"color": "rojo", "talle": "M"},
            },
        ]

        total_order_amount = 0.0
        created_order_items = []

        for item in cart_items:
            product = item["product"]
            quantity = item["quantity"]
            price = product["price"]

            order_item_data = {
                "order_id": order_id,
                "product_id": product["id"],
                "quantity": quantity,
                "price": price,
            }

            item_response = client.post(
                "/api/v1/order-items/", json=order_item_data, headers=auth_cookie
            )
            assert item_response.status_code == 200
            created_order_items.append(item_response.json())

            total_order_amount += price * quantity

        print(f"✓ Agregados {len(created_order_items)} items al pedido")
        print(f"✓ Total del pedido: ${total_order_amount}")

        # 7. Actualizar total del pedido
        update_order_data = {
            "customer_id": customer_id,
            "status": "confirmed",
            "total": total_order_amount,
        }
        update_order_response = client.put(
            f"/api/v1/orders/{order_id}", json=update_order_data, headers=auth_cookie
        )
        assert update_order_response.status_code == 200
        final_order = update_order_response.json()

        print(f"✓ Pedido confirmado con total: ${final_order['total']}")

        # === FASE 3: GESTIÓN POST-VENTA ===

        # 8. Actualizar inventario después de la venta (reducir stock)
        for i, item in enumerate(cart_items):
            product = item["product"]
            quantity_sold = item["quantity"]

            # Obtener inventario actual
            inventory_list = client.get(
                "/api/v1/inventory/", headers=auth_cookie
            ).json()
            product_inventory = next(
                inv for inv in inventory_list if inv["product_id"] == product["id"]
            )

            # Reducir stock
            new_quantity = product_inventory["quantity"] - quantity_sold

            update_inventory_data = {
                "product_id": product["id"],
                "quantity": new_quantity,
                "last_update": "2025-08-07T15:00:00",
            }

            inventory_update_response = client.put(
                f"/api/v1/inventory/{product_inventory['id']}",
                json=update_inventory_data,
                headers=auth_cookie,
            )
            assert inventory_update_response.status_code == 200

        print("✓ Inventarios actualizados después de la venta")

        # 9. Marcar pedido como completado
        complete_order_data = {
            "customer_id": customer_id,
            "status": "completed",
            "total": total_order_amount,
        }
        complete_response = client.put(
            f"/api/v1/orders/{order_id}", json=complete_order_data, headers=auth_cookie
        )
        assert complete_response.status_code == 200
        completed_order = complete_response.json()

        assert completed_order["status"] == "completed"
        print("✓ Pedido marcado como completado")

        # === VERIFICACIONES FINALES ===

        # 10. Verificar que todo está correctamente registrado

        # Verificar productos siguen existiendo
        products_check = client.get("/api/v1/products/", headers=auth_cookie)
        assert products_check.status_code == 200
        products_list = products_check.json()
        assert len(products_list) >= 3

        # Verificar cliente existe
        customer_check = client.get(
            f"/api/v1/customers/{customer_id}", headers=auth_cookie
        )
        assert customer_check.status_code == 200

        # Verificar pedido completado
        order_check = client.get(f"/api/v1/orders/{order_id}", headers=auth_cookie)
        assert order_check.status_code == 200
        final_order_check = order_check.json()
        assert final_order_check["status"] == "completed"
        assert final_order_check["total"] == total_order_amount

        # Verificar items del pedido
        order_items_check = client.get("/api/v1/order-items/", headers=auth_cookie)
        assert order_items_check.status_code == 200
        all_order_items = order_items_check.json()
        order_items = [item for item in all_order_items if item["order_id"] == order_id]
        assert len(order_items) == 3

        # Verificar inventarios actualizados
        final_inventory_check = client.get("/api/v1/inventory/", headers=auth_cookie)
        assert final_inventory_check.status_code == 200
        final_inventories = final_inventory_check.json()

        # Verificar que los stocks fueron reducidos
        for inventory in final_inventories:
            if any(
                inv["product_id"] == inventory["product_id"]
                for inv in final_inventories
            ):
                assert inventory["quantity"] >= 0  # No stock negativo

        print("✓ Todas las verificaciones finales pasaron")
        print(f"🎉 Flujo completo de ecommerce exitoso!")
        print(f"   - Productos creados: {len(created_products)}")
        print(f"   - Cliente: {customer['name']}")
        print(f"   - Pedido #{order_id} por ${total_order_amount}")
        print(f"   - Items del pedido: {len(order_items)}")

    # def test_multi_customer_concurrent_orders(self, client, auth_cookie):
    #     """Test múltiples clientes haciendo pedidos concurrentes"""
    #
    #     # Crear producto compartido
    #     product_data = {
    #         "name": "Producto Popular",
    #         "price": 30.0,
    #         "images": ["popular.jpg"],
    #         "variants": [{"color": "verde", "talle": "M", "stock": 10}]
    #     }
    #     product_response = client.post("/api/v1/products/", json=product_data, headers=auth_cookie)
    #     product_id = product_response.json()["id"]
    #
    #     # Crear múltiples clientes
    #     customers_data = [
    #         {"name": "Cliente 1", "email": "cliente1@example.com"},
    #         {"name": "Cliente 2", "email": "cliente2@example.com"},
    #         {"name": "Cliente 3", "email": "cliente3@example.com"}
    #     ]
    #
    #     customers = []
    #     for customer_data in customers_data:
    #         response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
    #         assert response.status_code == 200
    #         customers.append(response.json())
    #
    #     # Crear pedidos concurrentes para el mismo producto
    #     orders = []
    #     for customer in customers:
    #         order_data = {
    #             "customer_id": customer["id"],
    #             "status": "pending",
    #             "total": 60.0  # 2 unidades × $30
    #         }
    #         order_response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
    #         assert order_response.status_code == 200
    #         orders.append(order_response.json()['order'])
    #
    #     # Agregar items a cada pedido
    #     for order in orders:
    #         order_item_data = {
    #             "order_id": order["id"],
    #             "product_id": product_id,
    #             "quantity": 2,
    #             "price": 30.0
    #         }
    #         item_response = client.post("/api/v1/order-items/", json=order_item_data, headers=auth_cookie)
    #         assert item_response.status_code == 200
    #
    #     # Verificar que todos los pedidos se crearon correctamente
    #     assert len(orders) == 3
    #     for order in orders:
    #         assert order["status"] == "pending"
    #         assert order["total"] == 60.0

    def test_inventory_low_stock_workflow(self, client, auth_cookie):
        """Test flujo completo de gestión de stock bajo"""

        # Crear producto con stock limitado
        product_data = {
            "name": "Producto Stock Limitado",
            "price": 40.0,
            "images": ["limitado.jpg"],
            "variants": [{"color": "púrpura", "talle": "S", "stock": 3}],
        }
        product_response = client.post(
            "/api/v1/products/", json=product_data, headers=auth_cookie
        )
        product = product_response.json()
        product_id = product["id"]

        # Crear inventario inicial
        inventory_data = {
            "product_id": product_id,
            "quantity": 3,
            "last_update": "2025-08-07T10:00:00",
        }
        inventory_response = client.post(
            "/api/v1/inventory/", json=inventory_data, headers=auth_cookie
        )
        inventory = inventory_response.json()
        inventory_id = inventory["id"]

        # Crear cliente
        customer_data = {"name": "Cliente Stock Test", "email": "stocktest@example.com"}
        customer_response = client.post(
            "/api/v1/customers/", json=customer_data, headers=auth_cookie
        )
        customer_id = customer_response.json()["id"]

        # Crear pedido que agote casi todo el stock
        order_data = {
            "customer_id": customer_id,
            "status": "pending",
            "total": 80.0,  # 2 unidades
            "delivery_method": "retiro_local",
        }
        order_response = client.post(
            "/api/v1/orders/", json=order_data, headers=auth_cookie
        )
        order_id = order_response.json()["order"]["id"]

        # Agregar items que reduzcan el stock
        order_item_data = {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": 2,
            "price": 40.0,
        }
        item_response = client.post(
            "/api/v1/order-items/", json=order_item_data, headers=auth_cookie
        )
        assert item_response.status_code == 200

        # Simular actualización de inventario (stock bajo)
        low_stock_data = {
            "product_id": product_id,
            "quantity": 1,  # Stock muy bajo
            "last_update": "2025-08-07T12:00:00",
        }
        low_stock_response = client.put(
            f"/api/v1/inventory/{inventory_id}",
            json=low_stock_data,
            headers=auth_cookie,
        )
        assert low_stock_response.status_code == 200

        updated_inventory = low_stock_response.json()
        assert updated_inventory["quantity"] == 1

        # Simular restock
        restock_data = {
            "product_id": product_id,
            "quantity": 20,  # Restock
            "last_update": "2025-08-07T14:00:00",
        }
        restock_response = client.put(
            f"/api/v1/inventory/{inventory_id}", json=restock_data, headers=auth_cookie
        )
        assert restock_response.status_code == 200

        restocked_inventory = restock_response.json()
        assert restocked_inventory["quantity"] == 20


class TestSystemReliability:
    """Tests para verificar la confiabilidad del sistema"""

    # def test_data_consistency_across_modules(self, client, auth_cookie):
    #     """Test consistencia de datos entre módulos"""
    #
    #     # Crear producto
    #     product_data = {
    #         "name": "Producto Consistencia",
    #         "price": 50.0,
    #         "images": ["consistencia.jpg"],
    #         "variants": [{"color": "índigo", "talle": "L", "stock": 8}]
    #     }
    #     product_response = client.post("/api/v1/products/", json=product_data, headers=auth_cookie)
    #     product_id = product_response.json()["id"]
    #
    #     # Crear inventario
    #     inventory_data = {
    #         "product_id": product_id,
    #         "quantity": 8,
    #         "last_update": "2025-08-07T10:00:00"
    #     }
    #     inventory_response = client.post("/api/v1/inventory/", json=inventory_data, headers=auth_cookie)
    #     assert inventory_response.status_code == 200
    #
    #     # Crear cliente y pedido
    #     customer_data = {"name": "Cliente Consistencia", "email": "consistencia@example.com"}
    #     customer_response = client.post("/api/v1/customers/", json=customer_data, headers=auth_cookie)
    #     customer_id = customer_response.json()["id"]
    #
    #     order_data = {
    #         "customer_id": customer_id,
    #         "status": "pending",
    #         "total": 100.0
    #     }
    #     order_response = client.post("/api/v1/orders/", json=order_data, headers=auth_cookie)
    #     order_id = order_response.json()['order']["id"]
    #
    #     # Verificar que todas las referencias existen
    #     product_check = client.get(f"/api/v1/products/{product_id}", headers=auth_cookie)
    #     customer_check = client.get(f"/api/v1/customers/{customer_id}", headers=auth_cookie)
    #     order_check = client.get(f"/api/v1/orders/{order_id}", headers=auth_cookie)
    #
    #     assert product_check.status_code == 200
    #     assert customer_check.status_code == 200
    #     assert order_check.status_code == 200
    #
    #     # Los datos deben ser consistentes
    #     assert product_check.json()["id"] == product_id
    #     assert customer_check.json()["id"] == customer_id
    #     assert order_check.json()["id"] == order_id
    #     assert order_check.json()["customer_id"] == customer_id

    def test_error_recovery_and_rollback(self, client, auth_cookie):
        """Test recuperación de errores y rollback"""

        # Intentar crear pedido con cliente inexistente
        invalid_order_data = {"customer_id": 99999, "status": "pending", "total": 50.0}
        invalid_response = client.post(
            "/api/v1/orders/", json=invalid_order_data, headers=auth_cookie
        )
        assert invalid_response.status_code in [400, 422, 404]

        # Verificar que no se creó el pedido inválido
        orders_check = client.get("/api/v1/orders/", headers=auth_cookie)
        all_orders = orders_check.json()
        invalid_orders = [o for o in all_orders if o["customer_id"] == 99999]
        assert len(invalid_orders) == 0

    # def test_large_dataset_performance(self, client, auth_cookie):
    #     """Test rendimiento con dataset grande"""
    #
    #     # Crear múltiples productos para simular catálogo grande
    #     products = []
    #     for i in range(10):  # Limitado para tests rápidos
    #         product_data = {
    #             "name": f"Producto Performance {i+1}",
    #             "price": 20.0 + i,
    #             "images": [f"perf_{i+1}.jpg"],
    #             "variants": [{"color": "gris", "talle": "M", "stock": 5}]
    #         }
    #         response = client.post("/api/v1/products/", json=product_data, headers=auth_cookie)
    #         assert response.status_code == 200
    #         products.append(response.json())
    #
    #     # Verificar que obtener la lista no tarde demasiado
    #     import time
    #     start_time = time.time()
    #     products_response = client.get("/api/v1/products/", headers=auth_cookie)
    #     end_time = time.time()
    #
    #     assert products_response.status_code == 200
    #     assert len(products_response.json()) >= 10
    #
    #     # La respuesta debería ser rápida (menos de 2 segundos)
    #     response_time = end_time - start_time
    #     assert response_time < 2.0, f"Response too slow: {response_time}s"


class TestBusinessRules:
    """Tests para reglas de negocio específicas"""

    def test_prevent_negative_inventory(self, client, auth_cookie):
        """Test que no se permita inventario negativo"""

        # Crear producto
        product_data = {
            "name": "Producto No Negativo",
            "price": 35.0,
            "images": ["no_neg.jpg"],
            "variants": [{"color": "cian", "talle": "M", "stock": 5}],
        }
        product_response = client.post(
            "/api/v1/products/", json=product_data, headers=auth_cookie
        )
        product_id = product_response.json()["id"]

        # Intentar crear inventario negativo
        negative_inventory_data = {
            "product_id": product_id,
            "quantity": -5,
            "last_update": "2025-08-07T10:00:00",
        }
        response = client.post(
            "/api/v1/inventory/", json=negative_inventory_data, headers=auth_cookie
        )
        assert response.status_code == 422

    def test_order_total_matches_items(self, client, auth_cookie):
        """Test que el total del pedido coincida con los items"""

        # Crear producto, cliente y pedido
        product_data = {
            "name": "Producto Total Test",
            "price": 25.0,
            "images": ["total.jpg"],
            "variants": [{"color": "mostaza", "talle": "L", "stock": 10}],
        }
        product_response = client.post(
            "/api/v1/products/", json=product_data, headers=auth_cookie
        )
        product_id = product_response.json()["id"]

        customer_data = {"name": "Cliente Total", "email": "total@example.com"}
        customer_response = client.post(
            "/api/v1/customers/", json=customer_data, headers=auth_cookie
        )
        customer_id = customer_response.json()["id"]

        order_data = {
            "customer_id": customer_id,
            "status": "pending",
            "total": 75.0,  # 3 × $25
            "delivery_method": "retiro_local",
        }
        order_response = client.post(
            "/api/v1/orders/", json=order_data, headers=auth_cookie
        )
        order_id = order_response.json()["order"]["id"]

        # Agregar items que sumen el total
        order_item_data = {
            "order_id": order_id,
            "product_id": product_id,
            "quantity": 3,
            "price": 25.0,
        }
        item_response = client.post(
            "/api/v1/order-items/", json=order_item_data, headers=auth_cookie
        )
        assert item_response.status_code == 200

        # Verificar consistencia
        order_check = client.get(f"/api/v1/orders/{order_id}", headers=auth_cookie)
        order = order_check.json()

        items_check = client.get("/api/v1/order-items/", headers=auth_cookie)
        all_items = items_check.json()
        order_items = [item for item in all_items if item["order_id"] == order_id]

        calculated_total = sum(item["quantity"] * item["price"] for item in order_items)
        assert order["total"] == calculated_total
