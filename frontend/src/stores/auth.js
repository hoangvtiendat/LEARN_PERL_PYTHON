import { defineStore } from "pinia"
import { ref, computed } from "vue"
import router from "@/router"
import { authService } from "@/services/authService"

export const useAuthStore = defineStore("auth", () => {
  const user = ref(null)
  const token = ref(localStorage.getItem("token"))
  const isLoading = ref(false)
  const twoFactorRequired = ref(false)
  const pendingLoginData = ref(null)
  const tempToken = ref(null)
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // Helpers
  const setTokens = (accessToken, refreshToken) => {
    token.value = accessToken
    localStorage.setItem("token", accessToken)
    if (refreshToken) localStorage.setItem("refreshToken", refreshToken)
  }

  const clearAuthData = () => {
    user.value = null
    token.value = null
    twoFactorRequired.value = false
    pendingLoginData.value = null
    localStorage.removeItem("token")
    localStorage.removeItem("refreshToken")
    localStorage.removeItem("user")
  }

  const setUser = (userData) => {
    user.value = userData
    localStorage.setItem("user", JSON.stringify(userData))
  }

  const login = async (credentials) => {
  isLoading.value = true
  try {
    const res = await authService.login(credentials)

    // Kiểm tra bằng message từ backend
    if (res.message === 'Vui lòng nhập mã OTP đã được gửi đến email của bạn.' && res.temp_token) {
      tempToken.value = res.temp_token
      twoFactorRequired.value = true
      pendingLoginData.value = credentials

      return { success: true, requires2FA: true, message: res.message }
    }

    if (res.access_token && res.refresh_token) {
      setTokens(res.access_token, res.refresh_token)
      twoFactorRequired.value = false
      await fetchProfile()
      if (user.value) return { success: true }

      await logout()
      throw new Error("Đăng nhập thành công nhưng không thể lấy thông tin người dùng.")
    }

    throw new Error(res.message || "Đăng nhập thất bại.")

  } catch (err) {
    const msg = err.response?.data?.error || err.message || "Đăng nhập thất bại."
    throw new Error(msg)

  } finally {
    isLoading.value = false
  }}

  const verifyTwoFactor = async (otp) => {
  isLoading.value = true
  try {
    const res = await authService.verifyTwoFactor(otp, tempToken.value)

    if (res.access_token && res.refresh_token) {
      setTokens(res.access_token, res.refresh_token)
      twoFactorRequired.value = false
      tempToken.value = null
      pendingLoginData.value = null

      await fetchProfile()
      if (user.value) return { success: true }

      await logout()
      throw new Error("Xác thực thành công nhưng không thể lấy thông tin người dùng.")
    }

    throw new Error(res.message || "Xác thực OTP thất bại.")

  } catch (err) {
    throw new Error(err.response?.data?.error || err.message || "Mã OTP không đúng.")

  } finally {
    isLoading.value = false
  }
}

  const fetchProfile = async () => {
    if (!token.value) return
    try {
      const res = await authService.getProfile()
      setUser(res.user || res)
    } catch (err) {
      throw err
    }
  }

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem("refreshToken")
      if (refreshToken) await authService.logout()
    } catch (err) {
      console.error("Logout error:", err)
    } finally {
      clearAuthData()
      if (router.currentRoute.value.name !== "Login") {
        router.push({ name: "Login" })
      }
    }
  }

  const checkAuth = async () => {
    if (!token.value) {
      user.value = null
      return
    }
    try {
      await fetchProfile()
    } catch {
      await logout()
    }
  }

  const cancelTwoFactor = () => {
    twoFactorRequired.value = false
    pendingLoginData.value = null
    tempToken.value = null
    localStorage.removeItem("token")
  }

  // Utility API wrappers (shared pattern)
  const apiCall = async (fn, ...args) => {
    isLoading.value = true
    try {
      return await fn(...args)
    } catch (err) {
      console.error(`${fn.name} error:`, err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const register = (data) => apiCall(authService.register, data)
  const updateProfile = async (data) => {
    const res = await apiCall(authService.updateProfile, data)
    if (res.user) setUser(res.user)
    return res
  }
  const changePassword = (data) => apiCall(authService.changePassword, data)
  const toggleTwoFactor = (enable) => apiCall(authService.toggleTwoFactor, enable)
  const forgotPassword = (email) => apiCall(authService.forgotPassword, email)
  const resetPassword = (token, password) => apiCall(authService.resetPassword, token, password)

  // Restore user from localStorage
  const storedUser = localStorage.getItem("user")
  if (storedUser) {
    try {
      user.value = JSON.parse(storedUser)
    } catch {
      localStorage.removeItem("user")
    }
  }

  return {
    user,
    token,
    isLoading,
    twoFactorRequired,
    pendingLoginData,
    isAuthenticated,
    login,
    register,
    logout,
    checkAuth,
    fetchProfile,
    updateProfile,
    changePassword,
    verifyTwoFactor,
    toggleTwoFactor,
    forgotPassword,
    resetPassword,
    cancelTwoFactor,
  }
})
