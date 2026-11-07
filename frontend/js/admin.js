import { apiFetch, assetUrl } from "./api.js";
import { requireAdmin } from "./auth.js";
import { ESTADOS, estadoBadge, estadoLabel } from "./estado.js";
import { initLayout } from "./layout.js";
import { el, formatDate, formatPrice, showMessage, stockLabel } from "./ui.js";

const pageMessage = document.querySelector("#page_message");
const $ = (selector) => document.querySelector(selector);

const state = { products: [], categories: [], editingProduct: null, editingCategory: null };

const notify = (text, type = "success") => {
  showMessage(pageMessage, text, type);
  pageMessage.scrollIntoView({ behavior: "smooth", block: "nearest" });
};

const attempt = async (action, successText) => {
  try {
    await action();
    if (successText) {
      notify(successText);
    }
    return true;
  } catch (error) {
    notify(error.message, "error");
    return false;
  }
};

document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((other) => other.classList.toggle("active", other === tab));
    document.querySelectorAll(".admin_section").forEach((section) => {
      section.hidden = section.id !== tab.dataset.tab;
    });
    showMessage(pageMessage, "");
    if (tab.dataset.tab === "orders_tab") {
      loadOrders();
    }
  });
});

const option = (value, text, selected = false) =>
  el("option", { text, attrs: { value, selected } });

const fillCategorySelect = () => {
  $("#product_category").replaceChildren(
    option("", "Seleccione una categoría"),
    ...state.categories.map((category) => option(String(category.id), category.nombre)),
  );
};

const updatePreview = () => {
  const path = $("#product_image").value;
  const preview = $("#image_preview");
  preview.hidden = path === "";
  if (path !== "") {
    preview.src = assetUrl(path);
  }
};

const PRODUCT_RULES = Object.freeze([
  { fails: (d) => d.nombre.length < 2, message: "El nombre debe tener al menos 2 caracteres" },
  { fails: (d) => d.descripcion === "", message: "Ingrese una descripción" },
  { fails: (d) => !/^\d+(\.\d{1,2})?$/.test(d.precio) || Number(d.precio) <= 0, message: "El precio debe ser mayor a 0 con máximo 2 decimales" },
  { fails: (d) => !Number.isInteger(d.stock) || d.stock < 0, message: "El stock debe ser un número entero mayor o igual a 0" },
  { fails: (d) => Number.isNaN(d.categoria_id), message: "Seleccione una categoría" },
  { fails: (d) => d.imagen === "", message: "Seleccione una imagen" },
]);

const readProductForm = () => ({
  nombre: $("#product_name").value.trim(),
  descripcion: $("#product_description").value.trim(),
  precio: $("#product_price").value.trim(),
  stock: Number($("#product_stock").value === "" ? NaN : $("#product_stock").value),
  categoria_id: Number.parseInt($("#product_category").value, 10),
  imagen: $("#product_image").value,
  destacado: $("#product_featured").checked,
});

const resetProductForm = () => {
  state.editingProduct = null;
  $("#product_form").reset();
  $("#product_form_title").textContent = "Agregar producto";
  $("#product_save").textContent = "Guardar";
  $("#product_cancel").hidden = true;
  updatePreview();
};

const editProduct = (product) => {
  state.editingProduct = product.id;
  $("#product_name").value = product.nombre;
  $("#product_description").value = product.descripcion;
  $("#product_price").value = product.precio;
  $("#product_stock").value = String(product.stock);
  $("#product_category").value = String(product.categoria.id);
  $("#product_image").value = product.imagen;
  $("#product_featured").checked = product.destacado;
  $("#product_form_title").textContent = "Editar producto #" + product.id;
  $("#product_save").textContent = "Actualizar";
  $("#product_cancel").hidden = false;
  updatePreview();
  $("#product_form").scrollIntoView({ behavior: "smooth", block: "start" });
};

const saveStock = async (product, input) => {
  const stock = Number(input.value);
  if (!Number.isInteger(stock) || stock < 0) {
    notify("El stock debe ser un número entero mayor o igual a 0", "error");
    return;
  }
  const ok = await attempt(
    () => apiFetch("/productos/" + product.id + "/stock", { method: "PATCH", auth: true, body: { stock } }),
    "Stock de " + product.nombre + " actualizado a " + stock,
  );
  if (ok) {
    await loadProducts();
  }
};

const deleteProduct = async (product) => {
  if (!window.confirm("¿Eliminar " + product.nombre + "? Ya no se mostrará en la tienda.")) {
    return;
  }
  const ok = await attempt(
    () => apiFetch("/productos/" + product.id, { method: "DELETE", auth: true }),
    "Producto " + product.nombre + " eliminado",
  );
  if (ok) {
    if (state.editingProduct === product.id) {
      resetProductForm();
    }
    await loadProducts();
  }
};

const productRow = (product) => {
  const stock = stockLabel(product.stock);
  const stockInput = el("input", {
    class: "stock_input",
    attrs: { type: "number", min: 0, step: 1, value: product.stock, "aria-label": "Stock de " + product.nombre },
  });
  return el(
    "article",
    { class: "admin_row" },
    el("img", { class: "admin_thumb", attrs: { src: assetUrl(product.imagen), alt: product.nombre } }),
    el(
      "div",
      { class: "admin_row_info" },
      el("h3", { text: "#" + product.id + " " + product.nombre }),
      el("p", { text: product.categoria.nombre + " · " + formatPrice(product.precio) + (product.destacado ? " · ★ Destacado" : "") }),
      el("p", { class: "stock stock_" + stock.type, text: stock.text }),
    ),
    el(
      "div",
      { class: "admin_row_actions" },
      el(
        "div",
        { class: "stock_editor" },
        stockInput,
        el("button", { text: "Stock", attrs: { type: "button", title: "Guardar stock" }, on: { click: () => saveStock(product, stockInput) } }),
      ),
      el("button", { class: "button_light", text: "Editar", attrs: { type: "button" }, on: { click: () => editProduct(product) } }),
      el("button", { class: "button_danger", text: "Eliminar", attrs: { type: "button" }, on: { click: () => deleteProduct(product) } }),
    ),
  );
};

const renderProducts = () => {
  const filter = $("#product_filter").value.trim().toLowerCase();
  const visible = state.products.filter((product) =>
    (product.nombre + " " + product.categoria.nombre).toLowerCase().includes(filter),
  );
  $("#product_count").textContent = String(state.products.length);
  $("#product_list").replaceChildren(
    ...(visible.length > 0
      ? visible.map(productRow)
      : [el("p", { class: "empty_state", text: "No hay productos" })]),
  );
};

const loadProducts = async () => {
  state.products = await apiFetch("/productos/");
  renderProducts();
  renderCategories();
};

$("#product_image").addEventListener("change", updatePreview);
$("#product_filter").addEventListener("input", renderProducts);
$("#product_cancel").addEventListener("click", resetProductForm);

$("#product_form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = readProductForm();
  const error = PRODUCT_RULES.find((rule) => rule.fails(data));
  if (error) {
    notify(error.message, "error");
    return;
  }
  const editing = state.editingProduct;
  let saved = null;
  const ok = await attempt(async () => {
    saved = await apiFetch(editing === null ? "/productos/" : "/productos/" + editing, {
      method: editing === null ? "POST" : "PUT",
      auth: true,
      body: data,
    });
  });
  if (ok) {
    notify(editing === null ? "Producto creado con ID " + saved.id : "Producto #" + saved.id + " actualizado");
    resetProductForm();
    await loadProducts();
  }
});

const resetCategoryForm = () => {
  state.editingCategory = null;
  $("#category_form").reset();
  $("#category_form_title").textContent = "Agregar categoría";
  $("#category_save").textContent = "Guardar";
  $("#category_cancel").hidden = true;
};

const editCategory = (category) => {
  state.editingCategory = category.id;
  $("#category_name").value = category.nombre;
  $("#category_description").value = category.descripcion;
  $("#category_form_title").textContent = "Editar categoría #" + category.id;
  $("#category_save").textContent = "Actualizar";
  $("#category_cancel").hidden = false;
  $("#category_form").scrollIntoView({ behavior: "smooth", block: "start" });
};

const deleteCategory = async (category) => {
  if (!window.confirm("¿Eliminar la categoría " + category.nombre + "?")) {
    return;
  }
  const ok = await attempt(
    () => apiFetch("/categorias/" + category.id, { method: "DELETE", auth: true }),
    "Categoría " + category.nombre + " eliminada",
  );
  if (ok) {
    await loadCategories();
  }
};

const categoryRow = (category) => {
  const count = state.products.filter((product) => product.categoria.id === category.id).length;
  return el(
    "article",
    { class: "admin_row" },
    el(
      "div",
      { class: "admin_row_info" },
      el("h3", { text: "#" + category.id + " " + category.nombre }),
      el("p", { text: category.descripcion }),
      el("p", { class: "admin_meta", text: count + (count === 1 ? " producto" : " productos") }),
    ),
    el(
      "div",
      { class: "admin_row_actions" },
      el("button", { class: "button_light", text: "Editar", attrs: { type: "button" }, on: { click: () => editCategory(category) } }),
      el("button", { class: "button_danger", text: "Eliminar", attrs: { type: "button" }, on: { click: () => deleteCategory(category) } }),
    ),
  );
};

const renderCategories = () => {
  $("#category_list").replaceChildren(...state.categories.map(categoryRow));
};

const loadCategories = async () => {
  state.categories = await apiFetch("/categorias/");
  fillCategorySelect();
  renderCategories();
};

$("#category_cancel").addEventListener("click", resetCategoryForm);

$("#category_form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = {
    nombre: $("#category_name").value.trim(),
    descripcion: $("#category_description").value.trim(),
  };
  if (data.nombre.length < 2 || data.descripcion === "") {
    notify("Ingrese el nombre (mínimo 2 caracteres) y la descripción", "error");
    return;
  }
  const editing = state.editingCategory;
  const ok = await attempt(
    () =>
      apiFetch(editing === null ? "/categorias/" : "/categorias/" + editing, {
        method: editing === null ? "POST" : "PUT",
        auth: true,
        body: data,
      }),
    editing === null ? "Categoría " + data.nombre + " creada" : "Categoría " + data.nombre + " actualizada",
  );
  if (ok) {
    resetCategoryForm();
    await loadCategories();
    await loadProducts();
  }
});

const nextEstado = (estado) => ESTADOS[ESTADOS.indexOf(estado) + 1] ?? null;

const advanceOrder = async (order, estado) => {
  const ok = await attempt(
    () => apiFetch("/admin/pedidos/" + order.id + "/estado", { method: "PATCH", auth: true, body: { estado } }),
    "Pedido #" + order.id + " ahora está " + estadoLabel(estado).toLowerCase(),
  );
  if (ok) {
    await loadOrders();
  }
};

const orderRow = (order) => {
  const next = nextEstado(order.estado);
  return el(
    "article",
    { class: "admin_row admin_order" },
    el(
      "div",
      { class: "admin_row_info" },
      el("div", { class: "order_card_header" }, el("h3", { text: "Pedido #" + order.id }), estadoBadge(order.estado)),
      el("p", { text: order.cliente.nombre + " · " + order.cliente.email }),
      el("p", { class: "admin_meta", text: formatDate(order.fecha) }),
      el(
        "ul",
        { class: "admin_order_items" },
        ...order.items.map((item) => el("li", { text: item.cantidad + " × " + item.nombre_producto + " (" + formatPrice(item.subtotal) + ")" })),
      ),
      el("p", { class: "price", text: "Total: " + formatPrice(order.total) }),
    ),
    el(
      "div",
      { class: "admin_row_actions" },
      next === null
        ? el("span", { class: "admin_meta", text: "Pedido completado" })
        : el("button", {
            text: "Marcar como " + estadoLabel(next).toLowerCase(),
            attrs: { type: "button" },
            on: { click: () => advanceOrder(order, next) },
          }),
    ),
  );
};

const loadOrders = async () => {
  const estado = $("#order_filter").value;
  try {
    const orders = await apiFetch("/admin/pedidos" + (estado === "" ? "" : "?estado=" + estado), { auth: true });
    $("#admin_order_list").replaceChildren(
      ...(orders.length > 0
        ? orders.map(orderRow)
        : [el("p", { class: "empty_state", text: "No hay pedidos con ese estado" })]),
    );
  } catch (error) {
    notify(error.message, "error");
  }
};

$("#order_filter").addEventListener("change", loadOrders);

const loadImages = async () => {
  const images = await apiFetch("/productos/imagenes", { auth: true });
  $("#product_image").replaceChildren(
    option("", "Seleccione una imagen"),
    ...images.map((path) => option(path, path.replace("Assets/", ""))),
  );
};

const user = await initLayout("admin.html");
if (requireAdmin(user)) {
  try {
    await Promise.all([loadCategories(), loadImages(), loadProducts()]);
  } catch (error) {
    notify(error.message, "error");
  }
}
