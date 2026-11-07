from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from schemas.categoria import CategoryRead

IMAGE_PATTERN = r"^Assets/[A-Za-z0-9_/-]+\.(jpg|jpeg|png|webp)$"


class ProductCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    descripcion: str = Field(min_length=1, max_length=500)
    precio: Decimal = Field(gt=0, le=1_000_000, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0, le=100_000)
    imagen: str = Field(max_length=255, pattern=IMAGE_PATTERN)
    categoria_id: int
    destacado: bool = False


class StockUpdate(BaseModel):
    stock: int = Field(ge=0, le=100_000)


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str
    precio: Decimal
    stock: int
    imagen: str
    destacado: bool
    categoria: CategoryRead
