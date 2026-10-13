// Save Co. · Design System Save v0.5 · preset do Tailwind para aplicativos e sites (Next.js, React, React Native/NativeWind).
// Uso no tailwind.config.js:  presets: [require("./tailwind-preset.js")]
// Valores = marca.json. Ouro em texto sobre fundo claro: sempre "ouro-texto".
const M = require("./marca.json");

module.exports = {
  darkMode: "class",
  theme: {
    extend: {
      fontFamily: {
        sans: ["IBM Plex Sans", "ui-sans-serif", "system-ui", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "Menlo", "monospace"],
      },
      colors: {
        save: {
          fundo: M.claro.fundo, "fundo-2": M.claro.fundo_2, cartao: M.claro.cartao,
          borda: M.claro.borda, "borda-2": M.claro.borda_2, "borda-3": M.claro.borda_3,
          texto: M.claro.texto, "texto-2": M.claro.texto_2, "texto-3": M.claro.texto_3,
          ouro: M.claro.ouro, "ouro-texto": M.claro.ouro_texto, "ouro-suave": M.claro.ouro_suave,
          sucesso: M.claro.sucesso, alerta: M.claro.alerta, erro: M.claro.erro, info: M.claro.info,
        },
        "save-escuro": {
          fundo: M.escuro.fundo, "fundo-2": M.escuro.fundo_2, cartao: M.escuro.cartao, elevado: M.escuro.elevado,
          borda: M.escuro.borda, texto: M.escuro.texto, "texto-2": M.escuro.texto_2, "texto-3": M.escuro.texto_3,
          ouro: M.escuro.ouro, sucesso: M.escuro.sucesso, alerta: M.escuro.alerta, erro: M.escuro.erro, info: M.escuro.info,
        },
      },
      borderRadius: { xs: "4px", sm: "8px", md: "12px", lg: "16px", xl: "24px" },  // nunca acima de 24
      fontSize: { micro: "11px", legenda: "12px", h4: "24px", h3: "30px", h2: "36px", h1: "48px", display: "56px" },
      transitionTimingFunction: { save: "cubic-bezier(0.4, 0, 0.2, 1)" },
      transitionDuration: { hover: "120ms", abre: "180ms", modal: "240ms", pagina: "300ms" },
      minHeight: { toque: "44px" },
      minWidth: { toque: "44px" },
    },
  },
};
