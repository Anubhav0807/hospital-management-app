import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";

import "./styles.css";
import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "bootstrap";

// PWA: register service worker
import { registerSW } from "virtual:pwa-register";

registerSW({
  immediate: true,
});

const app = createApp(App);
app.use(router);
app.mount("#app");
