from decimal import Decimal

from sqlmodel import Session, select

from core.config import settings
from core.security import hash_password
from db.database import create_db_and_tables, engine
from models import Categoria, Producto, Rol, Usuario

DEMO_EMAIL = "cliente@tienda.ec"
DEMO_PASSWORD = "Cliente12345"

CATEGORIES = {
    "Laptops": "Portátiles para estudio, oficina y juegos.",
    "Smartphones": "Teléfonos inteligentes de las principales marcas.",
    "Audio": "Audífonos, parlantes y barras de sonido.",
    "Accesorios": "Teclados, mouse, cargadores y cámaras web.",
    "Monitores": "Pantallas para trabajo, diseño y gaming.",
    "Gaming": "Consolas, controles y periféricos para jugar.",
}

PRODUCTS = [
    ("Laptops", "MacBook Air 13", "Portátil ultradelgada con chip Apple, 8 GB de RAM y 256 GB SSD. Ideal para estudiar y trabajar.", "1099.00", 8, "laptops/macbook-air", True),
    ("Laptops", "Lenovo ThinkPad", "Portátil empresarial resistente con teclado cómodo y TrackPoint.", "849.99", 12, "laptops/thinkpad", False),
    ("Laptops", "MSI Laptop Gamer", "Laptop gamer con tarjeta gráfica dedicada y pantalla de 144 Hz.", "1349.00", 5, "laptops/laptop-gamer-msi", True),
    ("Laptops", "Samsung Chromebook", "Chromebook liviana con Chrome OS, perfecta para clases en línea.", "299.90", 15, "laptops/chromebook", False),
    ("Smartphones", "iPhone 15", "Pantalla Super Retina de 6,1 pulgadas, cámara de 48 MP y USB-C.", "999.00", 10, "smartphones/iphone-15", True),
    ("Smartphones", "Samsung Galaxy S23", "Smartphone Android con cámara triple y procesador Snapdragon.", "849.00", 9, "smartphones/galaxy-s23", False),
    ("Smartphones", "Google Pixel 8", "La mejor experiencia Android pura con fotos increíbles gracias a la IA.", "699.00", 2, "smartphones/pixel-8", False),
    ("Smartphones", "Xiaomi Redmi Note 10 Pro", "Gran batería, pantalla AMOLED de 120 Hz y cámara de 108 MP a buen precio.", "279.99", 20, "smartphones/redmi-note-10-pro", False),
    ("Audio", "Bose QuietComfort 25", "Audífonos con cancelación de ruido y estuche de transporte.", "199.00", 7, "audio/audifonos-bose-qc25", True),
    ("Audio", "Samsung Galaxy Buds2 Pro", "Audífonos inalámbricos in-ear con sonido Hi-Fi de 24 bits.", "179.99", 14, "audio/galaxy-buds2-pro", False),
    ("Audio", "Parlante JBL Flip", "Parlante bluetooth portátil resistente al agua con 12 horas de batería.", "119.00", 18, "audio/parlante-jbl-flip", False),
    ("Audio", "Barra de sonido Samsung", "Barra de sonido 2.1 con subwoofer integrado para tu televisor.", "159.90", 6, "audio/barra-sonido-samsung", False),
    ("Accesorios", "Teclado mecánico RGB", "Teclado mecánico con iluminación RGB y switches táctiles.", "69.99", 25, "accesorios/teclado-mecanico", False),
    ("Accesorios", "Mouse inalámbrico", "Mouse ergonómico inalámbrico con receptor USB y 1600 DPI.", "19.99", 40, "accesorios/mouse-inalambrico", False),
    ("Accesorios", "Power bank Anker", "Batería externa de 10000 mAh con carga rápida para tu celular.", "34.99", 30, "accesorios/power-bank", False),
    ("Accesorios", "Cámara web Logitech C922", "Webcam Full HD 1080p ideal para clases virtuales y streaming.", "89.00", 11, "accesorios/webcam", True),
    ("Monitores", "Monitor curvo ASUS 21:9", "Monitor curvo ultra panorámico para una experiencia inmersiva.", "449.00", 4, "monitores/monitor-curvo", False),
    ("Monitores", "Monitor EIZO Foris 24", "Monitor gamer de 24 pulgadas a 120 Hz con colores precisos.", "329.00", 6, "monitores/monitor-gamer-eizo", False),
    ("Monitores", "Monitor LG 19", "Monitor LCD sencillo y económico para la oficina o el hogar.", "109.99", 16, "monitores/monitor-lg", False),
    ("Monitores", "Monitor Dell UltraWide 34", "Monitor curvo de 34 pulgadas WQHD, perfecto para productividad.", "599.00", 3, "monitores/monitor-ultrawide-34", True),
    ("Gaming", "PlayStation 5", "Consola de nueva generación con control DualSense incluido.", "549.00", 0, "gaming/playstation-5", True),
    ("Gaming", "Control DualSense", "Control inalámbrico para PS5 con retroalimentación háptica.", "74.99", 13, "gaming/control-dualsense", False),
    ("Gaming", "Nintendo Switch", "Consola híbrida para jugar en casa o donde quieras.", "329.00", 8, "gaming/nintendo-switch", False),
    ("Gaming", "Control Xbox inalámbrico", "Control para Xbox y PC con conexión bluetooth.", "59.99", 17, "gaming/control-xbox", False),
    ("Gaming", "Audífonos gamer Logitech G35", "Audífonos gamer con sonido envolvente 7.1 y micrófono.", "89.99", 9, "gaming/audifonos-gamer", False),
]


def seed_user(session: Session, nombre: str, email: str, password: str, rol: Rol) -> None:
    exists = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if exists is None:
        session.add(
            Usuario(nombre=nombre, email=email, password=hash_password(password), rol=rol)
        )


def seed_categories(session: Session) -> dict[str, Categoria]:
    categories: dict[str, Categoria] = {}
    for nombre, descripcion in CATEGORIES.items():
        category = session.exec(select(Categoria).where(Categoria.nombre == nombre)).first()
        if category is None:
            category = Categoria(nombre=nombre, descripcion=descripcion)
            session.add(category)
        categories[nombre] = category
    session.flush()
    return categories


def seed_products(session: Session, categories: dict[str, Categoria]) -> None:
    for categoria, nombre, descripcion, precio, stock, slug, destacado in PRODUCTS:
        imagen = f"Assets/{slug}.jpg"
        exists = session.exec(select(Producto).where(Producto.imagen == imagen)).first()
        category_id = categories[categoria].id
        if exists is None and category_id is not None:
            session.add(
                Producto(
                    nombre=nombre,
                    descripcion=descripcion,
                    precio=Decimal(precio),
                    stock=stock,
                    imagen=imagen,
                    destacado=destacado,
                    categoria_id=category_id,
                )
            )


def run() -> None:
    create_db_and_tables()
    with Session(engine) as session:
        seed_user(session, "Administrador", settings.admin_email.lower(), settings.admin_password, Rol.admin)
        seed_user(session, "Cliente Demo", DEMO_EMAIL, DEMO_PASSWORD, Rol.cliente)
        seed_products(session, seed_categories(session))
        session.commit()


if __name__ == "__main__":
    run()
