<template>
  <div class="course-list-container p-6">
    <h1 class="text-3xl font-bold text-navy mb-6">📚 Danh sách Khóa học</h1>
    
    <div v-if="courses.length" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="course in courses" :key="course.id" class="bg-white rounded-lg shadow-lg p-4 border border-gray-200 hover:shadow-xl transition">
        <h2 class="text-xl font-semibold text-navy mb-2">
          {{ course.title }}
        </h2>
        <p class="text-gray-600 text-sm mb-4 line-clamp-3">
          {{ course.description }}
        </p>
        <router-link
          :to="`/courses/${course.id}`"
          class="inline-block text-white bg-navy hover:bg-blue-900 px-4 py-2 rounded text-sm transition"
        >
          Xem chi tiết
        </router-link>
      </div>
    </div>

    <p v-else class="text-gray-500 mt-4">Không có khóa học nào được tìm thấy.</p>
  </div>
</template>

<script>
import { getAllCourses } from '@/services/courseService'

export default {
  data() {
    return {
      courses: [],
    };
  },
  async created() {
    try {
      const res = await getAllCourses();
      this.courses = res.data;
    } catch (error) {
      console.error('Lỗi khi tải khóa học:', error);
    }
  },
};
</script>

<style scoped>
.text-navy {
  color: #1f2d3d;
}

.bg-navy {
  background-color: #1f2d3d;
}

.course-list-container {
  background-color: #f4f7fa;
  min-height: 100vh;
}
</style>
