from datetime import UTC, datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from models.carrito import Carrito
    from models.pedido import Pedido


class Rol(StrEnum):
    cliente = "cliente"
    admin = "admin"


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=50)
    email: str = Field(unique=True, index=True, max_length=255)
    password: str
    rol: Rol = Field(default=Rol.cliente)
    creado_en: datetime = Field(default_factory=lambda: datetime.now(UTC))

    carrito: Optional["Carrito"] = Relationship(back_populates="usuario")
    pedidos: list["Pedido"] = Relationship(back_populates="usuario")
