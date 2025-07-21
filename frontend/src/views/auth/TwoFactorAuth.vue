<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Xác thực hai bước
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          Vui lòng nhập mã xác thực 6 số từ email của bạn.
        </p>
        <div class="mt-4 p-4 bg-yellow-50 rounded-lg">
          <p class="text-sm text-yellow-800">
            Kiểm tra hộp thư đến hoặc thư mục spam
          </p>
        </div>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleOTPSubmit">
        <div>
          <label for="otp" class="block text-sm font-medium text-gray-700 mb-2">
            Mã xác thực (6 số)
          </label>
          <input
            id="otp"
            v-model="otpCode"
            name="otp"
            type="text"
            maxlength="6"
            pattern="[0-9]{6}"
            required
            class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 text-center text-2xl tracking-widest"
            placeholder="000000"
            @input="formatOTP"
            autofocus
          />
        </div>

        <div v-if="otpError" class="text-red-600 text-sm text-center bg-red-50 p-3 rounded-md">
          {{ otpError }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading || otpCode.length !== 6"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {{ isLoading ? 'Đang xác thực...' : 'Xác thực' }}
          </button>
        </div>

        <div class="text-center">
          <button
            type="button"
            @click="cancelTwoFactor"
            class="text-sm text-gray-600 hover:text-gray-500"
          >
            Quay lại đăng nhập
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const otpCode = ref('')
const otpError = ref('')
const isLoading = computed(() => authStore.isLoading)

// Redirect to login if 2FA is not actually required (e.g., direct access to /2fa)
onMounted(() => {
  if (!authStore.twoFactorRequired) {
    console.log("TwoFactorAuth: 2FA not required, redirecting to login.")
    router.replace('/login')
  }
})

const handleOTPSubmit = async () => {
  otpError.value = ''

  if (otpCode.value.length !== 6) {
    otpError.value = 'Mã OTP phải có 6 số'
    return
  }

  try {
    console.log("🔑 Attempting OTP verification with:", otpCode.value)
    const result = await authStore.verifyTwoFactor(otpCode.value)
    console.log("🔑 OTP verification result:", result)

    if (result.success) {
      console.log("✅ OTP verification successful, redirecting to dashboard.")
      router.push('/dashboard')
    } else if (result.message) {
      otpError.value = result.message; // Display error message if OTP verification failed
    }
  } catch (err) {
    console.error("❌ OTP verification error:", err)
    otpError.value = err.response?.data?.error || err.message || 'Mã OTP không đúng'
    otpCode.value = '' // Clear OTP input on error
  }
}

const formatOTP = (event) => {
  const value = event.target.value.replace(/\D/g, '')
  otpCode.value = value.slice(0, 6)
}

const cancelTwoFactor = () => {
  console.log("TwoFactorAuth: Cancelling 2FA, redirecting to login.")
  authStore.cancelTwoFactor()
  otpCode.value = ''
  otpError.value = ''
  router.push('/login')
}
</script>
