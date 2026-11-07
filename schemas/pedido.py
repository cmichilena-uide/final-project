from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from models.pedido import EstadoPedido


class OrderItemRead(BaseModel):
    producto_id: int
    nombre_producto: str
    imagen: str
    precio_unitario: Decimal
    cantidad: int
    subtotal: Decimal


class OrderCustomer(BaseModel):
    id: int
    nombre: str
    email: str


class OrderRead(BaseModel):
    id: int
    fecha: datetime
    estado: EstadoPedido
    total: Decimal
    cantidad_total: int
    cliente: OrderCustomer
    items: list[OrderItemRead]


class StatusUpdate(BaseModel):
    estado: EstadoPedido
