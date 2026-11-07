from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from db.database import SessionDep
from dependencies.auth import AdminUser
from models.producto import Producto
from schemas.producto import ProductCreate, ProductRead, StockUpdate
from services import producto_service

router = APIRouter(prefix="/productos", tags=["productos"])

NOT_FOUND = "Producto no encontrado"


def _found(product: Producto | None) -> Producto:
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return product


def _invalid(error: Exception) -> HTTPException:
    if isinstance(error, producto_service.CategoryNotFoundError):
        detail = "La categoría no existe"
    else:
        detail = "La imagen no existe en la carpeta Assets"
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


@router.get("/", response_model=list[ProductRead])
def list_products(
    session: SessionDep,
    q: Annotated[str | None, Query(max_length=100)] = None,
    categoria_id: int | None = None,
    destacado: bool | None = None,
):
    return producto_service.list_products(session, q, categoria_id, destacado)


@router.get("/aleatorios", response_model=list[ProductRead])
def random_products(session: SessionDep, limite: Annotated[int, Query(ge=1, le=24)] = 8):
    return producto_service.random_products(session, limite)


@router.get("/imagenes", response_model=list[str])
def list_images(_admin: AdminUser):
    return producto_service.list_images()


@router.get("/{id}", response_model=ProductRead)
def get_product(id: int, session: SessionDep):
    return _found(producto_service.get_product(session, id))


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductRead)
def create_product(data: ProductCreate, session: SessionDep, _admin: AdminUser):
    try:
        return producto_service.create_product(session, data)
    except (producto_service.CategoryNotFoundError, producto_service.ImageNotFoundError) as error:
        raise _invalid(error)


@router.put("/{id}", response_model=ProductRead)
def update_product(id: int, data: ProductCreate, session: SessionDep, _admin: AdminUser):
    try:
        return _found(producto_service.update_product(session, id, data))
    except (producto_service.CategoryNotFoundError, producto_service.ImageNotFoundError) as error:
        raise _invalid(error)


@router.patch("/{id}/stock", response_model=ProductRead)
def update_stock(id: int, data: StockUpdate, session: SessionDep, _admin: AdminUser):
    return _found(producto_service.update_stock(session, id, data.stock))


@router.delete("/{id}")
def delete_product(id: int, session: SessionDep, _admin: AdminUser):
    if not producto_service.delete_product(session, id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return {"message": "Producto eliminado"}
