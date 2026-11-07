from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=60)
    descripcion: str = Field(min_length=1, max_length=300)


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str
