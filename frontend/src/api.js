import axios from "axios";
import router from "./router";

const api = axios.create({
  baseURL: "http://localhost:5000/api",
});

// Attach JWT token to every outgoing request
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Redirect to login page in case of invalid token
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      router.push("/login")
    }
    return Promise.reject(error);
  }
);

export default api;
