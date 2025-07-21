<template>
  <div class="max-w-5xl mx-auto p-6 space-y-6">
    <h1 class="text-3xl font-bold text-center text-gray-800">
      📚 Danh sách Khóa học
    </h1>

    <!-- Danh sách khóa học -->
    <div v-if="courses.length > 0" class="space-y-4">
      <button
        v-for="course in courses"
        :key="course.id"
        @click="selectCourse(course)"
        class="w-full bg-yellow-100 hover:bg-yellow-200 px-4 py-2 rounded-lg text-left font-semibold text-gray-800 shadow-sm"
      >
        🏫 {{ course.title }} ({{ course.teacher_name }})
      </button>
    </div>
    <p v-else class="text-gray-500 text-center">Không có khóa học nào.</p>

    <!-- Danh sách bài giảng -->
    <div v-if="selectedCourse" class="space-y-4">
      <h2 class="text-2xl font-semibold text-center text-gray-700">
        📖 Bài giảng của khóa học: {{ selectedCourse.title }}
      </h2>
      <button
        v-for="lesson in lessons"
        :key="lesson.id"
        @click="fetchExercises(lesson.id)"
        class="w-full bg-blue-100 hover:bg-blue-200 px-4 py-2 rounded-lg text-left font-semibold text-gray-800 shadow-sm"
      >
        {{ lesson.order }}. {{ lesson.title }}
      </button>
    </div>

    <!-- Danh sách bài tập -->
    <div v-if="exercises.length > 0" class="space-y-4">
      <h2 class="text-2xl font-semibold text-center text-gray-700">
        📋 Danh sách Bài tập
      </h2>
      <div
        v-for="exercise in exercises"
        :key="exercise.id"
        class="p-4 bg-white rounded-lg border shadow-sm"
      >
        <h2 class="font-bold text-gray-800">{{ exercise.title }}</h2>
        <p class="text-sm text-gray-600">{{ exercise.description }}</p>
        <p class="text-sm text-gray-500">Loại: {{ exercise.exercise_type }}</p>

        <button
          @click="openSubmitForm(exercise.id)"
          class="mt-2 bg-green-600 hover:bg-green-700 text-white font-semibold px-4 py-1 rounded-md"
        >
          Nộp bài
        </button>
      </div>
    </div>

    <!-- Form nộp bài -->
    <div v-if="showSubmitForm" class="p-4 bg-gray-100 rounded-md border">
      <h3 class="font-bold mb-2">Nộp bài cho bài tập ID: {{ submitExerciseId }}</h3>
      <textarea
        v-model="submissionContent"
        rows="5"
        class="w-full border rounded-md p-2"
        placeholder="Nhập bài làm (code hoặc nội dung khác)"
      ></textarea>
      <div class="mt-2 flex space-x-2">
        <button
          @click="submitExercise"
          class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1 rounded-md"
        >
          Gửi bài
        </button>
        <button
          @click="showSubmitForm = false"
          class="bg-gray-400 hover:bg-gray-500 text-white px-4 py-1 rounded-md"
        >
          Hủy
        </button>
      </div>

      <div v-if="submitFeedback" class="mt-4 p-3 bg-white rounded-md border">
        <p>{{ submitFeedback }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_BASE = 'http://127.0.0.1:5000/api'

const courses = ref([])
const selectedCourse = ref(null)
const lessons = ref([])
const exercises = ref([])

const showSubmitForm = ref(false)
const submitExerciseId = ref(null)
const submissionContent = ref('')
const submitFeedback = ref('')

const fetchCourses = async () => {
  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/courses`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (res.ok) {
    courses.value = await res.json()
  }
}

const selectCourse = async (course) => {
  selectedCourse.value = course
  exercises.value = []
  showSubmitForm.value = false

  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/courses/${course.id}`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  if (res.ok) {
    const data = await res.json()
    lessons.value = data.lessons || []
  }
}

const fetchExercises = async (lessonId) => {
  exercises.value = []
  showSubmitForm.value = false

  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/exercise/lessons/${lessonId}/exercises`, {
    headers: { Authorization: `Bearer ${token}` }
  })

  if (res.ok) {
    const data = await res.json()
    exercises.value = data.exercises || []
  }
}

const openSubmitForm = (exerciseId) => {
  submitExerciseId.value = exerciseId
  submissionContent.value = ''
  submitFeedback.value = ''
  showSubmitForm.value = true
}

const submitExercise = async () => {
  if (!submissionContent.value.trim()) {
    alert('Vui lòng nhập bài làm.')
    return
  }

  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/exercise/exercises/${submitExerciseId.value}/submit`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ content: submissionContent.value })
  })

  if (res.ok) {
    const data = await res.json()
    submitFeedback.value = data.message || 'Đã nộp bài thành công.'
  } else {
    submitFeedback.value = 'Lỗi khi nộp bài.'
  }
}

onMounted(fetchCourses)
</script>
