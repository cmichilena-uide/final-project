import { apiFetch } from "./api.js";
import { loadUser, logout } from "./auth.js";
import { el } from "./ui.js";

const navLink = (href, text, active, extra = null) =>
  el(
    "li",
    { class: "nav_item" },
    el(
      "a",
      { class: href === active ? "nav_link active" : "nav_link", attrs: { href } },
      text,
      extra,
    ),
  );

const cartBadge = el("span", { class: "cart_badge", text: "0", attrs: { hidden: true } });

export const refreshCartCount = async () => {
  try {
    const cart = await apiFetch("/carrito/", { auth: true, redirectOn401: false });
    setCartCount(cart.cantidad_total);
  } catch {
    setCartCount(0);
  }
};

export const setCartCount = (count) => {
  cartBadge.textContent = String(count);
  cartBadge.hidden = count === 0;
};

const userArea = (user) => {
  if (user === null) {
    return el(
      "div",
      { class: "user_area" },
      el("a", { class: "button button_light", attrs: { href: "login.html" }, text: "Ingresar" }),
      el("a", { class: "button", attrs: { href: "registro.html" }, text: "Registrarse" }),
    );
  }
  return el(
    "div",
    { class: "user_area" },
    el("span", { class: "user_name", text: "Hola, " + user.nombre }),
    user.rol === "admin" ? el("span", { class: "role_tag", text: "Admin" }) : null,
    el("button", { class: "button button_light", attrs: { type: "button" }, text: "Cerrar sesión", on: { click: logout } }),
  );
};

const buildHeader = (user, active) => {
  const links = el(
    "ul",
    { class: "nav_list" },
    navLink("index.html", "Inicio", active),
    navLink("catalogo.html", "Catálogo", active),
    navLink("carrito.html", "Carrito ", active, cartBadge),
    user !== null ? navLink("pedidos.html", "Mis pedidos", active) : null,
    user !== null && user.rol === "admin" ? navLink("admin.html", "Administrar", active) : null,
  );
  return el(
    "nav",
    { class: "main_nav" },
    el("a", { class: "brand", attrs: { href: "index.html" }, text: "TecnoTienda" }),
    links,
    userArea(user),
  );
};

const buildFooter = () =>
  el(
    "div",
    { class: "footer_content" },
    el("p", { text: "TecnoTienda - Proyecto final Fundamentos de Back End y Front End" }),
    el("p", { class: "footer_small", text: "FastAPI + SQLModel + SQLite · UIDE 2026" }),
  );

export const initLayout = async (active) => {
  const user = await loadUser();
  document.querySelector("#site_header").replaceChildren(buildHeader(user, active));
  document.querySelector("#site_footer").replaceChildren(buildFooter());
  if (user !== null) {
    await refreshCartCount();
  }
  return user;
};
