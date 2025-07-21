<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Quên mật khẩu
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Nhập địa chỉ email của bạn để nhận liên kết đặt lại mật khẩu.
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email" class="sr-only">Địa chỉ email</label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm"
              placeholder="Địa chỉ email"
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
            {{ isLoading ? 'Đang gửi...' : 'Gửi liên kết đặt lại' }}
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
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

const email = ref('')
const error = ref('')
const successMessage = ref('')
const isLoading = computed(() => authStore.isLoading)

const handleSubmit = async () => {
  error.value = ''
  successMessage.value = ''
  try {
    const response = await authStore.forgotPassword(email.value)
    successMessage.value = response.message || 'Liên kết đặt lại mật khẩu đã được gửi đến email của bạn.'
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Gửi yêu cầu thất bại.'
  }
}
</script>
