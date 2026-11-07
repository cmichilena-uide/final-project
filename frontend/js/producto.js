import { apiFetch, assetUrl } from "./api.js";
import { goToLogin } from "./auth.js";
import { initLayout, setCartCount } from "./layout.js";
import { formatPrice, showMessage, stockLabel } from "./ui.js";

const detail = document.querySelector("#product_detail");
const pageMessage = document.querySelector("#page_message");
const addMessage = document.querySelector("#add_message");
const quantityInput = document.querySelector("#quantity");
const addButton = document.querySelector("#add_button");

const productId = new URLSearchParams(window.location.search).get("id");
let product = null;
let user = null;

const renderStock = () => {
  const stock = stockLabel(product.stock);
  const stockNode = document.querySelector("#detail_stock");
  stockNode.textContent = stock.text;
  stockNode.className = "stock stock_" + stock.type;
  quantityInput.max = String(Math.max(product.stock, 1));
  quantityInput.disabled = product.stock === 0;
  addButton.disabled = product.stock === 0;
  addButton.textContent = product.stock === 0 ? "Agotado" : "Agregar al carrito";
};

const renderProduct = () => {
  document.title = "TecnoTienda | " + product.nombre;
  const image = document.querySelector("#detail_image");
  image.src = assetUrl(product.imagen);
  image.alt = product.nombre;
  const category = document.querySelector("#detail_category");
  category.textContent = product.categoria.nombre;
  category.href = "catalogo.html?categoria=" + product.categoria.id;
  document.querySelector("#detail_name").textContent = product.nombre;
  document.querySelector("#detail_price").textContent = formatPrice(product.precio);
  document.querySelector("#detail_description").textContent = product.descripcion;
  renderStock();
  detail.hidden = false;
};

const loadProduct = async () => {
  if (productId === null || !/^\d+$/.test(productId)) {
    showMessage(pageMessage, "Producto no encontrado", "error");
    return;
  }
  try {
    product = await apiFetch("/productos/" + productId);
    renderProduct();
  } catch (error) {
    showMessage(pageMessage, error.status === 404 ? "Producto no encontrado" : error.message, "error");
  }
};

document.querySelector("#add_form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (user === null) {
    goToLogin();
    return;
  }
  const cantidad = Number(quantityInput.value);
  if (!Number.isInteger(cantidad) || cantidad < 1) {
    showMessage(addMessage, "Ingrese una cantidad válida", "error");
    return;
  }
  if (cantidad > product.stock) {
    showMessage(addMessage, "Solo hay " + product.stock + " unidades disponibles", "error");
    return;
  }
  addButton.disabled = true;
  try {
    const cart = await apiFetch("/carrito/items", {
      method: "POST",
      auth: true,
      body: { producto_id: product.id, cantidad },
    });
    setCartCount(cart.cantidad_total);
    showMessage(addMessage, "Producto agregado al carrito", "success");
  } catch (error) {
    showMessage(addMessage, error.message, "error");
  } finally {
    addButton.disabled = product.stock === 0;
  }
});

user = await initLayout("catalogo.html");
await loadProduct();
