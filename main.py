from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from controller import (
    admin_controller,
    auth_controller,
    carrito_controller,
    categoria_controller,
    pedido_controller,
    producto_controller,
)
from core.config import settings
from db.database import create_db_and_tables


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_db_and_tables()
    yield


ASSETS_DIR = Path(__file__).resolve().parent / "Assets"

app = FastAPI(title="Tienda UIDE", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(auth_controller.router)
app.include_router(categoria_controller.router)
app.include_router(producto_controller.router)
app.include_router(carrito_controller.router)
app.include_router(pedido_controller.router)
app.include_router(admin_controller.router)
app.mount("/Assets", StaticFiles(directory=ASSETS_DIR), name="assets")
