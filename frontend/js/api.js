export const API_URL = "http://localhost:8000";

const TOKEN_KEY = "token";

const ERROR_MESSAGES = Object.freeze({
  400: "Solicitud inválida",
  401: "Sesión expirada, inicie sesión nuevamente",
  403: "No tienes permisos para esta acción",
  404: "No encontrado",
  409: "Conflicto con los datos enviados",
  422: "Datos inválidos, revise el formulario",
});

export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

export const readToken = () => {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
};

export const writeToken = (token) => {
  try {
    if (token === null) {
      localStorage.removeItem(TOKEN_KEY);
    } else {
      localStorage.setItem(TOKEN_KEY, token);
    }
  } catch {}
};

export const assetUrl = (path) => API_URL + "/" + path;

const errorMessage = async (response) => {
  const fallback = ERROR_MESSAGES[response.status] ?? "Error en el servidor";
  try {
    const body = await response.json();
    return typeof body.detail === "string" ? body.detail : fallback;
  } catch {
    return fallback;
  }
};

const buildRequest = (method, body, form, token) => {
  const headers = {};
  if (token !== null) {
    headers.Authorization = "Bearer " + token;
  }
  if (form !== undefined) {
    return { method, headers, body: new URLSearchParams(form) };
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    return { method, headers, body: JSON.stringify(body) };
  }
  return { method, headers };
};

export const apiFetch = async (
  path,
  { method = "GET", body, form, auth = false, redirectOn401 = true } = {},
) => {
  const token = auth ? readToken() : null;
  let response;
  try {
    response = await fetch(API_URL + path, buildRequest(method, body, form, token));
  } catch {
    throw new ApiError(0, "No se pudo conectar con el servidor");
  }
  if (response.status === 401 && auth) {
    writeToken(null);
    if (!redirectOn401) {
      throw new ApiError(401, ERROR_MESSAGES[401]);
    }
    window.location.href = "login.html?next=" + encodeURIComponent(currentPage());
    throw new ApiError(401, ERROR_MESSAGES[401]);
  }
  if (!response.ok) {
    throw new ApiError(response.status, await errorMessage(response));
  }
  return response.status === 204 ? null : response.json();
};

export const currentPage = () => {
  const path = window.location.pathname.split("/").pop() || "index.html";
  return path + window.location.search;
};
