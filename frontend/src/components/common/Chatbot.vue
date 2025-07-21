<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">Trợ lý học tập AI</h1>

    <div class="flex space-x-4 mb-4">
      <button
        class="px-4 py-2 rounded text-white"
        :class="mode === 'chat' ? 'bg-blue-600' : 'bg-gray-400'"
        @click="mode = 'chat'"
      >
        Chatbot
      </button>
      <button
        class="px-4 py-2 rounded text-white"
        :class="mode === 'quiz' ? 'bg-blue-600' : 'bg-gray-400'"
        @click="mode = 'quiz'"
      >
        Sinh câu hỏi
      </button>
    </div>

    <!-- Chatbot -->
    <div v-if="mode === 'chat'" class="bg-white p-4 rounded shadow">
      <div class="mb-4">
        <label class="block font-medium mb-1">Nhập câu hỏi cho AI:</label>
        <textarea
          v-model="chatInput"
          rows="3"
          class="w-full border rounded p-2"
          placeholder="Ví dụ: Giải thích vòng lặp while trong Python"
        />
      </div>
      <button
        @click="sendQuestion"
        class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded"
        :disabled="chatLoading"
      >
        {{ chatLoading ? 'Đang gửi...' : 'Gửi câu hỏi' }}
      </button>

      <div v-if="chatResponse" class="mt-4 bg-gray-100 p-3 rounded whitespace-pre-wrap">
        <strong>Phản hồi:</strong>
        <div v-html="chatResponse"></div>
      </div>
    </div>

    <!-- Sinh câu hỏi -->
    <div v-else class="bg-white p-4 rounded shadow">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div>
          <label class="block font-medium mb-1">Chủ đề:</label>
          <input
            v-model="quizTopic"
            class="w-full border rounded px-2 py-1"
            placeholder="VD: biến, vòng lặp, hàm..."
          />
        </div>
        <div>
          <label class="block font-medium mb-1">Độ khó:</label>
          <select v-model="quizDifficulty" class="w-full border rounded px-2 py-1">
            <option value="dễ">Dễ</option>
            <option value="trung bình">Trung bình</option>
            <option value="khó">Khó</option>
          </select>
        </div>
        <div class="flex items-end">
          <button
            @click="handleGenerateQuestions"
            class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded w-full"
            :disabled="quizLoading"
          >
            {{ quizLoading ? 'Đang tạo...' : 'Tạo câu hỏi' }}
          </button>
        </div>
      </div>

      <div v-if="quizQuestions.length" class="space-y-4 mt-4">
        <div
          v-for="(q, idx) in quizQuestions"
          :key="idx"
          class="bg-gray-50 border rounded p-3"
        >
          <h3 class="font-semibold mb-1">{{ idx + 1 }}. {{ q.question_text }}</h3>
          <ul class="ml-4 list-disc text-sm text-gray-700">
            <li v-for="(opt, i) in q.options" :key="i">
              {{ String.fromCharCode(65 + i) }}. {{ opt }}
            </li>
          </ul>
          <p class="text-green-600 mt-2">✅ Đáp án đúng: {{ q.correct_answer }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { askChatbot, generateQuestions as apiGenerateQuestions } from '@/services/aiService'

const mode = ref('chat') // 'chat' | 'quiz'

const chatInput = ref('')
const chatResponse = ref('')
const chatLoading = ref(false)

const quizTopic = ref('')
const quizDifficulty = ref('dễ')
const quizQuestions = ref([])
const quizLoading = ref(false)

const sendQuestion = async () => {
  if (!chatInput.value.trim()) return
  chatLoading.value = true
  chatResponse.value = ''
  try {
    const res = await askChatbot(chatInput.value)
    chatResponse.value = res.data.answer
  } catch (err) {
    chatResponse.value = '❌ Lỗi: ' + (err.response?.data?.error || 'Không thể kết nối với AI.')
    console.error(err)
  } finally {
    chatLoading.value = false
  }
}

const handleGenerateQuestions = async () => {
  if (!quizTopic.value.trim()) return
  quizLoading.value = true
  quizQuestions.value = []
  try {
    const res = await apiGenerateQuestions(quizTopic.value, quizDifficulty.value, 3)
    quizQuestions.value = res.data.questions || []
  } catch (err) {
    quizQuestions.value = []
    alert('Không thể tạo câu hỏi: ' + (err.response?.data?.error || 'Lỗi không xác định.'))
    console.error(err)
  } finally {
    quizLoading.value = false
  }
}
</script>

<style scoped>
/* chatbot-business.css */
:root {
  --navy: #1a2a4f;
  --navy-light: #2d3e6b;
  --navy-dark: #142040;
  --white: #fff;
  --gray: #f5f7fa;
  --border: #e3e8ee;
  --primary: var(--navy);
  --primary-hover: var(--navy-light);
  --success: #1abc9c;
}

body {
  background: var(--gray);
  font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
  color: var(--navy-dark);
}

.container {
  background: var(--white);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(26, 42, 79, 0.08);
  padding: 32px;
  margin-top: 32px;
}

h1 {
  color: var(--primary);
  letter-spacing: 1px;
}

button {
  background: var(--primary);
  color: var(--white);
  border: none;
  border-radius: 6px;
  transition: background 0.2s;
  font-weight: 500;
  cursor: pointer;
}

button:hover:not(:disabled) {
  background: var(--primary-hover);
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

input, select, textarea {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 1rem;
  background: var(--gray);
  transition: border 0.2s;
}

input:focus, select:focus, textarea:focus {
  border-color: var(--primary);
  outline: none;
}

.bg-white {
  background: var(--white);
}

.bg-gray-100, .bg-gray-50 {
  background: var(--gray);
}

.text-blue-600, .bg-blue-600 {
  color: white;
  background: var(--primary) !important;
}

.text-green-600 {
  color: var(--success) !important;
}

.shadow {
  box-shadow: 0 2px 8px rgba(26, 42, 79, 0.06);
}

.rounded {
  border-radius: 8px;
}

.list-disc {
  list-style-type: disc;
}

.font-bold {
  font-weight: bold;
}

.font-medium {
  font-weight: 500;
}

.whitespace-pre-wrap {
  white-space: pre-wrap;
}
</style>
