from decimal import Decimal

from pydantic import BaseModel, Field

from schemas.producto import ProductRead


class CartItemAdd(BaseModel):
    producto_id: int
    cantidad: int = Field(default=1, ge=1, le=100)


class CartItemUpdate(BaseModel):
    cantidad: int = Field(ge=1, le=100)


class CartItemRead(BaseModel):
    producto: ProductRead
    cantidad: int
    subtotal: Decimal


class CartRead(BaseModel):
    items: list[CartItemRead]
    cantidad_total: int
    total: Decimal
