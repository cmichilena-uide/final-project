from fastapi import APIRouter, HTTPException, status

from db.database import SessionDep
from dependencies.auth import AdminUser
from schemas.categoria import CategoryCreate, CategoryRead
from schemas.producto import ProductRead
from services import categoria_service, producto_service

router = APIRouter(prefix="/categorias", tags=["categorias"])

NOT_FOUND = "Categoría no encontrada"
DUPLICATED = "Ya existe una categoría con ese nombre"


@router.get("/", response_model=list[CategoryRead])
def list_categories(session: SessionDep):
    return categoria_service.list_categories(session)


@router.get("/{id}", response_model=CategoryRead)
def get_category(id: int, session: SessionDep):
    category = categoria_service.get_category(session, id)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return category


@router.get("/{id}/productos", response_model=list[ProductRead])
def list_category_products(id: int, session: SessionDep):
    if categoria_service.get_category(session, id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return producto_service.list_products(session, categoria_id=id)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CategoryRead)
def create_category(data: CategoryCreate, session: SessionDep, _admin: AdminUser):
    try:
        return categoria_service.create_category(session, data)
    except categoria_service.CategoryAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DUPLICATED)


@router.put("/{id}", response_model=CategoryRead)
def update_category(id: int, data: CategoryCreate, session: SessionDep, _admin: AdminUser):
    try:
        category = categoria_service.update_category(session, id, data)
    except categoria_service.CategoryAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=DUPLICATED)
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return category


@router.delete("/{id}")
def delete_category(id: int, session: SessionDep, _admin: AdminUser):
    try:
        deleted = categoria_service.delete_category(session, id)
    except categoria_service.CategoryInUseError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: la categoría tiene productos",
        )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND)
    return {"message": "Categoría eliminada"}
