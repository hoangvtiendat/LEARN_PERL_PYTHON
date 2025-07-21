import api from "./api"

export const authService = {
  async login({ email, password }) {
    console.log("🌐 Login request:", { email })
    try {
      const res = await api.post("/auth/login", { email, password })
      console.log("✅ Login success:", res.data)
      return res.data
    } catch (err) {
      console.error("❌ Login failed:", err)
      throw err
    }
  },

  register({ email, password, full_name, student_code }) {
    return api.post("/auth/register", { email, password, full_name, student_code })
      .then(res => res.data)
  },

  logout() {
    return api.post("/auth/logout").then(res => res.data)
  },

  async getProfile() {
    console.log("🌐 Fetching profile")
    try {
      const res = await api.get("/user/profile")
      console.log("✅ Profile:", res.data)
      return res.data
    } catch (err) {
      console.error("❌ Profile fetch failed:", err)
      throw err
    }
  },

  updateProfile({ full_name, email }) {
    return api.put("/user/profile", { full_name, email }).then(res => res.data)
  },

  changePassword({ current_password, new_password, confirm_password }) {
    return api.post("/user/change-password", {
      current_password,
      new_password,
      confirm_password,
    }).then(res => res.data)
  },

  verifyTwoFactor(otp, tempToken) {
  console.log("🌐 Verifying 2FA with OTP:", otp)
  return api.post("/auth/verify-2fa", { otp }, {
    headers: {
      Authorization: `Bearer ${tempToken}`
    }
  })
  .then(res => {
    console.log("✅ 2FA success:", res.data)
    return res.data
  })
  .catch(err => {
    console.error("❌ 2FA failed:", err)
    throw err
  })
},

  toggleTwoFactor(enable) {
    return api.post("/auth/toggle-2fa", { enable }).then(res => res.data)
  },

  forgotPassword(email) {
    return api.post("/auth/forgot-password", { email }).then(res => res.data)
  },

  resetPassword(token, password) {
    return api.post("/auth/reset-password", { token, password }).then(res => res.data)
  },
}
