import { apiFetch } from "./api.js";
import { requireAuth } from "./auth.js";
import { initLayout, setCartCount } from "./layout.js";
import { el, formatPrice, productImage, showMessage } from "./ui.js";

const itemsBox = document.querySelector("#cart_items");
const summary = document.querySelector("#cart_summary");
const pageMessage = document.querySelector("#page_message");
const checkoutButton = document.querySelector("#checkout_button");
const clearButton = document.querySelector("#clear_button");

const run = async (request, successText = "") => {
  try {
    const cart = await request();
    renderCart(cart);
    showMessage(pageMessage, successText, "success");
  } catch (error) {
    showMessage(pageMessage, error.message, "error");
    await loadCart();
  }
};

const updateQuantity = (item, cantidad) =>
  run(() =>
    apiFetch("/carrito/items/" + item.producto.id, {
      method: "PUT",
      auth: true,
      body: { cantidad },
    }),
  );

const removeItem = (item) =>
  run(
    () => apiFetch("/carrito/items/" + item.producto.id, { method: "DELETE", auth: true }),
    item.producto.nombre + " se eliminó del carrito",
  );

const quantityInput = (item) =>
  el("input", {
    class: "cart_quantity",
    attrs: {
      type: "number",
      min: 1,
      max: item.producto.stock,
      value: item.cantidad,
      "aria-label": "Cantidad de " + item.producto.nombre,
    },
    on: {
      change: (event) => {
        const cantidad = Number(event.target.value);
        if (!Number.isInteger(cantidad) || cantidad < 1) {
          showMessage(pageMessage, "Ingrese una cantidad válida", "error");
          event.target.value = String(item.cantidad);
          return;
        }
        updateQuantity(item, cantidad);
      },
    },
  });

const cartRow = (item) => {
  const link = "producto.html?id=" + item.producto.id;
  return el(
    "article",
    { class: "cart_item" },
    el("a", { attrs: { href: link } }, productImage(item.producto, "cart_image")),
    el(
      "div",
      { class: "cart_info" },
      el("h3", {}, el("a", { attrs: { href: link }, text: item.producto.nombre })),
      el("p", { class: "cart_unit", text: formatPrice(item.producto.precio) + " c/u" }),
      el("p", { class: "cart_stock", text: "Stock disponible: " + item.producto.stock }),
    ),
    el(
      "div",
      { class: "cart_controls" },
      quantityInput(item),
      el("span", { class: "cart_subtotal", text: formatPrice(item.subtotal) }),
      el("button", {
        class: "button_danger",
        text: "Eliminar",
        attrs: { type: "button" },
        on: { click: () => removeItem(item) },
      }),
    ),
  );
};

const renderCart = (cart) => {
  setCartCount(cart.cantidad_total);
  if (cart.items.length === 0) {
    summary.hidden = true;
    itemsBox.replaceChildren(
      el(
        "div",
        { class: "empty_state" },
        el("p", { text: "Tu carrito está vacío" }),
        el("a", { class: "button", attrs: { href: "catalogo.html" }, text: "Ir al catálogo" }),
      ),
    );
    return;
  }
  itemsBox.replaceChildren(...cart.items.map(cartRow));
  document.querySelector("#summary_count").textContent = String(cart.cantidad_total);
  document.querySelector("#summary_total").textContent = formatPrice(cart.total);
  summary.hidden = false;
};

const loadCart = async () => {
  try {
    renderCart(await apiFetch("/carrito/", { auth: true }));
  } catch (error) {
    showMessage(pageMessage, error.message, "error");
  }
};

checkoutButton.addEventListener("click", async () => {
  checkoutButton.disabled = true;
  try {
    const order = await apiFetch("/pedidos/", { method: "POST", auth: true });
    setCartCount(0);
    window.location.href = "pedidos.html?id=" + order.id + "&nuevo=1";
  } catch (error) {
    showMessage(pageMessage, error.message, "error");
    checkoutButton.disabled = false;
    await loadCart();
  }
});

clearButton.addEventListener("click", () => {
  if (window.confirm("¿Seguro que deseas vaciar el carrito?")) {
    run(() => apiFetch("/carrito/", { method: "DELETE", auth: true }), "Carrito vaciado");
  }
});

const user = await initLayout("carrito.html");
if (requireAuth(user)) {
  await loadCart();
}
