import { apiFetch, assetUrl } from "./api.js";
import { requireAuth } from "./auth.js";
import { estadoBadge, estadoSteps } from "./estado.js";
import { initLayout } from "./layout.js";
import { el, formatDate, formatPrice, showMessage } from "./ui.js";

const listBox = document.querySelector("#order_list");
const detailBox = document.querySelector("#order_detail");
const pageMessage = document.querySelector("#page_message");

const params = new URLSearchParams(window.location.search);
let selectedId = params.get("id");

const orderCard = (order) =>
  el(
    "article",
    { class: String(order.id) === selectedId ? "order_card selected" : "order_card" },
    el(
      "div",
      { class: "order_card_header" },
      el("h3", { text: "Pedido #" + order.id }),
      estadoBadge(order.estado),
    ),
    el("p", { class: "order_date", text: formatDate(order.fecha) }),
    el(
      "div",
      { class: "order_card_footer" },
      el("span", { text: order.cantidad_total + (order.cantidad_total === 1 ? " producto" : " productos") }),
      el("span", { class: "price", text: formatPrice(order.total) }),
    ),
    el("button", {
      class: "button_light",
      text: "Ver detalle",
      attrs: { type: "button" },
      on: { click: () => selectOrder(order.id) },
    }),
  );

const detailLine = (item) =>
  el(
    "li",
    { class: "order_line" },
    el("img", { class: "order_line_image", attrs: { src: assetUrl(item.imagen), alt: item.nombre_producto } }),
    el(
      "div",
      { class: "order_line_info" },
      el("a", { attrs: { href: "producto.html?id=" + item.producto_id }, text: item.nombre_producto }),
      el("span", { text: item.cantidad + " × " + formatPrice(item.precio_unitario) }),
    ),
    el("span", { class: "order_line_subtotal", text: formatPrice(item.subtotal) }),
  );

const renderDetail = (order) => {
  detailBox.replaceChildren(
    el(
      "div",
      { class: "order_detail_header" },
      el("h2", { text: "Detalle del pedido #" + order.id }),
      estadoBadge(order.estado),
    ),
    el("p", { class: "order_date", text: "Realizado el " + formatDate(order.fecha) }),
    estadoSteps(order.estado),
    el("ul", { class: "order_lines" }, ...order.items.map(detailLine)),
    el(
      "p",
      { class: "summary_row summary_total" },
      el("span", { text: "Total" }),
      el("span", { text: formatPrice(order.total) }),
    ),
  );
  detailBox.hidden = false;
};

const selectOrder = async (id) => {
  selectedId = String(id);
  history.replaceState(null, "", "pedidos.html?id=" + id);
  listBox.querySelectorAll(".order_card").forEach((card) => card.classList.remove("selected"));
  try {
    renderDetail(await apiFetch("/pedidos/" + id, { auth: true }));
    await loadOrders();
    detailBox.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    detailBox.hidden = true;
    showMessage(pageMessage, error.status === 404 ? "Pedido no encontrado" : error.message, "error");
  }
};

const loadOrders = async () => {
  const orders = await apiFetch("/pedidos/", { auth: true });
  listBox.replaceChildren(
    ...(orders.length > 0
      ? orders.map(orderCard)
      : [
          el(
            "div",
            { class: "empty_state" },
            el("p", { text: "Todavía no has realizado ningún pedido" }),
            el("a", { class: "button", attrs: { href: "catalogo.html" }, text: "Ir al catálogo" }),
          ),
        ]),
  );
};

const user = await initLayout("pedidos.html");
if (requireAuth(user)) {
  try {
    await loadOrders();
    if (params.get("nuevo") === "1") {
      showMessage(pageMessage, "¡Compra realizada con éxito! Tu pedido #" + selectedId + " está pendiente.", "success");
    }
    if (selectedId !== null && /^\d+$/.test(selectedId)) {
      await selectOrder(selectedId);
    }
  } catch (error) {
    showMessage(pageMessage, error.message, "error");
  }
}
