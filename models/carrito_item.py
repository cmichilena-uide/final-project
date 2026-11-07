from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel, UniqueConstraint

if TYPE_CHECKING:
    from models.carrito import Carrito
    from models.producto import Producto


class CarritoItem(SQLModel, table=True):
    __table_args__ = (UniqueConstraint("carrito_id", "producto_id"),)

    id: int | None = Field(default=None, primary_key=True)
    carrito_id: int = Field(foreign_key="carrito.id", index=True, ondelete="CASCADE")
    producto_id: int = Field(foreign_key="producto.id", index=True)
    cantidad: int = Field(gt=0)

    carrito: "Carrito" = Relationship(back_populates="items")
    producto: "Producto" = Relationship()
