# TecnoTienda

Proyecto final de Fundamentos de Back End y Front End (UIDE). Tienda virtual de tecnología con catálogo, carrito de compras, pedidos y panel de administración.

## Tecnologías

- **Backend:** FastAPI, SQLModel, SQLite, JWT (PyJWT) y contraseñas con Argon2 (pwdlib).
- **Frontend:** HTML semántico, CSS (Grid y Flexbox, mobile first) y JavaScript con `fetch`.

## Estructura

```
controller/    rutas de la API
services/      lógica de negocio
models/        tablas de SQLModel
schemas/       validación de entrada y salida
dependencies/  autenticación y permisos
core/          configuración y seguridad
db/            conexión y datos de ejemplo (seed)
Assets/        imágenes de los productos
frontend/      páginas de la tienda
tienda.db      base de datos SQLite con datos de ejemplo
```

## Cómo ejecutar

Requiere Python 3.12 o superior.

```bash
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # cambiar SECRET_KEY por una clave larga
fastapi dev main.py
```

La API queda en `http://localhost:8000` y la documentación en `http://localhost:8000/docs`.

El frontend se abre con Live Server desde la carpeta `frontend/` en el puerto 5500, o con:

```bash
cd frontend
python -m http.server 5500
```

Para volver a los datos iniciales, detener el servidor, borrar `tienda.db` y ejecutar `python -m db.seed`.

## Usuarios de prueba

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@tienda.ec | Admin12345 |
| Cliente | cliente@tienda.ec | Cliente12345 |

## Endpoints principales

| Método | Ruta | Acceso |
|---|---|---|
| POST | `/auth/register`, `/auth/login` | Público |
| GET | `/auth/me` | Usuario |
| GET | `/productos/?q=&categoria_id=&destacado=` | Público |
| GET | `/productos/aleatorios`, `/productos/{id}` | Público |
| POST, PUT, DELETE | `/productos/`, `/productos/{id}` | Administrador |
| PATCH | `/productos/{id}/stock` | Administrador |
| GET | `/categorias/`, `/categorias/{id}/productos` | Público |
| POST, PUT, DELETE | `/categorias/`, `/categorias/{id}` | Administrador |
| GET, DELETE | `/carrito/` | Usuario |
| POST, PUT, DELETE | `/carrito/items`, `/carrito/items/{producto_id}` | Usuario |
| POST, GET | `/pedidos/`, `/pedidos/{id}` | Usuario |
| GET, PATCH | `/admin/pedidos`, `/admin/pedidos/{id}/estado` | Administrador |

Los pedidos avanzan en orden: pendiente → procesando → enviado → entregado. El pago es simulado.

## Imágenes

Las imágenes provienen de Wikimedia Commons. Autores y licencias en `Assets/CREDITOS.md`.
