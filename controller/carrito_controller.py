from fastapi import APIRouter, HTTPException, status

from db.database import SessionDep
from dependencies.auth import CurrentUser, user_id_of
from schemas.carrito import CartItemAdd, CartItemUpdate, CartRead
from services import carrito_service

router = APIRouter(prefix="/carrito", tags=["carrito"])


def _http_error(error: Exception) -> HTTPException:
    if isinstance(error, carrito_service.InsufficientStockError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Stock insuficiente para {error.producto}. Disponibles: {error.disponible}",
        )
    if isinstance(error, carrito_service.ProductNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="El producto no está en el carrito"
    )


CART_ERRORS = (
    carrito_service.InsufficientStockError,
    carrito_service.ProductNotFoundError,
    carrito_service.CartItemNotFoundError,
)


@router.get("/", response_model=CartRead)
def get_cart(session: SessionDep, user: CurrentUser):
    return carrito_service.build_cart(session, user_id_of(user))


@router.post("/items", response_model=CartRead)
def add_item(data: CartItemAdd, session: SessionDep, user: CurrentUser):
    try:
        return carrito_service.add_item(session, user_id_of(user), data.producto_id, data.cantidad)
    except CART_ERRORS as error:
        raise _http_error(error)


@router.put("/items/{producto_id}", response_model=CartRead)
def update_item(producto_id: int, data: CartItemUpdate, session: SessionDep, user: CurrentUser):
    try:
        return carrito_service.update_item(session, user_id_of(user), producto_id, data.cantidad)
    except CART_ERRORS as error:
        raise _http_error(error)


@router.delete("/items/{producto_id}", response_model=CartRead)
def remove_item(producto_id: int, session: SessionDep, user: CurrentUser):
    try:
        return carrito_service.remove_item(session, user_id_of(user), producto_id)
    except CART_ERRORS as error:
        raise _http_error(error)


@router.delete("/", response_model=CartRead)
def clear_cart(session: SessionDep, user: CurrentUser):
    return carrito_service.clear_cart(session, user_id_of(user))
