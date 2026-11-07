from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.pedido_item import PedidoItem
    from models.usuario import Usuario


class EstadoPedido(StrEnum):
    pendiente = "pendiente"
    procesando = "procesando"
    enviado = "enviado"
    entregado = "entregado"


class Pedido(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    fecha: datetime = Field(default_factory=lambda: datetime.now(UTC))
    estado: EstadoPedido = Field(default=EstadoPedido.pendiente, index=True)
    total: Decimal = Field(max_digits=12, decimal_places=2)

    usuario: "Usuario" = Relationship(back_populates="pedidos")
    items: list["PedidoItem"] = Relationship(back_populates="pedido")
