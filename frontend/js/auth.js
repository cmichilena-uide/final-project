import { apiFetch, currentPage, readToken, writeToken } from "./api.js";

export const isLoggedIn = () => readToken() !== null;

export const loadUser = async () => {
  if (!isLoggedIn()) {
    return null;
  }
  try {
    return await apiFetch("/auth/me", { auth: true, redirectOn401: false });
  } catch {
    return null;
  }
};

export const login = async (email, password) => {
  const data = await apiFetch("/auth/login", {
    method: "POST",
    form: { username: email, password },
  });
  writeToken(data.access_token);
};

export const register = (nombre, email, password) =>
  apiFetch("/auth/register", { method: "POST", body: { nombre, email, password } });

export const logout = () => {
  writeToken(null);
  window.location.href = "index.html";
};

export const goToLogin = () => {
  window.location.href = "login.html?next=" + encodeURIComponent(currentPage());
};

export const requireAuth = (user) => {
  if (user === null) {
    goToLogin();
    return false;
  }
  return true;
};

export const requireAdmin = (user) => {
  if (!requireAuth(user)) {
    return false;
  }
  if (user.rol !== "admin") {
    window.location.href = "index.html";
    return false;
  }
  return true;
};
