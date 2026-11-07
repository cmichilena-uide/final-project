from decimal import Decimal

from sqlmodel import Session, col, select

from models.carrito import Carrito
from models.carrito_item import CarritoItem
from models.producto import Producto
from schemas.carrito import CartItemRead, CartRead
from schemas.producto import ProductRead


class ProductNotFoundError(Exception):
    pass


class CartItemNotFoundError(Exception):
    pass


class InsufficientStockError(Exception):
    def __init__(self, producto: str, disponible: int) -> None:
        super().__init__(producto)
        self.producto: str = producto
        self.disponible: int = disponible


def get_or_create_cart(session: Session, user_id: int) -> Carrito:
    cart = session.exec(select(Carrito).where(Carrito.usuario_id == user_id)).first()
    if cart is None:
        cart = Carrito(usuario_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart


def _cart_id(cart: Carrito) -> int:
    if cart.id is None:
        raise CartItemNotFoundError
    return cart.id


def _active_product(session: Session, product_id: int) -> Producto:
    product = session.get(Producto, product_id)
    if product is None or not product.activo:
        raise ProductNotFoundError
    return product


def _find_item(session: Session, cart_id: int, product_id: int) -> CarritoItem | None:
    return session.exec(
        select(CarritoItem).where(
            CarritoItem.carrito_id == cart_id, CarritoItem.producto_id == product_id
        )
    ).first()


def _ensure_stock(product: Producto, cantidad: int) -> None:
    if cantidad > product.stock:
        raise InsufficientStockError(product.nombre, product.stock)


def build_cart(session: Session, user_id: int) -> CartRead:
    cart_id = _cart_id(get_or_create_cart(session, user_id))
    rows = session.exec(
        select(CarritoItem, Producto)
        .where(CarritoItem.carrito_id == cart_id, CarritoItem.producto_id == Producto.id)
        .where(col(Producto.activo))
        .order_by(col(CarritoItem.id))
    ).all()
    items = [
        CartItemRead(
            producto=ProductRead.model_validate(product),
            cantidad=item.cantidad,
            subtotal=product.precio * item.cantidad,
        )
        for item, product in rows
    ]
    return CartRead(
        items=items,
        cantidad_total=sum(item.cantidad for item in items),
        total=sum((item.subtotal for item in items), Decimal("0.00")),
    )


def add_item(session: Session, user_id: int, product_id: int, cantidad: int) -> CartRead:
    product = _active_product(session, product_id)
    cart_id = _cart_id(get_or_create_cart(session, user_id))
    item = _find_item(session, cart_id, product_id)
    nueva = cantidad + (item.cantidad if item is not None else 0)
    _ensure_stock(product, nueva)
    if item is None:
        item = CarritoItem(carrito_id=cart_id, producto_id=product_id, cantidad=nueva)
    else:
        item.cantidad = nueva
    session.add(item)
    session.commit()
    return build_cart(session, user_id)


def update_item(session: Session, user_id: int, product_id: int, cantidad: int) -> CartRead:
    cart_id = _cart_id(get_or_create_cart(session, user_id))
    item = _find_item(session, cart_id, product_id)
    if item is None:
        raise CartItemNotFoundError
    _ensure_stock(_active_product(session, product_id), cantidad)
    item.cantidad = cantidad
    session.add(item)
    session.commit()
    return build_cart(session, user_id)


def remove_item(session: Session, user_id: int, product_id: int) -> CartRead:
    cart_id = _cart_id(get_or_create_cart(session, user_id))
    item = _find_item(session, cart_id, product_id)
    if item is None:
        raise CartItemNotFoundError
    session.delete(item)
    session.commit()
    return build_cart(session, user_id)


def clear_cart(session: Session, user_id: int) -> CartRead:
    cart_id = _cart_id(get_or_create_cart(session, user_id))
    for item in session.exec(select(CarritoItem).where(CarritoItem.carrito_id == cart_id)).all():
        session.delete(item)
    session.commit()
    return build_cart(session, user_id)
