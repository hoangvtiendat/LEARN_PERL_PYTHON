<template>
  <div id="app" class="min-h-screen flex flex-col">
    <Navbar v-if="showNavbar" />
    <main :class="{ 'pt-16': showNavbar }" class="flex-1">
      <router-view />
    </main>
    <LoadingSpinner v-if="isLoading" />
    
    <!-- Chatbot - only show for students -->
    <Chatbot v-if="isAuthenticated && userRoleIsStudent" />
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Navbar from '@/components/layout/Navbar.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
import Chatbot from '@/components/common/Chatbot.vue'

const route = useRoute()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const isLoading = computed(() => authStore.isLoading)
const user = computed(() => authStore.user)
const userRoleIsStudent = computed(() => user.value?.role === 'student')

const showNavbar = computed(() => {
  const noNavbarRoutes = ['Login', 'Register', 'ForgotPassword', 'ResetPassword', 'TwoFactorAuth']
  return !noNavbarRoutes.includes(route.name) && isAuthenticated.value;
})

onMounted(async () => {
  await authStore.checkAuth()
})
</script>

<style>
@import './style.css';
</style>
