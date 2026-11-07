from fastapi import APIRouter, HTTPException, status

from db.database import SessionDep
from dependencies.auth import CurrentUser, user_id_of
from schemas.pedido import OrderRead
from services import pedido_service
from services.carrito_service import InsufficientStockError

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrderRead)
def checkout(session: SessionDep, user: CurrentUser):
    try:
        order = pedido_service.checkout(session, user_id_of(user))
    except pedido_service.EmptyCartError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito está vacío")
    except InsufficientStockError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Stock insuficiente para {error.producto}. Disponibles: {error.disponible}",
        )
    return pedido_service.to_read(order)


@router.get("/", response_model=list[OrderRead])
def list_my_orders(session: SessionDep, user: CurrentUser):
    return [pedido_service.to_read(o) for o in pedido_service.list_user_orders(session, user_id_of(user))]


@router.get("/{id}", response_model=OrderRead)
def get_order(id: int, session: SessionDep, user: CurrentUser):
    order = pedido_service.get_order(session, id, user)
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return pedido_service.to_read(order)
