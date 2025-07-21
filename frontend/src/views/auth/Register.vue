<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Đăng ký tài khoản mới
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Hoặc <router-link to="/login" class="font-medium text-primary-600 hover:text-primary-500">đăng nhập</router-link> nếu bạn đã có tài khoản
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="full-name" class="sr-only">Họ và tên</label>
            <input
              id="full-name"
              v-model="form.full_name"
              name="full-name"
              type="text"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="Họ và tên"
            />
          </div>
          <div>
            <label for="email-address" class="sr-only">Địa chỉ email</label>
            <input
              id="email-address"
              v-model="form.email"
              name="email"
              type="email"
              autocomplete="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="Địa chỉ email"
            />
          </div>
          <div>
            <label for="student-code" class="sr-only">Mã số sinh viên</label>
            <input
              id="student-code"
              v-model="form.student_code"
              name="student-code"
              type="text"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="Mã số sinh viên"
            />
          </div>
          <div>
            <label for="password" class="sr-only">Mật khẩu</label>
            <input
              id="password"
              v-model="form.password"
              name="password"
              type="password"
              autocomplete="new-password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="Mật khẩu"
            />
          </div>
          <div>
            <label for="confirm-password" class="sr-only">Xác nhận mật khẩu</label>
            <input
              id="confirm-password"
              v-model="form.confirm_password"
              name="confirm-password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="Xác nhận mật khẩu"
            />
          </div>
        </div>

        <div v-if="error" class="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md">
          {{ error }}
        </div>
        <div v-if="successMessage" class="text-green-600 text-sm text-center bg-green-50 p-3 rounded-md">
          {{ successMessage }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {{ isLoading ? 'Đang đăng ký...' : 'Đăng ký' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({
  full_name: '',
  email: '',
  student_code: '',
  password: '',
  confirm_password: ''
})

const error = ref('')
const successMessage = ref('')
const isLoading = computed(() => authStore.isLoading)

const handleSubmit = async () => {
  error.value = ''
  successMessage.value = ''

  if (form.value.password !== form.value.confirm_password) {
    error.value = 'Mật khẩu xác nhận không khớp.'
    return
  }

  try {
    const response = await authStore.register({
      full_name: form.value.full_name,
      email: form.value.email,
      student_code: form.value.student_code,
      password: form.value.password
    })
    successMessage.value = response.message || 'Đăng ký thành công! Vui lòng đăng nhập.'
    // Clear form after successful registration
    form.value = {
      full_name: '',
      email: '',
      student_code: '',
      password: '',
      confirm_password: ''
    }
    // Optionally redirect to login after a short delay
    setTimeout(() => {
      router.push('/login')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Đăng ký thất bại.'
  }
}
</script>
