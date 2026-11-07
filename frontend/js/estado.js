import { el } from "./ui.js";

export const ESTADOS = Object.freeze(["pendiente", "procesando", "enviado", "entregado"]);

const LABELS = Object.freeze({
  pendiente: "Pendiente",
  procesando: "Procesando",
  enviado: "Enviado",
  entregado: "Entregado",
});

export const estadoLabel = (estado) => LABELS[estado] ?? estado;

export const estadoBadge = (estado) =>
  el("span", { class: "status status_" + estado, text: estadoLabel(estado) });

export const estadoSteps = (estado) => {
  const current = ESTADOS.indexOf(estado);
  return el(
    "ol",
    { class: "status_steps", attrs: { "aria-label": "Estado del pedido" } },
    ...ESTADOS.map((step, index) =>
      el("li", {
        class: index <= current ? "status_step done" : "status_step",
        text: estadoLabel(step),
        attrs: { "aria-current": index === current ? "step" : null },
      }),
    ),
  );
};
