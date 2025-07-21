<template>
  <div class="p-8 space-y-8">
    <h2 class="text-3xl font-bold text-gray-800">📚 Quản lý Khóa học</h2>

    <!-- Tạo hoặc sửa khóa học -->
    <div class="bg-white shadow-md p-6 rounded-md border border-gray-200">
      <h3 class="text-xl font-semibold mb-4 text-blue-600">
        {{ isEditing ? '🛠️ Sửa khóa học' : '➕ Tạo khóa học mới' }}
      </h3>

      <input
        v-model="newCourse.title"
        placeholder="📌 Tên khóa học"
        class="w-full border border-gray-300 p-2 mb-3 rounded focus:ring focus:outline-none"
      />
      <textarea
        v-model="newCourse.description"
        placeholder="📝 Mô tả khóa học"
        class="w-full border border-gray-300 p-2 mb-3 rounded focus:ring focus:outline-none"
      ></textarea>

      <button
        @click="isEditing ? updateCourse() : createNewCourse()"
        class="bg-blue-600 hover:bg-blue-700 text-white py-2 px-6 rounded font-medium"
      >
        {{ isEditing ? 'Cập nhật' : 'Tạo' }}
      </button>

      <button
        v-if="isEditing"
        @click="cancelEdit"
        class="ml-4 bg-gray-300 hover:bg-gray-400 text-black py-2 px-6 rounded font-medium"
      >
        Hủy
      </button>
    </div>

    <!-- Danh sách khóa học -->
    <div v-if="courses.length > 0" class="grid grid-cols-1 gap-6">
      <div
        v-for="course in courses"
        :key="course.id"
        class="bg-white shadow-md p-6 rounded-md border border-gray-200"
      >
        <h4 class="text-xl font-bold text-gray-800 mb-2">📌{{ course.title }}</h4>
        <p class="text-gray-700 mb-4 whitespace-pre-line">
          {{ course.description || '— Không có mô tả —' }}
        </p>
        <button
          @click="startEditCourse(course)"
          class="bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-1 rounded mr-2"
        >
          🛠️ Sửa
        </button>
        <button
          @click="deleteExistingCourse(course.id)"
          class="bg-red-500 hover:bg-red-600 text-white px-4 py-1 rounded"
        >
          🗑️ Xóa
        </button>
      </div>
    </div>

    <p v-else class="text-gray-500">⚠️ Chưa có khóa học nào.</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const courses = ref([])
const newCourse = ref({ title: '', description: '' })
const isEditing = ref(false)
const editingCourseId = ref(null)

const fetchCourses = async () => {
  const res = await fetch('http://127.0.0.1:5000/api/courses', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  const data = await res.json()
  courses.value = data
}

onMounted(() => {
  fetchCourses()
})

const createNewCourse = async () => {
  if (!newCourse.value.title.trim()) return alert('Nhập tên khóa học!')

  await fetch('http://127.0.0.1:5000/api/courses', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(newCourse.value)
  })

  newCourse.value = { title: '', description: '' }
  fetchCourses()
  alert('Khóa học đã được tạo thành công!')
}

const deleteExistingCourse = async (id) => {
  if (confirm('Bạn chắc chắn muốn xóa khóa học này?')) {
    await fetch(`http://127.0.0.1:5000/api/courses/${id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    fetchCourses()
  }
}

const startEditCourse = (course) => {
  isEditing.value = true
  editingCourseId.value = course.id
  newCourse.value = { title: course.title, description: course.description }
}

const updateCourse = async () => {
  if (!newCourse.value.title.trim()) return alert('Nhập tên khóa học!')

  await fetch(`http://127.0.0.1:5000/api/courses/${editingCourseId.value}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(newCourse.value)
  })

  cancelEdit()
  fetchCourses()
  alert('Khóa học đã được cập nhật thành công!')
}

const cancelEdit = () => {
  isEditing.value = false
  editingCourseId.value = null
  newCourse.value = { title: '', description: '' }
}
</script>
