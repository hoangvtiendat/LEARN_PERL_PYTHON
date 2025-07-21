<template>
  <div class="min-h-screen bg-gray-100">
    <Navbar />
    <div class="container mx-auto px-4 py-8">
      <h1 class="text-3xl font-bold text-gray-800 mb-6">Chào mừng, {{ authStore.user?.username || 'Giáo viên' }}!</h1>
      <p class="text-gray-600 mb-8">Đây là bảng điều khiển giáo viên của bạn. Bạn có thể quản lý khóa học, bài tập và chấm điểm tại đây.</p>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <!-- Card 1: Manage Courses -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Quản lý khóa học</h2>
          <p class="text-gray-600 mb-4">Tạo, chỉnh sửa và quản lý các khóa học của bạn.</p>
          <router-link to="/courses" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            Quản lý
          </router-link>
        </div>

        <!-- Card 2: Grade Assignments -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Chấm điểm bài tập</h2>
          <p class="text-gray-600 mb-4">Xem và chấm điểm các bài nộp của học sinh.</p>
          <router-link to="/grading" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            Chấm điểm
          </router-link>
        </div>

        <!-- Card 3: View Assignments -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-4">Xem bài tập</h2>
          <p class="text-gray-600 mb-4">Xem danh sách các bài tập đã tạo.</p>
          <router-link to="/assignments" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            Xem bài tập
          </router-link>
        </div>

        <!-- Card 4: Online IDE -->
        <div class="bg-white rounded-lg shadow-md p-6">
          <h2 class="text-xl font-semibold text-gray-800 mb-4">IDE trực tuyến</h2>
          <p class="text-gray-600 mb-4">Thực hành viết mã trực tiếp trong trình duyệt.</p>
          <router-link to="/ide" class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            Mở IDE
          </router-link>
        </div>
      </div>
    </div>
    <Chatbot />
  </div>
</template>

<script setup>
import Navbar from '@/components/layout/Navbar.vue';
import Chatbot from '@/components/common/Chatbot.vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
</script>
