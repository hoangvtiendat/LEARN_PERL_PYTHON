import api from "./api"

const handleError = (method, error) => {
  console.error(`📊 ReportService ${method} error:`, error.response?.data || error.message)
  throw error
}

export const reportService = {
  async getUserReport() {
    try {
      const res = await api.get("/admin/reports/users")
      return res.data
    } catch (err) {
      handleError("getUserReport", err)
    }
  },

  async getCourseReport() {
    try {
      const res = await api.get("/admin/reports/courses")
      return res.data
    } catch (err) {
      handleError("getCourseReport", err)
    }
  },

  async getAssignmentReport() {
    try {
      const res = await api.get("/admin/reports/assignments")
      return res.data
    } catch (err) {
      handleError("getAssignmentReport", err)
    }
  },

  async getActivityReport() {
    try {
      const res = await api.get("/admin/reports/activity")
      return res.data
    } catch (err) {
      handleError("getActivityReport", err)
    }
  },
}
