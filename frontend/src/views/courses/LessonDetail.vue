<template>
  <div>
    <h2>{{ lesson.title }}</h2>
    <div v-html="lesson.content"></div>
  </div>
  
</template>

<script>
import { getLessonDetails } from '@/services/courseService';

export default {
  data() {
    return {
      lesson: {},
    };
  },
  async created() {
    const id = this.$route.params.id;
    try {
      const res = await getLessonDetails(id);
      this.lesson = res.data;
    } catch (error) {
      console.error('Lỗi khi tải bài học:', error);
    }
  },
};
</script>

