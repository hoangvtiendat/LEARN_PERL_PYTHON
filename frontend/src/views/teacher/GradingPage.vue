<template>
  <div class="max-w-6xl mx-auto p-6 space-y-8">
    <h1 class="text-3xl font-bold text-center">📚 Quản lý Bài tập & Chấm điểm</h1>

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
    <div v-if="lessons.length">
      <label class="font-semibold">Chọn bài giảng:</label>
      <select v-model="selectedLessonId" @change="fetchExercises" class="border p-2 rounded w-1/3">
        <option disabled value="">-- Chọn bài giảng --</option>
        <option v-for="lesson in lessons" :key="lesson.id" :value="lesson.id">
          {{ lesson.title }}
        </option>
      </select>
    </div>

    <!-- 3️⃣ Thêm / Sửa bài tập -->
    <div v-if="selectedLessonId">
      <h2 class="font-bold mt-6 mb-2">🛠️ {{ editingExerciseId ? 'Sửa' : 'Thêm' }} Bài tập</h2>

      <input v-model="form.title" placeholder="Tiêu đề"
        class="w-full border p-2 rounded mb-2"/>

      <textarea v-model="form.description" placeholder="Mô tả"
        class="w-full border p-2 rounded mb-2"></textarea>

      <label class="block font-semibold mb-1">Loại bài tập:</label>
      <select v-model="form.exercise_type" class="w-full border p-2 rounded mb-4">
        <option disabled value="">-- Chọn loại bài tập --</option>
        <option value="CODE">CODE</option>
        <option value="TEXT">TEXT</option>
      </select>

      <button @click="saveExercise"
        class="bg-green-600 text-white px-4 py-2 rounded">
        {{ editingExerciseId ? 'Cập nhật' : 'Thêm mới' }}
      </button>

      <button v-if="editingExerciseId"
        @click="cancelEdit"
        class="ml-2 bg-gray-400 text-white px-4 py-2 rounded">
        Hủy
      </button>
    </div>

    <!-- 4️⃣ Danh sách bài tập -->
    <div v-if="exercises.length" class="space-y-4">
      <h2 class="font-bold text-lg mt-8">📄 Danh sách Bài tập</h2>
      <div v-for="exercise in exercises" :key="exercise.id"
        class="p-4 bg-white rounded border shadow">
        <h3 class="font-semibold">{{ exercise.title }}</h3>
        <p>{{ exercise.description }}</p>

        <div class="flex space-x-2 mt-2">
          <button @click="openEditForm(exercise)"
            class="bg-yellow-500 text-white px-3 py-1 rounded">Sửa</button>
          <button @click="deleteExercise(exercise.id)"
            class="bg-red-600 text-white px-3 py-1 rounded">Xóa</button>
          <button @click="viewSubmissions(exercise.id)"
            class="bg-blue-600 text-white px-3 py-1 rounded">Xem bài nộp</button>
        </div>
      </div>
    </div>

    <!-- 5️⃣ Danh sách bài nộp -->
    <div v-if="submissions.length || submissionsChecked" class="space-y-4 mt-6">
      <h2 class="font-bold text-xl">📋 Danh sách Bài nộp</h2>
      <div v-if="submissions.length === 0" class="text-gray-600 italic">
        ⚠️ Hiện chưa có bài nộp cho bài tập này.
      </div>

      <div v-for="sub in submissions" :key="sub.id"
        class="p-4 bg-white rounded border">
        <p class="font-semibold">👤 Học viên: {{ sub.student_name || 'Ẩn danh' }}</p>
        <pre class="bg-gray-100 p-2 rounded text-sm">{{ sub.content }}</pre>

        <div class="mt-2">
          <label class="block font-semibold">Điểm:</label>
          <input v-model="sub.score" type="number" min="0" max="10"
            class="w-20 border p-1 rounded mb-2"/>

          <label class="block font-semibold">Phản hồi:</label>
          <textarea v-model="sub.feedback" rows="2"
            class="w-full border rounded p-2 mb-2"></textarea>

          <button @click="submitGrade(sub)"
            class="bg-green-600 text-white px-4 py-1 rounded">
            Gửi điểm
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const token = localStorage.getItem('token')

const courses = ref([])
const lessons = ref([])
const exercises = ref([])
const submissions = ref([])

const submissionsChecked = ref(false)

const selectedCourseId = ref('')
const selectedLessonId = ref('')

const form = ref({ title: '', description: '', exercise_type: '' })
const editingExerciseId = ref(null)

const fetchCourses = async () => {
  const res = await fetch('http://127.0.0.1:5000/api/courses', {
    headers: { Authorization: `Bearer ${token}` }
  })
  courses.value = await res.json()
}

const fetchLessons = async () => {
  lessons.value = []
  exercises.value = []
  submissions.value = []
  submissionsChecked.value = false
  selectedLessonId.value = ''

  const res = await fetch(`http://127.0.0.1:5000/api/courses/${selectedCourseId.value}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const data = await res.json()
  lessons.value = data.lessons || []
}

const fetchExercises = async () => {
  exercises.value = []
  submissions.value = []
  submissionsChecked.value = false

  const res = await fetch(`http://127.0.0.1:5000/api/exercise/lessons/${selectedLessonId.value}/exercises`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const data = await res.json()
  exercises.value = data.exercises || []
}

const saveExercise = async () => {
  const url = editingExerciseId.value
    ? `http://127.0.0.1:5000/api/exercise/exercises/${editingExerciseId.value}`
    : `http://127.0.0.1:5000/api/exercise/lessons/${selectedLessonId.value}/exercises`
  const method = editingExerciseId.value ? 'PUT' : 'POST'

  await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify(form.value)
  })

  form.value = { title: '', description: '', exercise_type: '' }
  editingExerciseId.value = null
  fetchExercises()
}

const openEditForm = (exercise) => {
  form.value = {
    title: exercise.title,
    description: exercise.description,
    exercise_type: exercise.exercise_type
  }
  editingExerciseId.value = exercise.id
}

const cancelEdit = () => {
  editingExerciseId.value = null
  form.value = { title: '', description: '', exercise_type: '' }
}

const deleteExercise = async (id) => {
  if (!confirm('Bạn có chắc muốn xóa bài tập này?')) return
  await fetch(`http://127.0.0.1:5000/api/exercise/exercises/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` }
  })
  fetchExercises()
}

const viewSubmissions = async (exerciseId) => {
  submissionsChecked.value = false
  submissions.value = []

  const res = await fetch(`http://127.0.0.1:5000/api/exercise/exercises/${exerciseId}/submissions`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const data = await res.json()
  submissions.value = data.submissions || []
  submissionsChecked.value = true
}

const submitGrade = async (sub) => {
  await fetch(`http://127.0.0.1:5000/api/exercise/submissions/${sub.id}/grade`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      score: sub.score,
      feedback: sub.feedback
    })
  })
  alert('Đã chấm điểm!')
}

onMounted(() => {
  fetchCourses()
})
</script>
