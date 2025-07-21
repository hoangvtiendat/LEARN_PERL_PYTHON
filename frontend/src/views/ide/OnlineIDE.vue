<template>
  <div class="max-w-5xl mx-auto p-6 space-y-6">
    <h1 class="text-3xl font-bold text-center text-gray-800">
      Trình biên dịch & Gợi ý sửa lỗi
    </h1>

    <!-- Select Language -->
    <div>
      <label class="block mb-1 text-sm font-semibold text-gray-700">Ngôn ngữ</label>
      <select
        v-model="language"
        class="w-full md:w-1/3 px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="python">Python</option>
        <option value="perl">Perl</option>
      </select>
    </div>

    <!-- IDE Editor -->
    <div>
      <label class="block mb-1 text-sm font-semibold text-gray-700">Viết mã nguồn của bạn</label>
      <textarea
        v-model="code"
        rows="12"
        placeholder="Viết mã Python hoặc Perl ở đây..."
        class="w-full p-4 font-mono text-sm border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      ></textarea>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-wrap items-center gap-4">
      <button
        @click="handleRun"
        :disabled="loading"
        class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-5 py-2 rounded-md disabled:opacity-50"
      >
        {{ loading ? 'Đang chạy...' : 'Chạy mã' }}
      </button>

      <button
        @click="handleFix"
        :disabled="loading || !code"
        class="bg-green-600 hover:bg-green-700 text-white font-semibold px-5 py-2 rounded-md disabled:opacity-50"
      >
        {{ loading ? 'Đang gợi ý...' : 'Gợi ý sửa lỗi' }}
      </button>

      <span v-if="error" class="text-red-600 text-sm">{{ error }}</span>
    </div>

    <!-- Output -->
    <div v-if="output" class="bg-gray-100 border border-gray-300 rounded-lg p-4">
      <h2 class="text-lg font-semibold mb-2 text-gray-800">Kết quả chạy mã</h2>
      <pre class="bg-white p-3 rounded-md overflow-auto text-sm text-gray-800 whitespace-pre-wrap">
{{ output }}
      </pre>
    </div>

    <!-- Suggestion -->
    <div v-if="suggestion" class="bg-yellow-50 border border-yellow-300 rounded-lg p-4">
      <h2 class="text-lg font-semibold mb-2 text-yellow-800">Gợi ý sửa lỗi</h2>
      <pre class="bg-white p-3 rounded-md overflow-auto text-sm text-yellow-800 whitespace-pre-wrap">
{{ suggestion }}
      </pre>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { suggestFix } from '@/services/aiService'

const code = ref('')
const language = ref('python')
const output = ref('')
const suggestion = ref('')
const error = ref('')
const loading = ref(false)

// Gọi thẳng API /execute để chạy code
const handleRun = async () => {
  loading.value = true
  error.value = ''
  output.value = ''
  suggestion.value = ''

  try {
    const token = localStorage.getItem('token')

    const res = await axios.post(
      'http://127.0.0.1:5000/api/ide/execute',
      { code: code.value, language: language.value },
      {
        headers: {
          Authorization: `Bearer ${token}`
        }
      }
    )

    const result = res.data

    output.value =
      (result.stdout || '') +
      (result.stderr ? '\n' + result.stderr : '') +
      (result.status ? '\n\nTrạng thái: ' + result.status : '')

  } catch (err) {
    error.value = err.response?.data?.error || 'Lỗi khi chạy mã.'
    console.error(err)
  } finally {
    loading.value = false
  }
}

// Gọi AI từ file aiService.js
const handleFix = async () => {
  loading.value = true
  error.value = ''
  suggestion.value = ''

  try {
    const res = await suggestFix(code.value, language.value)
    suggestion.value = res.data?.suggestion || 'Không có gợi ý nào.'
  } catch (err) {
    error.value = err.response?.data?.error || 'Lỗi khi gợi ý sửa lỗi.'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>
