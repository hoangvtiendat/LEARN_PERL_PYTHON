import api from "./api"

const handleError = (method, error) => {
  console.error(`👤 userService ${method} error:`, error.response?.data || error.message)
  throw error
}

export const userService = {
  async getAllUsers() {
    try {
      const res = await api.get("/admin/users")
      return res.data
    } catch (err) {
      handleError("getAllUsers", err)
    }
  },

  async getUserById(id) {
    try {
      const res = await api.get(`/admin/users/${id}`)
      return res.data
    } catch (err) {
      handleError("getUserById", err)
    }
  },

  async createUser(userData) {
    try {
      const res = await api.post("/admin/users", userData)
      return res.data
    } catch (err) {
      handleError("createUser", err)
    }
  },

  async updateUser(id, userData) {
    try {
      const res = await api.put(`/admin/users/${id}`, userData)
      return res.data
    } catch (err) {
      handleError("updateUser", err)
    }
  },

  async deleteUser(id) {
    try {
      const res = await api.delete(`/admin/users/${id}`)
      return res.data
    } catch (err) {
      handleError("deleteUser", err)
    }
  },

  async getReports() {
    try {
      const res = await api.get("/admin/reports")
      return res.data
    } catch (err) {
      handleError("getReports", err)
    }
  },
}
