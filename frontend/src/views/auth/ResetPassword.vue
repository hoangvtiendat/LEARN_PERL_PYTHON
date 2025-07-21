<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Đặt lại mật khẩu
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Nhập mật khẩu mới của bạn.
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="password" class="sr-only">Mật khẩu mới</label>
            <input
              id="password"
              v-model="form.password"
              name="password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="Mật khẩu mới"
            />
          </div>
          <div>
            <label for="confirm_password" class="sr-only">Xác nhận mật khẩu mới</label>
            <input
              id="confirm_password"
              v-model="form.confirm_password"
              name="confirm_password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="Xác nhận mật khẩu mới"
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
            {{ isLoading ? 'Đang đặt lại...' : 'Đặt lại mật khẩu' }}
          </button>
        </div>

        <div class="text-center">
          <router-link to="/login" class="font-medium text-primary-600 hover:text-primary-500">
            Quay lại đăng nhập
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const form = ref({
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

  const token = route.query.token // Lấy token từ URL query params
  if (!token) {
    error.value = 'Không tìm thấy token đặt lại mật khẩu.'
    return
  }

  try {
    const response = await authStore.resetPassword(token, form.value.password)
    successMessage.value = response.message || 'Mật khẩu của bạn đã được đặt lại thành công. Vui lòng đăng nhập.'
    form.value = { password: '', confirm_password: '' } // Clear form
    // Optionally redirect to login after success
    setTimeout(() => {
      router.push('/login')
    }, 3000)
  } catch (err) {
    error.value = err.response?.data?.message || err.message || 'Đặt lại mật khẩu thất bại.'
  }
}
</script>
