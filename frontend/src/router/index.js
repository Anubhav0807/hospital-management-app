import { createRouter, createWebHistory } from "vue-router";
import LoginPage from "../pages/LoginPage.vue";
import RegisterPage from "../pages/RegisterPage.vue";
import ResetPasswordPage from "../pages/ResetPasswordPage.vue";
import DashboardPage from "../pages/DashboardPage.vue";
import api from "../api.js";

const routes = [
  { path: "/", redirect: "/dashboard" },
  { path: "/dashboard", name: "Dashboard", component: DashboardPage },
  { path: "/login", name: "Login", component: LoginPage },
  { path: "/register", name: "Register", component: RegisterPage },
  { path: "/reset-password", name: "ResetPassword", component: ResetPasswordPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const publicPaths = ["/login", "/register", "/reset-password"];
  const token = localStorage.getItem("token");

  // Allow open routes
  if (publicPaths.includes(to.path)) return next();

  // Require authentication
  if (!token) return next("/login");

  next();
});

export default router;
