from sqlmodel import Session, select

from core.security import (
    DUMMY_HASH,
    create_access_token,
    hash_password,
    verify_password,
)
from models.usuario import Usuario
from schemas.usuario import Token, UserCreate


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


def get_user_by_email(session: Session, email: str) -> Usuario | None:
    return session.exec(select(Usuario).where(Usuario.email == email.lower())).first()


def register_user(session: Session, data: UserCreate) -> Usuario:
    if get_user_by_email(session, data.email) is not None:
        raise UserAlreadyExistsError
    user = Usuario(
        nombre=data.nombre.strip(),
        email=data.email.lower(),
        password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def authenticate_user(session: Session, email: str, password: str) -> Usuario:
    user = get_user_by_email(session, email)
    if user is None:
        _ = verify_password(password, DUMMY_HASH)
        raise InvalidCredentialsError
    if not verify_password(password, user.password):
        raise InvalidCredentialsError
    return user


def login(session: Session, email: str, password: str) -> Token:
    user = authenticate_user(session, email, password)
    return Token(access_token=create_access_token(str(user.id)))


def get_user_by_id(session: Session, user_id: int) -> Usuario | None:
    return session.get(Usuario, user_id)
