import { login, nextPage, register } from "./auth.js";
import { initLayout } from "./layout.js";
import { showMessage } from "./ui.js";

const form = document.querySelector("#register_form");
const message = document.querySelector("#form_message");
const submitButton = document.querySelector("#submit_button");

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const RULES = Object.freeze([
  { fails: (d) => d.nombre.length < 2, message: "Ingrese su nombre completo" },
  { fails: (d) => !EMAIL_PATTERN.test(d.email), message: "Ingrese un correo válido" },
  { fails: (d) => d.password.length < 8, message: "La contraseña debe tener al menos 8 caracteres" },
  { fails: (d) => d.password !== d.confirm, message: "Las contraseñas no coinciden" },
]);

const readForm = () => ({
  nombre: document.querySelector("#nombre").value.trim(),
  email: document.querySelector("#email").value.trim(),
  password: document.querySelector("#password").value,
  confirm: document.querySelector("#confirm_password").value,
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = readForm();
  const error = RULES.find((rule) => rule.fails(data));
  if (error) {
    showMessage(message, error.message, "error");
    return;
  }
  submitButton.disabled = true;
  try {
    await register(data.nombre, data.email, data.password);
    await login(data.email, data.password);
    window.location.href = nextPage();
  } catch (requestError) {
    showMessage(message, requestError.message, "error");
    submitButton.disabled = false;
  }
});

const user = await initLayout("registro.html");
if (user !== null) {
  window.location.href = nextPage();
}
document.querySelector("#switch_link").href =
  "login.html" + window.location.search;
