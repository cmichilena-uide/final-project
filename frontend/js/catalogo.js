import { apiFetch } from "./api.js";
import { initLayout } from "./layout.js";
import { el, emptyState, productCard, showMessage } from "./ui.js";

const productList = document.querySelector("#product_list");
const chipBox = document.querySelector("#category_chips");
const resultCount = document.querySelector("#result_count");
const searchInput = document.querySelector("#search_input");
const pageMessage = document.querySelector("#page_message");

const params = new URLSearchParams(window.location.search);
const filters = {
  q: params.get("q") ?? "",
  categoria: params.get("categoria") ?? "",
};
let categories = [];

const syncUrl = () => {
  const query = new URLSearchParams();
  if (filters.q !== "") {
    query.set("q", filters.q);
  }
  if (filters.categoria !== "") {
    query.set("categoria", filters.categoria);
  }
  const text = query.toString();
  history.replaceState(null, "", text === "" ? "catalogo.html" : "catalogo.html?" + text);
};

const chip = (text, value) =>
  el("button", {
    class: value === filters.categoria ? "chip chip_active" : "chip",
    text,
    attrs: { type: "button", "aria-pressed": value === filters.categoria },
    on: {
      click: () => {
        filters.categoria = value;
        renderChips();
        loadProducts();
      },
    },
  });

const renderChips = () => {
  chipBox.replaceChildren(
    chip("Todas", ""),
    ...categories.map((category) => chip(category.nombre, String(category.id))),
  );
};

const countText = (total) => {
  const category = categories.find((item) => String(item.id) === filters.categoria);
  const parts = [total + (total === 1 ? " producto" : " productos")];
  if (category) {
    parts.push("en " + category.nombre);
  }
  if (filters.q !== "") {
    parts.push('para "' + filters.q + '"');
  }
  return parts.join(" ");
};

const loadProducts = async () => {
  syncUrl();
  const query = new URLSearchParams();
  if (filters.q !== "") {
    query.set("q", filters.q);
  }
  if (filters.categoria !== "") {
    query.set("categoria_id", filters.categoria);
  }
  try {
    const products = await apiFetch("/productos/?" + query.toString());
    showMessage(pageMessage, "");
    resultCount.textContent = countText(products.length);
    productList.replaceChildren(
      ...(products.length > 0
        ? products.map(productCard)
        : [emptyState("No encontramos productos con esos filtros")]),
    );
  } catch (error) {
    showMessage(pageMessage, error.message, "error");
  }
};

document.querySelector("#search_form").addEventListener("submit", (event) => {
  event.preventDefault();
  filters.q = searchInput.value.trim();
  loadProducts();
});

searchInput.value = filters.q;
await initLayout("catalogo.html");
try {
  categories = await apiFetch("/categorias/");
  renderChips();
} catch (error) {
  showMessage(pageMessage, error.message, "error");
}
await loadProducts();
