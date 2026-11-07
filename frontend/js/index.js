import { apiFetch } from "./api.js";
import { initLayout } from "./layout.js";
import { el, emptyState, productCard, showMessage } from "./ui.js";

const RANDOM_COUNT = 4;

const randomBox = document.querySelector("#random_products");
const featuredBox = document.querySelector("#featured_products");
const categoryBox = document.querySelector("#category_list");
const pageMessage = document.querySelector("#page_message");

const renderProducts = (box, products, emptyText) => {
  box.replaceChildren(
    ...(products.length > 0 ? products.map(productCard) : [emptyState(emptyText)]),
  );
};

const categoryCard = (category) =>
  el(
    "a",
    { class: "category_card", attrs: { href: "catalogo.html?categoria=" + category.id } },
    el("h3", { text: category.nombre }),
    el("p", { text: category.descripcion }),
  );

const loadRandom = async () => {
  const products = await apiFetch("/productos/aleatorios?limite=" + RANDOM_COUNT);
  renderProducts(randomBox, products, "No hay productos disponibles");
};

const loadHome = async () => {
  try {
    const [featured, categories] = await Promise.all([
      apiFetch("/productos/?destacado=true"),
      apiFetch("/categorias/"),
      loadRandom(),
    ]);
    renderProducts(featuredBox, featured, "No hay productos destacados");
    categoryBox.replaceChildren(...categories.map(categoryCard));
  } catch (error) {
    showMessage(pageMessage, error.message, "error");
  }
};

document.querySelector("#search_form").addEventListener("submit", (event) => {
  event.preventDefault();
  const text = document.querySelector("#search_input").value.trim();
  window.location.href = text === "" ? "catalogo.html" : "catalogo.html?q=" + encodeURIComponent(text);
});

document.querySelector("#shuffle_button").addEventListener("click", () => {
  loadRandom().catch((error) => showMessage(pageMessage, error.message, "error"));
});

await initLayout("index.html");
await loadHome();
