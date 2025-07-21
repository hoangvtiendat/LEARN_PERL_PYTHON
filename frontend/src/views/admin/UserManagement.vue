<template>
  <div class="max-w-5xl mx-auto p-6 space-y-8">
    <h1 class="text-2xl font-bold text-center">👤 Quản lý Người dùng & Lịch sử hoạt động</h1>

    <!-- 🔍 Tìm kiếm -->
    <div class="mb-4">
      <input
        v-model="searchKeyword"
        placeholder="🔍 Tìm kiếm người dùng (Họ tên, email, vai trò, MSSV)..."
        class="w-full border px-3 py-2 rounded"
      />
    </div>

    <!-- Danh sách người dùng -->
    <div v-if="filteredUsers.length === 0" class="text-center text-gray-500">
      Không tìm thấy người dùng nào.
    </div>

    <div v-else class="overflow-x-auto bg-white shadow rounded">
      <table class="min-w-full table-auto border">
        <thead class="bg-gray-100 text-left">
          <tr>
            <th class="p-2">ID</th>
            <th class="p-2">Họ tên</th>
            <th class="p-2">Email</th>
            <th class="p-2">Vai trò</th>
            <th class="p-2">MSSV</th>
            <th class="p-2">Hành động</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.id" class="border-t">
            <td class="p-2">{{ user.id }}</td>
            <td class="p-2">{{ user.full_name }}</td>
            <td class="p-2">{{ user.email }}</td>
            <td class="p-2">{{ user.role }}</td>
            <td class="p-2">{{ user.student_code || '—' }}</td>
            <td class="p-2 space-x-2">
              <button @click="startEdit(user)" class="bg-yellow-500 text-white px-2 py-1 rounded">Sửa</button>
              <button @click="deleteUser(user.id)" class="bg-red-600 text-white px-2 py-1 rounded">Xóa</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Form sửa người dùng -->
    <div v-if="editingUser" class="bg-gray-100 p-4 rounded shadow">
      <h2 class="text-lg font-semibold mb-2">🛠️ Cập nhật người dùng</h2>
      <div class="space-y-2">
        <input v-model="editingUser.full_name" placeholder="Họ tên" class="w-full border rounded p-2" />
        <input v-model="editingUser.email" placeholder="Email" class="w-full border rounded p-2" />
        <select v-model="editingUser.role" class="w-full border rounded p-2">
          <option value="STUDENT">Sinh viên</option>
          <option value="TEACHER">Giảng viên</option>
          <option value="ADMIN">Quản trị</option>
        </select>
      </div>
      <div class="mt-4 space-x-2">
        <button @click="updateUser" class="bg-green-600 text-white px-4 py-1 rounded">Lưu</button>
        <button @click="editingUser = null" class="bg-gray-500 text-white px-4 py-1 rounded">Hủy</button>
      </div>
    </div>

    <!-- 📂 Backup & Restore -->
    <div class="bg-white shadow rounded p-4">
      <h2 class="text-xl font-semibold mb-4">🔢 Backup & Restore CSDL</h2>
      <div class="space-x-4">
        <button @click="backupDatabase" class="bg-blue-600 text-white px-4 py-2 rounded">Backup</button>
        <input type="file" ref="restoreFile" class="hidden" @change="handleRestoreFile" />
        <button @click="$refs.restoreFile.click()" class="bg-green-600 text-white px-4 py-2 rounded">Restore</button>
      </div>
      <p v-if="backupMsg" class="mt-2 text-sm text-gray-600">{{ backupMsg }}</p>
    </div>

    <!-- 📊 Logs Table -->
    <div class="bg-white shadow rounded p-4">
      <div class="flex justify-between items-center mb-4">
        <h2 class="text-xl font-semibold">📜 Lịch sử hoạt động</h2>
        <button @click="exportLogs" class="bg-indigo-600 text-white px-4 py-2 rounded">Export CSV</button>
      </div>

      <div v-if="logs.length === 0" class="text-gray-500">Chưa có log nào.</div>

      <div v-else class="overflow-x-auto">
        <table class="min-w-full border">
          <thead class="bg-gray-100">
            <tr>
              <th class="p-2">#</th>
              <th class="p-2">User</th>
              <th class="p-2">Hành động</th>
              <th class="p-2">Chi tiết</th>
              <th class="p-2">Thời gian</th>
              <th class="p-2">Trạng thái</th>
              <th class="p-2">📋</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in logs" :key="log.id" class="border-t">
              <td class="p-2">{{ log.id }}</td>
              <td class="p-2">{{ log.full_name }}<br><small>{{ log.email }}</small></td>
              <td class="p-2">{{ log.action }}</td>
              <td class="p-2 text-sm">{{ log.detail }}</td>
              <td class="p-2 text-xs">{{ log.timestamp }}</td>
              <td class="p-2">
                <select v-model="log.status" @change="updateLog(log)" class="border rounded px-2 py-1">
                  <option value="active">active</option>
                  <option value="inactive">inactive</option>
                </select>
              </td>
              <td class="p-2">
                <button @click="deleteLog(log.id)" class="text-red-600 hover:underline">Xóa</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const users = ref([])
const searchKeyword = ref('')
const editingUser = ref(null)
const logs = ref([])
const backupMsg = ref('')
const token = localStorage.getItem('token')
const API = 'http://127.0.0.1:5000/api'

// Tìm kiếm người dùng
const filteredUsers = computed(() => {
  const keyword = searchKeyword.value.trim().toLowerCase()
  if (!keyword) return users.value
  return users.value.filter(user => {
    return (
      user.full_name?.toLowerCase().includes(keyword) ||
      user.email?.toLowerCase().includes(keyword) ||
      user.role?.toLowerCase().includes(keyword) ||
      (user.student_code || '').toLowerCase().includes(keyword)
    )
  })
})

// Quản lý người dùng
const fetchUsers = async () => {
  const res = await fetch(`${API}/user/users`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  users.value = await res.json()
}

const startEdit = (user) => {
  editingUser.value = { ...user }
}

const updateUser = async () => {
  await fetch(`${API}/user/users/${editingUser.value.id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({
      full_name: editingUser.value.full_name,
      email: editingUser.value.email,
      role: editingUser.value.role
    })
  })
  editingUser.value = null
  fetchUsers()
}

const deleteUser = async (id) => {
  if (!confirm('Bạn có chắc muốn xóa người dùng này?')) return
  await fetch(`${API}/user/users/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` }
  })
  fetchUsers()
}

onMounted(() => {
  fetchUsers()
})

// Quản lý logs
const fetchLogs = async () => {
  const res = await fetch(`${API}/user/logs`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const data = await res.json()
  logs.value = data.logs || []
}

const updateLog = async (log) => {
  await fetch(`${API}/user/logs/${log.id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`
    },
    body: JSON.stringify({ status: log.status, detail: log.detail, action: log.action })
  })
}

const deleteLog = async (logId) => {
  if (confirm('Xác nhận xóa log này?')) {
    await fetch(`${API}/user/logs/${logId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    fetchLogs()
  }
}

const exportLogs = async () => {
  const res = await fetch(`${API}/user/logs/export`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  const blob = await res.blob()
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'logs.csv'
  link.click()
  window.URL.revokeObjectURL(url)
}

// Backup & Restore
const backupDatabase = async () => {
  backupMsg.value = 'Đang thực hiện backup...'
  const res = await fetch(`${API}/user/admin/backup`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` }
  })
  if (res.ok) {
    const blob = await res.blob()
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'backup.sql'
    link.click()
    URL.revokeObjectURL(url)
    backupMsg.value = 'Backup thành công.'
  } else {
    backupMsg.value = 'Backup thất bại.'
  }
}

const handleRestoreFile = async (event) => {
  const file = event.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)

  const res = await fetch(`${API}/user/admin/restore`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` },
    body: formData
  })
  if (res.ok) {
    alert('Phục hồi thành công!')
  } else {
    alert('Phục hồi thất bại.')
  }
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
table th, table td {
  border: 1px solid #ddd;
}
</style>
