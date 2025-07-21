<template>
  <nav class="bg-gray-800 p-4 text-white flex justify-between items-center">
    <div class="tilte">
      <router-link to="/dashboard" class="text-xl font-bold">E‑Learning</router-link>
    </div>
    <div class="flex items-center space-x-4">
      <div class="ml-6 space-x-4">
        <!-- Dashboard hiển thị theo vai trò -->
        <router-link v-if="isStudent" to="/dashboard" class="hover:text-gray-300">Dashboard</router-link>
        <router-link v-if="isTeacherOrAdmin" to="/teacher-dashboard" class="hover:text-gray-300">Dashboard</router-link>
        
        <!-- Các mục chung cho tất cả người dùng đã đăng nhập -->
        <router-link v-if="isAuthenticated" to="/courses" class="hover:text-gray-300">Khóa học</router-link>
        <router-link v-if="isAuthenticated" to="/assignments" class="hover:text-gray-300">Bài tập</router-link>
        <router-link v-if="isTeacherOrAdmin" to="/grading/1/1" class="hover:text-gray-300">QL Bài Tập & Chấm điểm</router-link>
        <router-link v-if="isAdmin" to="/admin/users" class="hover:text-gray-300">Người dùng</router-link>
        <router-link v-if="isAdmin" to="/admin/reports" class="hover:text-gray-300">Báo cáo</router-link>
        <router-link v-if="isAuthenticated" to="/ide" class="hover:text-gray-300">IDE</router-link>
        <router-link
            v-if="isStudent"
            to="/notifications"
            class="relative hover:text-gray-300"
          >
            🔔
            <span
              v-if="unreadCount > 0"
              class="absolute -top-2 -right-3 bg-red-600 text-white text-xs rounded-full px-1"
            >
              {{ unreadCount }}
            </span>
          </router-link>
      </div>
    </div>

    <div class="flex items-center space-x-4">
      <router-link
        v-if="isAuthenticated"
        to="/profile"
        class="hover:text-gray-300"
      >
        Chào, {{ authStore.user.full_name || authStore.user.email }}
      </router-link>

      <button
        v-if="isAuthenticated"
        @click="logout"
        class="bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded"
      >
        Đăng xuất
      </button>

      <!-- Nếu chưa đăng nhập -->
      <div v-else class="space-x-2">
        <router-link to="/login" class="hover:text-gray-300">Đăng nhập</router-link>
        <router-link to="/register" class="bg-blue-500 hover:bg-blue-600 text-white py-1 px-3 rounded">Đăng ký</router-link>
      </div>
    </div>
  </nav>
</template>

<script setup>

import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ref, computed, onMounted } from 'vue'
const notifications = ref([])

const fetchNotifications = async () => {
  if (!isStudent.value) return
  const res = await fetch('http://127.0.0.1:5000/api/notifications', {
    headers: { Authorization: `Bearer ${token}` }
  })
  notifications.value = await res.json()
}

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)

onMounted(() => {
  fetchNotifications()
})
const router = useRouter()
const authStore = useAuthStore()

// Trạng thái đăng nhập & vai trò
const isAuthenticated = computed(() => authStore.isAuthenticated)
const role = computed(() => authStore.user?.role)
const isStudent = computed(() => role.value === 'student')
const isTeacher = computed(() => role.value === 'teacher')
const isAdmin = computed(() => role.value === 'admin')
const isTeacherOrAdmin = computed(() => isTeacher.value || isAdmin.value)

const logout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>
<style scoped>
/* Tông màu chính */
:root {
  --primary-color: #1b2a4e; /* Xanh navy */
  --primary-hover: #253a6c;
  --accent-color: #4f83ff; /* Xanh nhạt hỗ trợ */
  --text-light: #ffffff;
  --text-muted: #b0b8d1;
  --danger-color: #e63946;
}
nav a[data-v-9eba1f0e] {
    color: var(--text-light);
    font-weight: 500;
    background-color: #3a4357;
    border-radius: 6px;
    padding: 9px 14px;
    border: 1px solid #252525;
    transition: color 0.2s ease;
}
body {
  font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
  background-color: #e8e8e8;
  color: #ccc6c6;
}

/* Thanh điều hướng */
nav {
  background-color: rgb(39, 39, 39);
  padding: 1rem 2rem;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

nav a {
  color: var(--text-light);
  font-weight: 500;
  transition: color 0.2s ease;
}

nav a:hover {
  color: var(--text-muted);
}

/* Button style */
button {
  font-weight: 500;
}

button.bg-red-500 {
  background-color: var(--danger-color);
}

button.bg-red-500:hover {
  background-color: #b82330;
}

.router-link-active {
  border-bottom: 2px solid var(--accent-color);
}

/* Đăng ký button */
nav .bg-blue-500 {
  background-color: var(--accent-color);
}

nav .bg-blue-500:hover {
  background-color: #356eff;
}

/* Responsive nav */
@media (max-width: 768px) {
  nav {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
