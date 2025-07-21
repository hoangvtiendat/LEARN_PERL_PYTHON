<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6">Chào mừng, {{ user?.full_name || 'Học sinh' }}!</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <!-- Card: Khóa học của tôi -->
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold mb-2">Khóa học của tôi</h2>
        <p class="text-gray-600 mb-4">Tiếp tục học các khóa học bạn đã đăng ký.</p>
        <router-link
          to="/courses"
          class="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors"
        >
          Xem khóa học
        </router-link>
      </div>

      <!-- Card: Bài tập của tôi -->
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold mb-2">Bài tập của tôi</h2>
        <p class="text-gray-600 mb-4">Kiểm tra các bài tập sắp tới và nộp bài.</p>
        <router-link
          to="/assignments"
          class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
        >
          Xem bài tập
        </router-link>
      </div>

      <!-- Card: IDE Online -->
      <div class="bg-white p-6 rounded-lg shadow-md">
        <h2 class="text-xl font-semibold mb-2">IDE Online</h2>
        <p class="text-gray-600 mb-4">Thực hành code trực tiếp trên trình duyệt.</p>
        <router-link
          to="/ide"
          class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
        >
          Mở IDE
        </router-link>
      </div>

      <!-- Card: Thông báo gần đây -->
      <div class="bg-white p-6 rounded-lg shadow-md col-span-1 md:col-span-2 lg:col-span-3">
        <h2 class="text-xl font-semibold mb-4">Thông báo gần đây</h2>
        <ul class="list-disc list-inside text-gray-700">
          <li v-if="notifications.length === 0">Không có thông báo mới.</li>
          <li v-for="(notify, idx) in notifications" :key="idx">
            {{ notify }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const authStore = useAuthStore()
const user = ref(null)
const notifications = ref([])

// Gọi API khi component mount
onMounted(async () => {
  try {
    const token = localStorage.getItem('access_token')
    const headers = {
      Authorization: `Bearer ${token}`
    }

    // Lấy thông tin người dùng từ authStore (nếu chưa có thì fetch lại)
    user.value = authStore.user

    // Gọi API lấy danh sách khóa học đã ghi danh (giả sử backend có filter theo user)
    const coursesRes = await axios.get('/api/courses', { headers })

    // Cập nhật thông báo (demo: liệt kê tên khóa học vừa ghi danh)
    notifications.value = coursesRes.data.map(course => `Bạn đã ghi danh khóa học: ${course.title}`)

  } catch (error) {
    console.error('Lỗi khi tải dữ liệu dashboard:', error)
  }
})
</script>
