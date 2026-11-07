from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.usuario import Rol


class UserCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: str
    rol: Rol
    creado_en: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
