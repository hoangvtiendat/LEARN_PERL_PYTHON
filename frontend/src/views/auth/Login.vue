<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Đăng nhập vào tài khoản
        </h2>
      </div>

      <div class="mt-8 space-y-6">
        <!-- Regular Login Form -->
        <form @submit.prevent="handleSubmit">
          <div class="rounded-md shadow-sm -space-y-px">
            <div>
              <label for="email" class="sr-only">Email</label>
              <input
                id="email"
                v-model="form.email"
                name="email"
                type="email"
                required
                class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Địa chỉ email"
              />
            </div>
            <div>
              <label for="password" class="sr-only">Mật khẩu</label>
              <input
                id="password"
                v-model="form.password"
                name="password"
                type="password"
                required
                class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
                placeholder="Mật khẩu"
              />
            </div>
          </div>

          <div v-if="error" class="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md">
            {{ error }}
          </div>

          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
            >
              {{ isLoading ? 'Đang đăng nhập...' : 'Đăng nhập' }}
            </button>
          </div>

          <div class="flex items-center justify-between">
            <router-link to="/forgot-password" class="text-sm text-primary-600 hover:text-primary-500">
              Quên mật khẩu?
            </router-link>
            <span class="text-sm text-gray-600">
              Chưa có tài khoản?
              <router-link to="/register" class="font-medium text-primary-600 hover:text-primary-500">
                Đăng ký ngay
              </router-link>
            </span>
          </div>
        </form>
      </div>

      <!-- Debug Info -->
      <div v-if="showDebug" class="mt-4 p-4 bg-gray-100 rounded-lg text-xs">
        <p><strong>Debug Info:</strong></p>
        <p>authStore.twoFactorRequired: {{ authStore.twoFactorRequired }}</p>
        <p>isAuthenticated: {{ authStore.isAuthenticated }}</p>
        <p>hasToken: {{ !!authStore.token }}</p>
        <p>hasUser: {{ !!authStore.user }}</p>
        <p>userRole: {{ authStore.user?.role }}</p>
        <p>userName: {{ authStore.user?.full_name }}</p>
        <p>pendingLoginData: {{ authStore.pendingLoginData ? 'Có' : 'Không' }}</p>
      </div>

      <div class="text-center">
        <button
          @click="showDebug = !showDebug"
          class="text-xs text-gray-400 hover:text-gray-600"
        >
          {{ showDebug ? 'Ẩn' : 'Hiện' }} debug
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  email: '',
  password: ''
})

const error = ref('')
const showDebug = ref(false)

const isLoading = computed(() => authStore.isLoading)

const handleSubmit = async () => {
  error.value = ''

  try {
    console.log("🔐 Attempting login with:", { email: form.value.email })
    const result = await authStore.login(form.value)
    console.log("🔐 Login result:", result)
    console.log("🔐 After login, authStore.twoFactorRequired:", authStore.twoFactorRequired)

    if (result.requires2FA) {
      console.log('🔑 2FA required, redirecting to OTP verification page.')
      await nextTick() // Ensure state is updated before redirect
      router.push('/2fa')
    } else if (result.success) {
      console.log("✅ Login successful, redirecting to dashboard")
      await nextTick()
      router.push('/dashboard')
    } else {
      console.log("❌ Login failed with message:", result.message)
      error.value = result.message || 'Đăng nhập thất bại'
    }
  } catch (err) {
    console.error("❌ Login error:", err)
    // Kiểm tra lại twoFactorRequired sau khi gặp lỗi
    if (authStore.twoFactorRequired) {
      console.log("🔑 Error occurred but 2FA required, redirecting to /2fa")
      await nextTick()
      router.push('/2fa')
    } else {
      error.value = err.message || 'Đăng nhập thất bại'
    }
  }
}
</script>
<style scoped>
:root {
  --navy: #1a2a4f;
  --navy-light: #2d3e6b;
  --navy-dark: #142040;
  --accent: #4f83ff;
  --success: #1abc9c;
  --danger: #e63946;
  --white: #fff;
  --gray: #f5f7fa;
  --border: #e3e8ee;
}

body {
  font-family: "Inter", "Segoe UI", Arial, sans-serif;
  background: var(--gray);
  color: var(--navy-dark);
}

.max-w-md {
  background: var(--white);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(26, 42, 79, 0.10);
  padding: 32px 24px;
}

h2 {
  color: var(--navy);
  font-weight: 700;
  letter-spacing: 1px;
}

input[type="email"], input[type="password"] {
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--gray);
  color: var(--navy-dark);
  font-size: 1rem;
  padding: 10px 14px;
  margin-bottom: 8px;
  transition: border 0.2s;
}

input[type="email"]:focus, input[type="password"]:focus {
  border-color: var(--navy);
  outline: none;
  background: var(--white);
}

button[type="submit"], .btn-primary {
  background: var(--navy);
  color: var(--white);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 1rem;
  padding: 10px 0;
  margin-top: 8px;
  transition: background 0.2s;
  box-shadow: 0 2px 8px rgba(26, 42, 79, 0.08);
}

button[type="submit"]:hover:not(:disabled), .btn-primary:hover:not(:disabled) {
  background: var(--navy-light);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.text-primary-600 {
  color: var(--navy);
  transition: color 0.2s;
}

.text-primary-600:hover, .font-medium.text-primary-600:hover {
  color: var(--accent);
}

.bg-red-50 {
  background: #fdecef;
}

.rounded-md {
  border-radius: 8px;
}

.bg-gray-100 {
  background: var(--gray);
  border-radius: 8px;
}

.text-xs {
  font-size: 0.85rem;
}

.text-gray-400 {
  color: #b0b8d1;
}

.text-gray-600 {
  color: var(--navy-light);
}

@media (max-width: 768px) {
  .max-w-md {
    padding: 16px 8px;
    border-radius: 8px;
  }
}
</style>
