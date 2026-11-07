from collections.abc import Sequence
from decimal import Decimal

from sqlmodel import Session, col, select

from models.carrito import Carrito
from models.carrito_item import CarritoItem
from models.pedido import EstadoPedido, Pedido
from models.pedido_item import PedidoItem
from models.producto import Producto
from models.usuario import Rol, Usuario
from schemas.pedido import OrderCustomer, OrderItemRead, OrderRead
from services.carrito_service import InsufficientStockError

NEXT_STATUS = {
    EstadoPedido.pendiente: EstadoPedido.procesando,
    EstadoPedido.procesando: EstadoPedido.enviado,
    EstadoPedido.enviado: EstadoPedido.entregado,
}


class EmptyCartError(Exception):
    pass


class InvalidStatusChangeError(Exception):
    def __init__(self, actual: EstadoPedido, nuevo: EstadoPedido) -> None:
        super().__init__(actual)
        self.actual: EstadoPedido = actual
        self.nuevo: EstadoPedido = nuevo


def to_read(order: Pedido) -> OrderRead:
    items = [
        OrderItemRead(
            producto_id=item.producto_id,
            nombre_producto=item.nombre_producto,
            imagen=item.producto.imagen,
            precio_unitario=item.precio_unitario,
            cantidad=item.cantidad,
            subtotal=item.subtotal,
        )
        for item in sorted(order.items, key=lambda line: line.id or 0)
    ]
    customer: Usuario = order.usuario
    return OrderRead(
        id=order.id or 0,
        fecha=order.fecha,
        estado=order.estado,
        total=order.total,
        cantidad_total=sum(item.cantidad for item in items),
        cliente=OrderCustomer(id=customer.id or 0, nombre=customer.nombre, email=customer.email),
        items=items,
    )


def checkout(session: Session, user_id: int) -> Pedido:
    rows = session.exec(
        select(CarritoItem, Producto)
        .join(Carrito, col(Carrito.id) == CarritoItem.carrito_id)
        .where(Carrito.usuario_id == user_id, CarritoItem.producto_id == Producto.id)
        .where(col(Producto.activo))
        .order_by(col(CarritoItem.id))
    ).all()
    if not rows:
        raise EmptyCartError
    for item, product in rows:
        if item.cantidad > product.stock:
            raise InsufficientStockError(product.nombre, product.stock)
    order = Pedido(usuario_id=user_id, total=Decimal("0.00"))
    session.add(order)
    session.flush()
    if order.id is None:
        raise RuntimeError("El pedido no recibió un id")
    total = Decimal("0.00")
    for item, product in rows:
        subtotal = product.precio * item.cantidad
        total += subtotal
        session.add(
            PedidoItem(
                pedido_id=order.id,
                producto_id=item.producto_id,
                nombre_producto=product.nombre,
                precio_unitario=product.precio,
                cantidad=item.cantidad,
                subtotal=subtotal,
            )
        )
        product.stock -= item.cantidad
        session.add(product)
        session.delete(item)
    order.total = total
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


def list_user_orders(session: Session, user_id: int) -> Sequence[Pedido]:
    return session.exec(
        select(Pedido).where(Pedido.usuario_id == user_id).order_by(col(Pedido.id).desc())
    ).all()


def get_order(session: Session, order_id: int, user: Usuario) -> Pedido | None:
    order = session.get(Pedido, order_id)
    if order is None:
        return None
    if user.rol != Rol.admin and order.usuario_id != user.id:
        return None
    return order


def list_all_orders(session: Session, estado: EstadoPedido | None) -> Sequence[Pedido]:
    query = select(Pedido)
    if estado is not None:
        query = query.where(Pedido.estado == estado)
    return session.exec(query.order_by(col(Pedido.id).desc())).all()


def change_status(session: Session, order_id: int, nuevo: EstadoPedido) -> Pedido | None:
    order = session.get(Pedido, order_id)
    if order is None:
        return None
    if NEXT_STATUS.get(order.estado) != nuevo:
        raise InvalidStatusChangeError(order.estado, nuevo)
    order.estado = nuevo
    session.add(order)
    session.commit()
    session.refresh(order)
    return order
