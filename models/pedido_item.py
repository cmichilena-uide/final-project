from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.pedido import Pedido
    from models.producto import Producto


class PedidoItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedido.id", index=True)
    producto_id: int = Field(foreign_key="producto.id", index=True)
    nombre_producto: str = Field(max_length=100)
    precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)
    cantidad: int = Field(gt=0)
    subtotal: Decimal = Field(max_digits=12, decimal_places=2)

    pedido: "Pedido" = Relationship(back_populates="items")
    producto: "Producto" = Relationship(back_populates="pedido_items")
