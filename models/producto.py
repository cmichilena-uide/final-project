from decimal import Decimal
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.categoria import Categoria
    from models.pedido_item import PedidoItem


class Producto(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=100)
    descripcion: str = Field(max_length=500)
    precio: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    imagen: str = Field(max_length=255)
    activo: bool = Field(default=True, index=True)
    categoria_id: int = Field(foreign_key="categoria.id", index=True)

    categoria: "Categoria" = Relationship(back_populates="productos")
    pedido_items: list["PedidoItem"] = Relationship(back_populates="producto")
