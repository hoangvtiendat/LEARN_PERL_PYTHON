<template>
  <div class="course-detail">
    <div class="course-info card">
      <h2>{{ course.title }}</h2>
      <p>{{ course.description }}</p>
      <p><strong>Giảng viên:</strong> {{ course.teacher_name }}</p>
    </div>

    <div class="lesson-section card">
      <h3>Bài giảng</h3>
      <ul class="lesson-list">
        <li
          v-for="lesson in course.lessons"
          :key="lesson.id"
          class="lesson-item"
        >
          <div class="lesson-header">
            <span @click="selectLesson(lesson)" class="lesson-title clickable">
              <strong>{{ lesson.order }}. {{ lesson.title }}</strong>
            </span>
            <div v-if="isTeacher" class="lesson-actions">
              <button @click="editLesson(lesson)">✏️</button>
              <button @click="deleteLesson(lesson.id)">🗑️</button>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <!-- Chi tiết bài giảng -->
    <div v-if="selectedLesson" class="card lesson-detail">
      <h4>📖 Chi tiết bài giảng</h4>
      <p><strong>Tiêu đề:</strong> {{ selectedLesson.title }}</p>
      <p><strong>Nội dung:</strong> {{ selectedLesson.content }}</p>
      <p><strong>Thứ tự:</strong> {{ selectedLesson.order }}</p>
      <div v-if="selectedLesson.attachment_url">
        <strong>Tài liệu:</strong>
        <a :href="selectedLesson.attachment_url" target="_blank">
          Mở tài liệu 📎
        </a>
      </div>
    </div>

    <!-- Form thêm/sửa bài giảng -->
    <div v-if="isTeacher" class="lesson-form card">
      <h3>{{ isEditing ? 'Sửa bài giảng' : 'Thêm bài giảng mới' }}</h3>
      <form @submit.prevent="handleLessonSubmit">
        <label>Tiêu đề</label>
        <input v-model="lessonForm.title" required />

        <label>Nội dung</label>
        <textarea v-model="lessonForm.content" rows="4" required></textarea>

        <label>Thứ tự</label>
        <input type="number" v-model.number="lessonForm.order" required />

        <label>Attachment URL</label>
        <input v-model="lessonForm.attachment_url" />

        <div class="form-buttons">
          <button type="submit" class="btn-primary">
            {{ isEditing ? 'Cập nhật' : 'Thêm bài' }}
          </button>
          <button
            v-if="isEditing"
            type="button"
            class="btn-secondary"
            @click="cancelEdit"
          >
            Hủy
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'
import { authService } from '@/services/authService'

export default {
  name: 'CourseDetail',
  data() {
    return {
      course: {},
      userRole: null,
      selectedLesson: null,
      lessonForm: {
        id: null,
        title: '',
        content: '',
        order: 1,
        attachment_url: ''
      },
      isEditing: false
    }
  },
  computed: {
    isTeacher() {
      return this.userRole === 'teacher'
    }
  },
  methods: {
    async fetchCourse() {
      const courseId = this.$route.params.id
      const res = await api.get(`/courses/${courseId}`)
      this.course = res.data
    },
    async fetchUserProfile() {
      try {
        const res = await authService.getProfile()
        this.userRole = res.role
      } catch (err) {
        console.error('Lỗi khi lấy profile:', err)
      }
    },
    async selectLesson(lesson) {
      try {
        const res = await api.get(`courses/lessons/${lesson.id}`)
        this.selectedLesson = res.data
      } catch (err) {
        console.error('Lỗi khi lấy chi tiết bài giảng:', err)
      }
    },
    async handleLessonSubmit() {
      const courseId = this.$route.params.id
      if (this.isEditing) {
        await api.put(`/courses/lessons/${this.lessonForm.id}`, this.lessonForm)
      } else {
        await api.post(`/courses/${courseId}/lessons`, this.lessonForm)
      }
      this.resetForm()
      await this.fetchCourse()
    },
    editLesson(lesson) {
      this.isEditing = true
      this.lessonForm = { ...lesson }
    },
    cancelEdit() {
      this.resetForm()
    },
    async deleteLesson(lessonId) {
      await api.delete(`/courses/lessons/${lessonId}`)
      await this.fetchCourse()
    },
    resetForm() {
      this.isEditing = false
      this.lessonForm = {
        id: null,
        title: '',
        content: '',
        order: 1,
        attachment_url: ''
      }
    }
  },
  async mounted() {
    await this.fetchUserProfile()
    await this.fetchCourse()
  }
}
</script>

<style scoped>
:root {
  --navy: #1a2a4f;
  --navy-light: #2c3e75;
  --gray-light: #f7f9fc;
  --gray-dark: #444;
  --border: #dce1ea;
  --text: #1a1a1a;
  --white: #fff;
  --radius: 12px;
}

.course-detail {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 24px;
  font-family: 'Segoe UI', sans-serif;
  background: var(--gray-light);
  color: var(--text);
}

.card {
  background: #93c5fd47;
  padding: 24px 28px;
  margin-bottom: 28px;
  border-radius: 11px;
  box-shadow: 0 2px 10px rgba(26, 42, 79, 0.08);
  border: 1px solid var(--border);
}

.course-info h2 {
  font-size: 24px;
  color: var(--navy);
  margin-bottom: 8px;
}

.course-info p {
  font-size: 16px;
  margin-bottom: 4px;
}

.lesson-section h3,
.lesson-form h3 {
  font-size: 20px;
  color: var(--navy);
  margin-bottom: 16px;
}

.lesson-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.lesson-item {
  border-bottom: 1px solid var(--border);
  padding: 12px 0;
}

.lesson-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.lesson-content {
  margin: 6px 0 0;
  color: var(--gray-dark);
}

.lesson-actions button {
  background: #e3d2bb;
  padding: 3px 7px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 20px;
  margin-left: 10px;
  color: #080808;
  transition: color 0.2s ease;
}

.lesson-actions button:hover {
  color: var(--navy);
}

/* ✅ phần mới thêm */
.clickable {
  cursor: pointer;
  color: var(--navy);
}

.clickable:hover {
  text-decoration: underline;
  color: #1d4ed8;
}

.lesson-detail {
  background-color: #e5efff;
}

.attachment-link {
  color: #0b60b0;
  text-decoration: underline;
}

.lesson-form label {
  display: block;
  margin-top: 14px;
  font-weight: 600;
  font-size: 14px;
}

.lesson-form input,
.lesson-form textarea {
  width: 100%;
  padding: 10px 14px;
  margin-top: 6px;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: #fff;
  font-size: 14px;
  box-sizing: border-box;
}

.lesson-form textarea {
  resize: vertical;
  min-height: 100px;
}

.form-buttons {
  margin-top: 18px;
  display: flex;
  gap: 12px;
}

.btn-primary {
  background-color: #000082;
  color: rgb(255, 255, 255);
  border: none;
  display: inline-block;
  padding: 10px 7px;
  border-radius: var(--radius);
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-primary:hover {
  background-color: rgb(71, 135, 223);
}

.btn-secondary {
  background-color: #ccc;
  color: #333;
  border: none;
  padding: 10px 20px;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.btn-secondary:hover {
  background-color: #b3b3b3;
}
</style>
