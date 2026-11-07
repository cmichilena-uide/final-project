import { assetUrl } from "./api.js";

const priceFormat = new Intl.NumberFormat("es-EC", { style: "currency", currency: "USD" });

export const formatPrice = (value) => priceFormat.format(Number(value));

export const formatDate = (value) =>
  new Date(value).toLocaleDateString("es-EC", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

export const el = (tag, props = {}, ...children) => {
  const node = document.createElement(tag);
  const { class: className, text, attrs = {}, on = {} } = props;
  if (className) {
    node.className = className;
  }
  if (text !== undefined) {
    node.textContent = text;
  }
  Object.entries(attrs).forEach(([name, value]) => {
    if (value === true) {
      node.setAttribute(name, "");
    } else if (value !== false && value !== null && value !== undefined) {
      node.setAttribute(name, String(value));
    }
  });
  Object.entries(on).forEach(([event, handler]) => node.addEventListener(event, handler));
  node.append(...children.filter((child) => child !== null && child !== undefined));
  return node;
};

export const showMessage = (node, text, type = "info") => {
  node.textContent = text;
  node.className = "message message_" + type;
  node.hidden = text === "";
};

export const stockLabel = (stock) => {
  if (stock === 0) {
    return { text: "Agotado", type: "out" };
  }
  if (stock <= 3) {
    return { text: "¡Últimas " + stock + " unidades!", type: "low" };
  }
  return { text: "Disponible (" + stock + ")", type: "ok" };
};

export const productImage = (product, className = "product_image") =>
  el("img", {
    class: className,
    attrs: { src: assetUrl(product.imagen), alt: product.nombre, loading: "lazy" },
  });

export const shortText = (text, max = 80) =>
  text.length > max ? text.slice(0, max).trimEnd() + "…" : text;

export const productCard = (product) => {
  const stock = stockLabel(product.stock);
  const link = "producto.html?id=" + product.id;
  return el(
    "article",
    { class: "product_card" },
    el("a", { class: "product_link", attrs: { href: link } }, productImage(product)),
    el("span", { class: "card_category", text: product.categoria.nombre }),
    el("h3", {}, el("a", { attrs: { href: link }, text: product.nombre })),
    el("p", { class: "card_description", text: shortText(product.descripcion) }),
    el(
      "div",
      { class: "card_footer" },
      el("span", { class: "price", text: formatPrice(product.precio) }),
      el("span", { class: "stock stock_" + stock.type, text: stock.text }),
    ),
    el("a", { class: "button card_button", attrs: { href: link }, text: "Ver detalle" }),
  );
};

export const emptyState = (text) => el("p", { class: "empty_state", text });
