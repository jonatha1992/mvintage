"""
Controlador para gestión de pagos en efectivo contra entrega.
Incluye cálculo de costos de envío, gestión de zonas de entrega
y programación de entregas.
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.order import Order
from app.models.customer import Customer
from app.models.payment_config import PaymentConfig

logger = logging.getLogger(__name__)


class CashController:
    """Controlador para manejar pagos en efectivo contra entrega"""
    
    def get_delivery_zones(self, session: Session) -> Dict[str, Any]:
        """
        Obtiene configuración de zonas de entrega desde PaymentConfig.
        
        Args:
            session: Sesión de base de datos
            
        Returns:
            Dict con configuración de zonas de entrega
        """
        try:
            configs = session.exec(
                select(PaymentConfig).where(
                    PaymentConfig.config_type == "delivery_zones",
                    PaymentConfig.is_active == True
                )
            ).all()
            
            zones = {}
            for config in configs:
                try:
                    zone_data = json.loads(config.config_data)
                    zones[config.config_name] = zone_data
                except json.JSONDecodeError:
                    logger.warning(f"Configuración de zona inválida: {config.config_name}")
                    continue
            
            # Valores por defecto si no hay configuración
            if not zones:
                zones = {
                    "caba": {
                        "name": "CABA", 
                        "cost": 800, 
                        "free_threshold": 25000, 
                        "days": "2-3",
                        "description": "Capital Federal"
                    },
                    "gba_norte": {
                        "name": "GBA Norte",
                        "cost": 1200, 
                        "free_threshold": 30000, 
                        "days": "3-4",
                        "description": "Zona Norte del Gran Buenos Aires"
                    },
                    "gba_sur": {
                        "name": "GBA Sur",
                        "cost": 1200, 
                        "free_threshold": 30000, 
                        "days": "3-4",
                        "description": "Zona Sur del Gran Buenos Aires"
                    },
                    "gba_oeste": {
                        "name": "GBA Oeste",
                        "cost": 1200, 
                        "free_threshold": 30000, 
                        "days": "3-4",
                        "description": "Zona Oeste del Gran Buenos Aires"
                    }
                }
                logger.warning("Usando zonas de entrega por defecto - configurar en PaymentConfig")
            
            return zones
            
        except Exception as e:
            logger.error(f"Error obteniendo zonas de entrega: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error obteniendo configuración de entregas"
            )
    
    def detect_delivery_zone(self, address: str, city: str) -> str:
        """
        Detecta la zona de entrega según dirección y ciudad.
        
        Args:
            address: Dirección del cliente
            city: Ciudad del cliente
            
        Returns:
            str: Código de zona detectada
        """
        if not city:
            return "gba_sur"  # Zona por defecto
        
        city_lower = city.lower().strip()
        
        # Palabras clave para CABA
        caba_keywords = [
            "caba", "capital", "capital federal", "buenos aires", "ciudad autónoma",
            "palermo", "recoleta", "belgrano", "villa crespo", "caballito",
            "flores", "barracas", "san telmo", "puerto madero", "retiro",
            "once", "balvanera", "constitución"
        ]
        
        if any(keyword in city_lower for keyword in caba_keywords):
            return "caba"
        
        # Palabras clave para GBA Norte
        norte_keywords = [
            "tigre", "san isidro", "vicente lópez", "olivos", "martínez",
            "acassuso", "beccar", "florida", "munro", "villa adelina",
            "san fernando", "victoria"
        ]
        
        if any(keyword in city_lower for keyword in norte_keywords):
            return "gba_norte"
        
        # Palabras clave para GBA Oeste
        oeste_keywords = [
            "morón", "castelar", "ituzaingó", "hurlingham", "villa tesei",
            "ramos mejía", "ciudadela", "santos lugares", "caseros"
        ]
        
        if any(keyword in city_lower for keyword in oeste_keywords):
            return "gba_oeste"
        
        # Por defecto: GBA Sur
        return "gba_sur"
    
    def calculate_delivery_cost(self, customer: Customer, order_total: float, session: Session) -> Dict[str, Any]:
        """
        Calcula el costo de envío según la zona y el monto de la orden.
        
        Args:
            customer: Cliente con dirección
            order_total: Total de la orden
            session: Sesión de base de datos
            
        Returns:
            Dict con información de entrega y costo
        """
        try:
            zones = self.get_delivery_zones(session)
            zone_code = self.detect_delivery_zone(customer.address or "", customer.city or "")
            
            zone_config = zones.get(zone_code, zones["gba_sur"])
            
            # Calcular costo (gratis si supera el threshold)
            delivery_cost = 0 if order_total >= zone_config["free_threshold"] else zone_config["cost"]
            
            return {
                "zone_code": zone_code,
                "zone_name": zone_config["name"],
                "zone_description": zone_config.get("description", ""),
                "cost": delivery_cost,
                "original_cost": zone_config["cost"],
                "estimated_days": zone_config["days"],
                "free_threshold": zone_config["free_threshold"],
                "is_free": delivery_cost == 0,
                "savings": zone_config["cost"] if delivery_cost == 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculando costo de entrega: {e}")
            # Retornar valores por defecto en caso de error
            return {
                "zone_code": "gba_sur",
                "zone_name": "GBA Sur",
                "zone_description": "Zona Sur del Gran Buenos Aires",
                "cost": 1200,
                "original_cost": 1200,
                "estimated_days": "3-4",
                "free_threshold": 30000,
                "is_free": False,
                "savings": 0
            }
    
    def create_cash_order(self, order_id: int, session: Session) -> Dict[str, Any]:
        raise HTTPException(status_code=410, detail="Pago en el local no disponible")
    
    def schedule_delivery(self, order_id: int, scheduled_date: datetime, time_slot: str, notes: str, session: Session) -> Order:
        """
        Programa una entrega (función para administradores).
        
        Args:
            order_id: ID de la orden
            scheduled_date: Fecha programada para la entrega
            time_slot: Horario (mañana, tarde, noche)
            notes: Notas adicionales para el delivery
            session: Sesión de base de datos
            
        Returns:
            Orden actualizada
        """
        try:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Orden no encontrada")
            
            # Validar fecha futura
            if scheduled_date.date() <= datetime.now().date():
                raise HTTPException(
                    status_code=400, 
                    detail="La fecha de entrega debe ser futura"
                )
            
            # Actualizar información de entrega
            order.delivery_scheduled_date = scheduled_date
            order.delivery_time_slot = time_slot
            order.delivery_notes = notes
            order.delivery_status = "scheduled"
            order.verified_by_admin = True
            order.admin_verification_date = datetime.now()
            order.admin_notes = f"Entrega programada para {scheduled_date.strftime('%d/%m/%Y')} en horario {time_slot}"
            
            session.add(order)
            session.commit()
            session.refresh(order)
            
            logger.info(f"Entrega programada para orden {order_id}: {scheduled_date} ({time_slot})")
            
            return order
            
        except Exception as e:
            logger.error(f"Error programando entrega para orden {order_id}: {e}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail="Error programando entrega"
            )
    
    def mark_as_delivered(self, order_id: int, delivery_notes: str, session: Session) -> Order:
        """
        Marca una orden como entregada.
        
        Args:
            order_id: ID de la orden
            delivery_notes: Notas sobre la entrega realizada
            session: Sesión de base de datos
            
        Returns:
            Orden actualizada
        """
        try:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Orden no encontrada")
            
            # Actualizar estado
            order.delivery_status = "delivered"
            order.payment_status = "approved"  # Pago completado
            order.delivery_notes = delivery_notes
            order.admin_notes = f"Entregado el {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            
            session.add(order)
            session.commit()
            session.refresh(order)
            
            logger.info(f"Orden {order_id} marcada como entregada")
            
            return order
            
        except Exception as e:
            logger.error(f"Error marcando orden {order_id} como entregada: {e}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail="Error marcando como entregada"
            )
    
    def get_pending_deliveries(self, session: Session) -> list:
        """
        Obtiene lista de entregas pendientes de programación.
        
        Args:
            session: Sesión de base de datos
            
        Returns:
            Lista de órdenes pendientes de programar entrega
        """
        try:
            pending_orders = session.exec(
                select(Order).where(
                    Order.payment_method == "cash",
                    Order.delivery_status == "pending"
                ).order_by(Order.created_at.desc())
            ).all()
            
            # Incluir datos del customer
            for order in pending_orders:
                order.customer = session.get(Customer, order.customer_id)
            
            return pending_orders
            
        except Exception as e:
            logger.error(f"Error obteniendo entregas pendientes: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error obteniendo entregas pendientes"
            )
    
    def format_full_address(self, customer: Customer) -> str:
        """
        Formatea la dirección completa del cliente.
        
        Args:
            customer: Cliente con datos de dirección
            
        Returns:
            str: Dirección formateada
        """
        address_parts = []
        
        if customer.address:
            address_parts.append(customer.address)
        
        if customer.city:
            address_parts.append(customer.city)
        
        if customer.postal_code:
            address_parts.append(f"CP {customer.postal_code}")
        
        if customer.province:
            address_parts.append(customer.province)
        
        return ", ".join(address_parts) if address_parts else "Dirección no especificada"


# Instancia global del controlador
cash_controller = CashController()
