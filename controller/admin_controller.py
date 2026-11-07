from fastapi import APIRouter, Depends, HTTPException, status

from db.database import SessionDep
from dependencies.auth import get_admin_user
from models.pedido import EstadoPedido
from schemas.pedido import OrderRead, StatusUpdate
from services import pedido_service

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_admin_user)])


@router.get("/pedidos", response_model=list[OrderRead])
def list_orders(session: SessionDep, estado: EstadoPedido | None = None):
    return [pedido_service.to_read(o) for o in pedido_service.list_all_orders(session, estado)]


@router.patch("/pedidos/{id}/estado", response_model=OrderRead)
def change_status(id: int, data: StatusUpdate, session: SessionDep):
    try:
        order = pedido_service.change_status(session, id, data.estado)
    except pedido_service.InvalidStatusChangeError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"No se puede cambiar el estado de {error.actual} a {error.nuevo}",
        )
    if order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pedido no encontrado")
    return pedido_service.to_read(order)
