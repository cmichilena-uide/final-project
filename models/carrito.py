from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.carrito_item import CarritoItem
    from models.usuario import Usuario


class Carrito(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", unique=True)

    usuario: "Usuario" = Relationship(back_populates="carrito")
    items: list["CarritoItem"] = Relationship(
        back_populates="carrito", cascade_delete=True
    )
