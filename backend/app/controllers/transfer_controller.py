"""
Controlador para gestión de transferencias bancarias.
Incluye configuración de datos bancarios, verificación manual de pagos
y seguimiento de transferencias recibidas.
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.order import Order
from app.models.customer import Customer
from app.models.payment_config import PaymentConfig

logger = logging.getLogger(__name__)


class TransferController:
    """Controlador para manejar pagos por transferencia bancaria"""
    
    def get_bank_info(self, session: Session) -> Dict[str, Any]:
        """
        Obtiene información bancaria configurada para mostrar a los clientes.
        
        Args:
            session: Sesión de base de datos
            
        Returns:
            Dict con datos bancarios (CBU, alias, titular, etc.)
        """
        try:
            # Buscar configuración bancaria activa
            config = session.exec(
                select(PaymentConfig).where(
                    PaymentConfig.config_type == "bank_account",
                    PaymentConfig.is_active == True
                )
            ).first()
            
            if config:
                bank_data = json.loads(config.config_data)
                logger.info("Datos bancarios obtenidos de configuración")
                return bank_data
            
            # Valores por defecto si no hay configuración
            default_bank_info = {
                "bank_name": "",
                "account_type": "",
                "account_number": "",
                "cbu": "",
                "alias": "SHOWROOMISABELLAA",
                "holder_name": "Priscila Moyano",
                "cuit": "",
                "instructions": "Incluí como referencia el número de pedido y enviá el comprobante por WhatsApp"
            }
            
            logger.warning("Usando datos bancarios por defecto - configurar en PaymentConfig")
            return default_bank_info
            
        except Exception as e:
            logger.error(f"Error obteniendo información bancaria: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error obteniendo información bancaria"
            )
    
    def create_transfer_order(self, order_id: int, session: Session) -> Dict[str, Any]:
        """
        Procesa una orden con método de pago transferencia.
        Configura la orden para verificación manual y retorna datos bancarios.
        
        Args:
            order_id: ID de la orden
            session: Sesión de base de datos
            
        Returns:
            Dict con información de la transferencia y datos bancarios
        """
        try:
            # Obtener la orden
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Orden no encontrada")
            
            # Obtener información bancaria
            bank_info = self.get_bank_info(session)
            
            # Actualizar orden con información de transferencia
            order.bank_account_info = json.dumps(bank_info)
            order.payment_status = "pending_payment"
            order.verification_required = True  # Requiere verificación manual
            
            session.add(order)
            session.commit()
            session.refresh(order)
            
            logger.info(f"Orden {order_id} configurada para transferencia bancaria")
            
            return {
                "order_id": order.id,
                "bank_info": bank_info,
                "total_amount": order.total,
                "reference": f"ORD-{order.id}",
                "instructions": [
                    "Realiza la transferencia con los datos bancarios proporcionados",
                    f"IMPORTANTE: Incluye la referencia ORD-{order.id} en el concepto",
                    "Una vez realizada la transferencia, nuestro equipo la verificará",
                    "Recibirás una notificación cuando se confirme el pago"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error procesando orden de transferencia {order_id}: {e}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail="Error procesando orden de transferencia"
            )
    
    def upload_receipt(self, order_id: int, receipt_url: str, session: Session) -> Dict[str, Any]:
        """
        Registra la subida de un comprobante de transferencia.
        
        Args:
            order_id: ID de la orden
            receipt_url: URL donde se almacenó el comprobante
            session: Sesión de base de datos
            
        Returns:
            Dict con confirmación de subida
        """
        try:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Orden no encontrada")
            
            # Registrar comprobante
            order.transfer_receipt_url = receipt_url
            order.admin_notes = f"Comprobante subido: {receipt_url}"
            
            session.add(order)
            session.commit()
            
            logger.info(f"Comprobante registrado para orden {order_id}: {receipt_url}")
            
            return {
                "status": "receipt_uploaded",
                "order_id": order_id,
                "receipt_url": receipt_url,
                "message": "Comprobante registrado. Nuestro equipo lo verificará pronto."
            }
            
        except Exception as e:
            logger.error(f"Error registrando comprobante para orden {order_id}: {e}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail="Error registrando comprobante"
            )
    
    def verify_transfer(self, order_id: int, verified: bool, admin_notes: str, session: Session) -> Order:
        """
        Verificación manual de transferencia por parte del administrador.
        
        Args:
            order_id: ID de la orden
            verified: True si se verificó la transferencia, False si se rechaza
            admin_notes: Notas del administrador sobre la verificación
            session: Sesión de base de datos
            
        Returns:
            Orden actualizada
        """
        try:
            order = session.get(Order, order_id)
            if not order:
                raise HTTPException(status_code=404, detail="Orden no encontrada")
            
            # Actualizar estado de verificación
            order.transfer_verified = verified
            order.verified_by_admin = verified
            order.admin_verification_date = datetime.now()
            order.admin_notes = admin_notes
            
            # Actualizar estado de pago según verificación
            if verified:
                order.payment_status = "approved"
                logger.info(f"Transferencia APROBADA para orden {order_id}")
            else:
                order.payment_status = "rejected"
                logger.info(f"Transferencia RECHAZADA para orden {order_id}")
            
            session.add(order)
            session.commit()
            session.refresh(order)
            
            return order
            
        except Exception as e:
            logger.error(f"Error verificando transferencia para orden {order_id}: {e}")
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail="Error verificando transferencia"
            )
    
    def get_pending_transfers(self, session: Session) -> list:
        """
        Obtiene lista de transferencias pendientes de verificación.
        
        Args:
            session: Sesión de base de datos
            
        Returns:
            Lista de órdenes pendientes de verificación
        """
        try:
            pending_orders = session.exec(
                select(Order).where(
                    Order.payment_method.in_(("transfer", "bank_transfer")),
                    Order.verification_required == True,
                    Order.verified_by_admin.is_(None)
                ).order_by(Order.created_at.desc())
            ).all()
            
            # Incluir datos del customer
            for order in pending_orders:
                order.customer = session.get(Customer, order.customer_id)
            
            return pending_orders
            
        except Exception as e:
            logger.error(f"Error obteniendo transferencias pendientes: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error obteniendo transferencias pendientes"
            )


# Instancia global del controlador
transfer_controller = TransferController()