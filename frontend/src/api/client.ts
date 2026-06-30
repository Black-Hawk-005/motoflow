import axios from "axios";

const axiosClient = axios.create({
  baseURL: "http://localhost:8000",
});

axiosClient.interceptors.request.use((config) => {
  const authToken = localStorage.getItem("token");
  if (authToken) {
    config.headers.Authorization = `Bearer ${authToken}`;
  }
  return config;
});
export default axiosClient;
