<template>
  <div class="container mx-auto p-4">
    <h1 class="text-3xl font-bold mb-6">Hồ sơ cá nhân</h1>

    <div v-if="isLoading" class="text-center text-gray-500">Đang tải hồ sơ...</div>
    <div v-else-if="error" class="text-center text-red-500">{{ error }}</div>
    <div v-else-if="!user" class="text-center text-gray-500">Không tìm thấy thông tin người dùng.</div>
    <div v-else class="bg-white p-6 rounded-lg shadow-md">
      <h2 class="text-2xl font-semibold mb-4">Thông tin cơ bản</h2>
      <form @submit.prevent="updateProfile" class="space-y-4">
        <div>
          <label for="full_name" class="block text-sm font-medium text-gray-700">Họ và tên</label>
          <input type="text" id="full_name" v-model="userForm.full_name" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3" required />
        </div>
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700">Email</label>
          <input type="email" id="email" v-model="userForm.email" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3" required />
        </div>
        <div>
          <label for="role" class="block text-sm font-medium text-gray-700">Vai trò</label>
          <input type="text" id="role" :value="userForm.role" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 bg-gray-100 cursor-not-allowed" disabled />
        </div>
        <div v-if="userForm.role === 'student'">
          <label for="student_code" class="block text-sm font-medium text-gray-700">Mã số sinh viên</label>
          <input type="text" id="student_code" :value="userForm.student_code" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 bg-gray-100 cursor-not-allowed" disabled />
        </div>

        <div v-if="updateError" class="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md">
          {{ updateError }}
        </div>
        <div v-if="updateSuccess" class="text-green-600 text-sm text-center bg-green-50 p-3 rounded-md">
          {{ updateSuccess }}
        </div>

        <button type="submit" :disabled="isUpdatingProfile" class="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50">
          {{ isUpdatingProfile ? 'Đang cập nhật...' : 'Cập nhật hồ sơ' }}
        </button>
      </form>

      <h2 class="text-2xl font-semibold mt-8 mb-4">Thay đổi mật khẩu</h2>
      <form @submit.prevent="changePassword" class="space-y-4">
        <div>
          <label for="current_password" class="block text-sm font-medium text-gray-700">Mật khẩu hiện tại</label>
          <input type="password" id="current_password" v-model="passwordForm.current_password" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3" required />
        </div>
        <div>
          <label for="new_password" class="block text-sm font-medium text-gray-700">Mật khẩu mới</label>
          <input type="password" id="new_password" v-model="passwordForm.new_password" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3" required />
        </div>
        <div>
          <label for="confirm_password" class="block text-sm font-medium text-gray-700">Xác nhận mật khẩu mới</label>
          <input type="password" id="confirm_password" v-model="passwordForm.confirm_password" class="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3" required />
        </div>

        <div v-if="passwordError" class="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md">
          {{ passwordError }}
        </div>
        <div v-if="passwordSuccess" class="text-green-600 text-sm text-center bg-green-50 p-3 rounded-md">
          {{ passwordSuccess }}
        </div>

        <button type="submit" :disabled="isChangingPassword" class="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 disabled:opacity-50">
          {{ isChangingPassword ? 'Đang thay đổi...' : 'Thay đổi mật khẩu' }}
        </button>
      </form>

      <h2 class="text-2xl font-semibold mt-8 mb-4">Xác thực hai lớp (2FA)</h2>
      <div class="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
        <span class="text-gray-700">Trạng thái 2FA: 
          <span :class="user.two_fa_enabled ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'">
            {{ user.two_fa_enabled ? 'Đã bật' : 'Đã tắt' }}
          </span>
        </span>
        <button 
          @click="toggleTwoFactor" 
          :disabled="isToggling2FA"
          :class="user.two_fa_enabled ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'"
          class="text-white px-4 py-2 rounded-md disabled:opacity-50"
        >
          {{ isToggling2FA ? 'Đang xử lý...' : (user.two_fa_enabled ? 'Tắt 2FA' : 'Bật 2FA') }}
        </button>
      </div>
      <div v-if="twoFactorMessage" class="mt-2 text-sm" :class="twoFactorMessageType === 'success' ? 'text-green-600' : 'text-red-600'">
        {{ twoFactorMessage }}
      </div>
      <div v-if="twoFactorProvisioningUri && !user.two_fa_enabled" class="mt-4 p-4 bg-yellow-50 rounded-lg">
        <p class="text-sm text-yellow-800 mb-2">Quét mã QR này bằng ứng dụng xác thực (ví dụ: Google Authenticator) để hoàn tất thiết lập 2FA:</p>
        <img :src="`https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=${twoFactorProvisioningUri}`" alt="QR Code" class="mx-auto my-2" />
        <p class="text-sm text-yellow-800">Hoặc nhập thủ công Secret Key: <span class="font-mono break-all">{{ twoFactorSecretKey }}</span></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const user = computed(() => authStore.user)
const isLoading = computed(() => authStore.isLoading)
const error = computed(() => authStore.error)

const userForm = ref({
  full_name: '',
  email: '',
  role: '',
  student_code: '',
})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: '',
})

const updateError = ref(null)
const updateSuccess = ref(null)
const isUpdatingProfile = ref(false)

const passwordError = ref(null)
const passwordSuccess = ref(null)
const isChangingPassword = ref(false)

const twoFactorMessage = ref(null)
const twoFactorMessageType = ref(null)
const isToggling2FA = ref(false)
const twoFactorProvisioningUri = ref(null)
const twoFactorSecretKey = ref(null)

// Watch for changes in authStore.user and update userForm
watch(user, (newUser) => {
  if (newUser) {
    userForm.value = {
      full_name: newUser.full_name || '',
      email: newUser.email || '',
      role: newUser.role || '',
      student_code: newUser.student_code || '',
    }
  }
}, { immediate: true }) // Run immediately on component mount

const updateProfile = async () => {
  updateError.value = null
  updateSuccess.value = null
  isUpdatingProfile.value = true
  try {
    const response = await authStore.updateProfile(userForm.value)
    updateSuccess.value = response.message || 'Cập nhật hồ sơ thành công!'
  } catch (err) {
    updateError.value = err.response?.data?.message || err.message || 'Cập nhật hồ sơ thất bại.'
  } finally {
    isUpdatingProfile.value = false
  }
}

const changePassword = async () => {
  passwordError.value = null
  passwordSuccess.value = null
  isChangingPassword.value = true

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = 'Mật khẩu mới và xác nhận mật khẩu không khớp.'
    isChangingPassword.value = false
    return
  }

  try {
    const response = await authStore.changePassword(passwordForm.value)
    passwordSuccess.value = response.message || 'Thay đổi mật khẩu thành công!'
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: '',
    }
  } catch (err) {
    passwordError.value = err.response?.data?.message || err.message || 'Thay đổi mật khẩu thất bại.'
  } finally {
    isChangingPassword.value = false
  }
}

const toggleTwoFactor = async () => {
  twoFactorMessage.value = null
  twoFactorMessageType.value = null
  isToggling2FA.value = true
  twoFactorProvisioningUri.value = null
  twoFactorSecretKey.value = null

  try {
    const enable = !user.value.two_fa_enabled
    const response = await authStore.toggleTwoFactor(enable)
    
    twoFactorMessage.value = response.message || `2FA đã được ${enable ? 'bật' : 'tắt'} thành công.`
    twoFactorMessageType.value = 'success'

    if (enable && response.provisioning_uri) {
      twoFactorProvisioningUri.value = response.provisioning_uri
      twoFactorSecretKey.value = response.secret_key
    } else {
      twoFactorProvisioningUri.value = null
      twoFactorSecretKey.value = null
    }

    // Re-fetch user profile to update 2FA status in store
    await authStore.fetchProfile()

  } catch (err) {
    twoFactorMessage.value = err.response?.data?.message || err.message || 'Thao tác 2FA thất bại.'
    twoFactorMessageType.value = 'error'
    console.error('Error toggling 2FA:', err)
  } finally {
    isToggling2FA.value = false
  }
}

onMounted(() => {
  // Initial fetch if user data is not already loaded (e.g., on direct page access)
  if (!authStore.user) {
    authStore.fetchProfile()
  }
})
</script>
<style scope>
:root {
  --navy: #1a2a4f;
  --navy-light: #2d3e6b;
  --navy-dark: #142040;
  --primary: var(--navy);
  --primary-hover: var(--navy-light);
  --accent: #4f83ff;
  --success: #1abc9c;
  --danger: #e63946;
  --white: #fff;
  --gray: #f5f7fa;
  --border: #e3e8ee;
}

body {
  font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
  background: var(--gray);
  color: var(--navy-dark);
}

.container {
  background: var(--white);
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(26, 42, 79, 0.08);
  padding: 32px;
  margin-top: 32px;
}

h1, h2 {
  color: var(--primary);
  font-weight: bold;
  letter-spacing: 1px;
}

label {
  color: var(--navy-dark);
  font-weight: 500;
}

input, select, textarea {
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--gray);
  font-size: 1rem;
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

.bg-green-50 {
  background: #e6fcf7;
}

.bg-red-50 {
  background: #fdecef;
}

.bg-yellow-50 {
  background: #fff9db;
}

.text-green-600 {
  color: var(--success);
}

.text-red-600 {
  color: var(--danger);
}

.text-yellow-800 {
  color: #b59f3b;
}

.text-gray-700 {
  color: var(--navy-light);
}

.text-gray-500 {
  color: #6b7280;
}

button {
  font-weight: 500;
  border: none;
  border-radius: 6px;
  transition: background 0.2s;
  cursor: pointer;
}

.bg-primary-600, .bg-blue-500 {
  background: var(--primary);
  color: var(--white);
}

.bg-primary-600:hover, .hover\:bg-primary-700:hover, .bg-blue-500:hover, .hover\:bg-blue-600:hover {
  background: var(--primary-hover);
}

.bg-red-500 {
  background: var(--danger);
  color: var(--white);
}

.bg-red-500:hover, .hover\:bg-red-600:hover {
  background: #b82330;
}

.rounded-md, .rounded-lg {
  border-radius: 8px;
}

.shadow-md {
  box-shadow: 0 2px 8px rgba(26, 42, 79, 0.06);
}

.disabled\:opacity-50:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.font-semibold {
  font-weight: 600;
}

.font-mono {
  font-family: 'Fira Mono', 'Consolas', monospace;
}

.break-all {
  word-break: break-all;
}

.mx-auto {
  margin-left: auto;
  margin-right: auto;
}

.my-2 {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}

.mt-1 { margin-top: 0.25rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-4 { margin-top: 1rem; }
.mt-6 { margin-top: 1.5rem; }
.mt-8 { margin-top: 2rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-4 { margin-bottom: 1rem; }
.mb-6 { margin-bottom: 1.5rem; }

.p-3 { padding: 0.75rem; }
.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }

.space-y-4 > * + * {
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .container {
    padding: 1rem;
  }
}
</style>
