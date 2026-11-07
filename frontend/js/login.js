import { login, nextPage } from "./auth.js";
import { initLayout } from "./layout.js";
import { showMessage } from "./ui.js";

const form = document.querySelector("#login_form");
const message = document.querySelector("#form_message");
const submitButton = document.querySelector("#submit_button");

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const email = document.querySelector("#email").value.trim();
  const password = document.querySelector("#password").value;
  if (!EMAIL_PATTERN.test(email) || password === "") {
    showMessage(message, "Ingrese su correo y contraseña", "error");
    return;
  }
  submitButton.disabled = true;
  try {
    await login(email, password);
    window.location.href = nextPage();
  } catch (error) {
    showMessage(message, error.message, "error");
    submitButton.disabled = false;
  }
});

const user = await initLayout("login.html");
if (user !== null) {
  window.location.href = nextPage();
}
document.querySelector("#switch_link").href =
  "registro.html" + window.location.search;
