import { defineStore } from "pinia"
import { ref } from "vue"
import { aiService } from "@/services/aiService"

export const useChatbotStore = defineStore("chatbot", () => {
  const messages = ref([])
  const isTyping = ref(false)
  const error = ref(null)

  const addMessage = (message) => {
    messages.value.push(message)
  }

  const sendMessageToBot = async (userMessage) => {
    isTyping.value = true
    error.value = null
    try {
      const response = await aiService.chatWithBot(userMessage)
      addMessage({ sender: "bot", text: response.reply || "Xin lỗi, tôi không hiểu câu hỏi của bạn." })
    } catch (err) {
      error.value = err.response?.data?.message || "Có lỗi xảy ra khi kết nối với AI Assistant."
      addMessage({ sender: "bot", text: "Xin lỗi, tôi đang gặp sự cố. Vui lòng thử lại sau." })
      console.error("Error sending message to bot:", err)
    } finally {
      isTyping.value = false
    }
  }

  return {
    messages,
    isTyping,
    error,
    addMessage,
    sendMessageToBot,
  }
})
