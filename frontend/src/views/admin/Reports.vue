<template>
  <div class="max-w-5xl mx-auto p-6 space-y-6">
    <h1 class="text-2xl font-bold text-center text-blue-800">📊 Báo cáo Bài tập</h1>

    <!-- 1️⃣ Chọn khóa học -->
    <div>
      <label class="font-semibold">Chọn khóa học:</label>
      <select v-model="selectedCourseId" @change="fetchLessons" class="border p-2 rounded w-1/3">
        <option disabled value="">-- Chọn khóa học --</option>
        <option v-for="course in courses" :key="course.id" :value="course.id">
          {{ course.title }}
        </option>
      </select>
    </div>

    <!-- 2️⃣ Chọn bài giảng -->
    <div v-if="lessons.length > 0">
      <label class="font-semibold">Chọn bài giảng:</label>
      <select v-model="selectedLessonId" @change="fetchExercises" class="border p-2 rounded w-1/3">
        <option disabled value="">-- Chọn bài giảng --</option>
        <option v-for="lesson in lessons" :key="lesson.id" :value="lesson.id">
          {{ lesson.title }}
        </option>
      </select>
    </div>

    <!-- 3️⃣ Chọn bài tập -->
    <div v-if="exercises.length > 0">
      <label class="font-semibold">Chọn bài tập:</label>
      <select v-model="selectedExerciseId" class="border p-2 rounded w-1/3">
        <option disabled value="">-- Chọn bài tập --</option>
        <option v-for="ex in exercises" :key="ex.id" :value="ex.id">
          {{ ex.title }}
        </option>
      </select>
      <div class="mt-4">
        <button @click="fetchReport" class="bg-blue-600 text-white px-4 py-2 rounded">
          Xem báo cáo
        </button>
        <button v-if="report.length > 0" @click="exportReport" class="ml-2 bg-green-600 text-white px-4 py-2 rounded">
          Xuất CSV
        </button>
      </div>
    </div>

    <!-- 4️⃣ Báo cáo -->
    <div v-if="isLoading" class="text-center text-gray-500">Đang tải báo cáo...</div>
    <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>

    <div v-else-if="report.length > 0" class="overflow-x-auto bg-white shadow rounded">
      <table class="min-w-full border">
        <thead class="bg-gray-100">
          <tr>
            <th class="p-2">Student ID</th>
            <th class="p-2">Email</th>
            <th class="p-2">Score</th>
            <th class="p-2">Status</th>
            <th class="p-2">Submitted At</th>
            <th class="p-2">Feedback</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sub in report" :key="sub.student_id" class="border-t">
            <td class="p-2">{{ sub.student_id }}</td>
            <td class="p-2">{{ sub.student_email }}</td>
            <td class="p-2">{{ sub.score }}</td>
            <td class="p-2">{{ sub.status }}</td>
            <td class="p-2">{{ sub.submitted_at }}</td>
            <td class="p-2 text-sm">{{ sub.feedback }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else-if="selectedExerciseId" class="text-center text-gray-500">
      Không có bài nộp nào cho bài tập này.
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const token = localStorage.getItem('token')
const API = 'http://127.0.0.1:5000/api'

const courses = ref([])
const lessons = ref([])
const exercises = ref([])

const selectedCourseId = ref('')
const selectedLessonId = ref('')
const selectedExerciseId = ref('')

const report = ref([])
const isLoading = ref(false)
const error = ref(null)

const fetchCourses = async () => {
  const res = await fetch(`${API}/courses`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  courses.value = await res.json()
}

const fetchLessons = async () => {
  lessons.value = []
  exercises.value = []
  selectedLessonId.value = ''
  selectedExerciseId.value = ''
  report.value = []

  const res = await fetch(`${API}/courses/${selectedCourseId.value}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const data = await res.json()
  lessons.value = data.lessons || []
}

const fetchExercises = async () => {
  exercises.value = []
  selectedExerciseId.value = ''
  report.value = []

  const res = await fetch(`${API}/exercise/lessons/${selectedLessonId.value}/exercises`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const data = await res.json()
  exercises.value = data.exercises || []
}

const fetchReport = async () => {
  if (!selectedExerciseId.value) return

  isLoading.value = true
  error.value = null
  report.value = []

  try {
    const res = await fetch(`${API}/report/exercise/${selectedExerciseId.value}/report`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (!res.ok) {
      const errData = await res.json()
      error.value = errData.error || 'Không thể tải báo cáo.'
    } else {
      const data = await res.json()
      report.value = data.submissions || []
    }
  } catch (err) {
    error.value = 'Lỗi kết nối.'
  } finally {
    isLoading.value = false
  }
}

const exportReport = async () => {
  const res = await fetch(`${API}/report/exercise/${selectedExerciseId.value}/report/export`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const blob = await res.blob()
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `exercise_${selectedExerciseId.value}_report.csv`
  link.click()
  window.URL.revokeObjectURL(url)
}

onMounted(() => {
  fetchCourses()
})
</script>

<style scoped>
table th,
table td {
  border: 1px solid #ddd;
  text-align: left;
}
</style>
