from collections.abc import Sequence

from sqlmodel import Session, col, func, select

from models.categoria import Categoria
from models.producto import Producto
from schemas.categoria import CategoryCreate


class CategoryAlreadyExistsError(Exception):
    pass


class CategoryInUseError(Exception):
    pass


def _name_taken(session: Session, nombre: str, exclude_id: int | None = None) -> bool:
    query = select(Categoria).where(func.lower(Categoria.nombre) == nombre.lower())
    if exclude_id is not None:
        query = query.where(Categoria.id != exclude_id)
    return session.exec(query).first() is not None


def list_categories(session: Session) -> Sequence[Categoria]:
    return session.exec(select(Categoria).order_by(col(Categoria.nombre))).all()


def get_category(session: Session, category_id: int) -> Categoria | None:
    return session.get(Categoria, category_id)


def create_category(session: Session, data: CategoryCreate) -> Categoria:
    nombre = data.nombre.strip()
    if _name_taken(session, nombre):
        raise CategoryAlreadyExistsError
    category = Categoria(nombre=nombre, descripcion=data.descripcion.strip())
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def update_category(
    session: Session, category_id: int, data: CategoryCreate
) -> Categoria | None:
    category = session.get(Categoria, category_id)
    if category is None:
        return None
    nombre = data.nombre.strip()
    if _name_taken(session, nombre, exclude_id=category_id):
        raise CategoryAlreadyExistsError
    category.nombre = nombre
    category.descripcion = data.descripcion.strip()
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def delete_category(session: Session, category_id: int) -> bool:
    category = session.get(Categoria, category_id)
    if category is None:
        return False
    in_use = session.exec(
        select(Producto).where(Producto.categoria_id == category_id)
    ).first()
    if in_use is not None:
        raise CategoryInUseError
    session.delete(category)
    session.commit()
    return True
