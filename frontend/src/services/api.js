import axios from "axios"
import router from "@/router" // Import router to redirect

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:5000/api",
  headers: {
    "Content-Type": "application/json",
  },
})

// Request interceptor to add the token to headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  },
)

// Response interceptor to handle errors, especially 401 Unauthorized
api.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // Log the error for debugging
    console.error("🌐 API Interceptor Error:", error.response?.status, error.response?.data, originalRequest.url)

    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      // Check if it's a login or 2FA verification attempt
      const isAuthEndpoint =
        originalRequest.url.includes("/auth/login") || originalRequest.url.includes("/auth/verify-2fa")

      if (isAuthEndpoint) {
        // For login/2FA 401s, do NOT clear token or redirect immediately.
        // Let the calling component/store handle the specific error message (e.g., wrong password, invalid OTP).
        console.log("🌐 API: 401 on auth endpoint. Not clearing token or redirecting.")
        return Promise.reject(error)
      } else {
        // For 401 on other protected routes, it means the token is invalid/expired.
        console.log("🌐 API: 401 on protected route. Clearing token and redirecting to login.")
        localStorage.removeItem("token")
        localStorage.removeItem("user")
        localStorage.removeItem("refreshToken") // Clear refresh token too
        // Use router.push for Vue Router navigation
        if (router.currentRoute.value.name !== "Login") {
          router.push({ name: "Login" })
        }
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  },
)

export default api
