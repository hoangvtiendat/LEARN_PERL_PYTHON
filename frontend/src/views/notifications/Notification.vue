<template>
  <div class="p-6 max-w-3xl mx-auto bg-white shadow rounded">
    <h2 class="text-xl font-bold mb-4">🔔 Thông báo của bạn</h2>

    <div v-if="notifications.length === 0" class="text-gray-500">
      Không có thông báo nào.
    </div>

    <ul v-else class="space-y-4">
      <li v-for="noti in notifications" :key="noti.id" class="border p-4 rounded shadow-sm">
        <p :class="noti.is_read ? 'text-gray-700' : 'font-semibold text-blue-600'">
          {{ noti.message }}
        </p>
        <small class="text-gray-500">{{ new Date(noti.created_at).toLocaleString() }}</small>
        <div v-if="!noti.is_read" class="mt-2">
          <button
            @click="markAsRead(noti.id)"
            class="bg-blue-600 text-white px-3 py-1 rounded"
          >
            Đánh dấu đã đọc
          </button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const notifications = ref([])
const token = localStorage.getItem('token')

const fetchNotifications = async () => {
  const res = await fetch('http://127.0.0.1:5000/api/notifications', {
    headers: { Authorization: `Bearer ${token}` }
  })
  notifications.value = await res.json()
}

const markAsRead = async (id) => {
  await fetch(`http://127.0.0.1:5000/api/notifications/mark_read/${id}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` }
  })
  fetchNotifications()
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
ul {
  list-style: none;
  padding: 0;
}
</style>
