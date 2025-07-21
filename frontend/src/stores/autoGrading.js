// import { defineStore } from "pinia"
// import { ref } from "vue"
// import { aiService } from "@/services/aiService"

// export const useAutoGradingStore = defineStore("autoGrading", () => {
//   const settings = ref({
//     apiKey: "",
//     model: "gpt-4o",
//     enabled: false,
//   })
//   const isLoading = ref(false)
//   const error = ref(null)
//   const successMessage = ref(null)

//   // Load settings from localStorage on store initialization
//   const loadSettings = () => {
//     const storedSettings = localStorage.getItem("autoGradingSettings")
//     if (storedSettings) {
//       try {
//         settings.value = JSON.parse(storedSettings)
//       } catch (e) {
//         console.error("Failed to parse auto grading settings from localStorage", e)
//         localStorage.removeItem("autoGradingSettings")
//       }
//     }
//   }

//   // Save settings to localStorage
//   const saveSettings = () => {
//     localStorage.setItem("autoGradingSettings", JSON.stringify(settings.value))
//   }

//   const updateSettings = (newSettings) => {
//     settings.value = { ...settings.value, ...newSettings }
//     saveSettings()
//     successMessage.value = "Cài đặt đã được cập nhật."
//     setTimeout(() => (successMessage.value = null), 3000)
//   }

//   const autoGradeSubmission = async (submissionId) => {
//     isLoading.value = true
//     error.value = null
//     successMessage.value = null
//     try {
//       // In a real app, you'd fetch submission content here
//       // For now, let's mock it or assume the backend handles fetching content
//       const response = await aiService.autoGrade({
//         submission_id: submissionId,
//         model: settings.value.model,
//         api_key: settings.value.apiKey, // Pass API key if backend needs it
//       })
//       successMessage.value = response.message || "Chấm điểm tự động thành công."
//       return response // Assuming response contains the grade
//     } catch (err) {
//       error.value = err.response?.data?.message || "Chấm điểm tự động thất bại."
//       console.error("Error auto-grading submission:", err)
//       throw err
//     } finally {
//       isLoading.value = false
//     }
//   }

//   // Call loadSettings when the store is created
//   loadSettings()

//   return {
//     settings,
//     isLoading,
//     error,
//     successMessage,
//     updateSettings,
//     autoGradeSubmission,
//   }
// })
