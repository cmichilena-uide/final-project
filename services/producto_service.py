from collections.abc import Sequence

from sqlmodel import Session, col, func, or_, select

from core.config import BASE_DIR
from models.carrito_item import CarritoItem
from models.categoria import Categoria
from models.producto import Producto
from schemas.producto import ProductCreate

ASSETS_DIR = BASE_DIR / "Assets"
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


class CategoryNotFoundError(Exception):
    pass


class ImageNotFoundError(Exception):
    pass


def list_products(
    session: Session,
    q: str | None = None,
    categoria_id: int | None = None,
    destacado: bool | None = None,
) -> Sequence[Producto]:
    query = select(Producto).where(col(Producto.activo))
    if q:
        pattern = f"%{q.strip()}%"
        query = query.where(
            or_(col(Producto.nombre).ilike(pattern), col(Producto.descripcion).ilike(pattern))
        )
    if categoria_id is not None:
        query = query.where(Producto.categoria_id == categoria_id)
    if destacado is not None:
        query = query.where(Producto.destacado == destacado)
    return session.exec(query.order_by(col(Producto.nombre))).all()


def random_products(session: Session, limit: int) -> Sequence[Producto]:
    return session.exec(
        select(Producto).where(col(Producto.activo)).order_by(func.random()).limit(limit)
    ).all()


def get_product(session: Session, product_id: int) -> Producto | None:
    product = session.get(Producto, product_id)
    if product is None or not product.activo:
        return None
    return product


def list_images() -> list[str]:
    return sorted(
        path.relative_to(BASE_DIR).as_posix()
        for path in ASSETS_DIR.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


def _validate(session: Session, data: ProductCreate) -> None:
    if session.get(Categoria, data.categoria_id) is None:
        raise CategoryNotFoundError
    if not (BASE_DIR / data.imagen).is_file():
        raise ImageNotFoundError


def _apply(product: Producto, data: ProductCreate) -> Producto:
    product.nombre = data.nombre.strip()
    product.descripcion = data.descripcion.strip()
    product.precio = data.precio
    product.stock = data.stock
    product.imagen = data.imagen
    product.categoria_id = data.categoria_id
    product.destacado = data.destacado
    return product


def create_product(session: Session, data: ProductCreate) -> Producto:
    _validate(session, data)
    product = Producto(
        nombre=data.nombre.strip(),
        descripcion=data.descripcion.strip(),
        precio=data.precio,
        stock=data.stock,
        imagen=data.imagen,
        categoria_id=data.categoria_id,
        destacado=data.destacado,
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def update_product(session: Session, product_id: int, data: ProductCreate) -> Producto | None:
    product = get_product(session, product_id)
    if product is None:
        return None
    _validate(session, data)
    session.add(_apply(product, data))
    session.commit()
    session.refresh(product)
    return product


def update_stock(session: Session, product_id: int, stock: int) -> Producto | None:
    product = get_product(session, product_id)
    if product is None:
        return None
    product.stock = stock
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def delete_product(session: Session, product_id: int) -> bool:
    product = get_product(session, product_id)
    if product is None:
        return False
    product.activo = False
    session.add(product)
    for item in session.exec(select(CarritoItem).where(CarritoItem.producto_id == product_id)).all():
        session.delete(item)
    session.commit()
    return True
