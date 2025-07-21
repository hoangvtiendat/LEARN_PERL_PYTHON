<template>
  <div class="exercise-form-container">
    <h1>{{ isEditMode ? 'Chỉnh Sửa Bài Tập' : 'Tạo Bài Tập Mới' }}</h1>

    <div v-if="exerciseStore.isLoading">
      <p class="loading-message">Đang tải...</p>
    </div>
    <div v-else-if="exerciseStore.error">
      <p class="error-message">{{ exerciseStore.error }}</p>
    </div>

    <form @submit.prevent="handleSubmit" class="exercise-form">
      <div class="form-group">
        <label for="title">Tiêu đề bài tập:</label>
        <input type="text" id="title" v-model="form.title" required class="form-control">
      </div>

      <div class="form-group">
        <label for="description">Mô tả:</label>
        <textarea id="description" v-model="form.description" rows="8" class="form-control"></textarea>
      </div>

      <div class="form-group">
        <label for="exercise_type">Loại bài tập:</label>
        <select id="exercise_type" v-model="form.exercise_type" class="form-control">
          <option value="CODE">CODE (Code Submission)</option>
          <option value="ESSAY">ESSAY (Tự luận)</option>
          <option value="QUIZ">QUIZ (Trắc nghiệm)</option>
        </select>
      </div>

      <div class="form-group">
        <label for="deadline">Hạn nộp (Ngày và giờ):</label>
        <input type="datetime-local" id="deadline" v-model="form.deadline" class="form-control">
      </div>

      <div v-if="form.exercise_type === 'CODE'" class="test-cases-section">
        <h3>Test Cases (cho bài CODE)</h3>
        <p class="hint">Thêm các cặp Input và Expected Output để hệ thống tự động chấm điểm.</p>
        <div v-for="(testCase, index) in form.test_cases" :key="index" class="test-case-item">
          <div class="form-group">
            <label :for="'input-' + index">Input {{ index + 1 }}:</label>
            <textarea :id="'input-' + index" v-model="testCase.input" rows="2" class="form-control" placeholder="Nhập dữ liệu đầu vào"></textarea>
          </div>
          <div class="form-group">
            <label :for="'output-' + index">Expected Output {{ index + 1 }}:</label>
            <textarea :id="'output-' + index" v-model="testCase.output" rows="2" class="form-control" placeholder="Nhập kết quả mong đợi"></textarea>
          </div>
          <button type="button" @click="removeTestCase(index)" class="remove-test-case-button">Xóa</button>
        </div>
        <button type="button" @click="addTestCase" class="add-test-case-button">+ Thêm Test Case</button>
      </div>

      <div class="form-actions">
        <button type="submit" :disabled="exerciseStore.isLoading" class="submit-form-button">
          {{ exerciseStore.isLoading ? 'Đang lưu...' : (isEditMode ? 'Cập nhật Bài Tập' : 'Tạo Bài Tập') }}
        </button>
        <button type="button" @click="router.back()" class="cancel-button">Hủy</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { onMounted, reactive, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useExerciseStore } from '@/stores/exerciseStore';

const route = useRoute();
const router = useRouter();
const exerciseStore = useExerciseStore();

const props = defineProps({
  lessonId: { // Chỉ có khi tạo mới
    type: String, // route params là string
    required: false
  },
  exerciseId: { // Chỉ có khi chỉnh sửa
    type: String, // route params là string
    required: false
  }
});

const isEditMode = computed(() => !!props.exerciseId);

const form = reactive({
  title: '',
  description: '',
  exercise_type: 'CODE', // Default
  test_cases: [],
  deadline: null, // YYYY-MM-DDTHH:mm cho input datetime-local
});

onMounted(async () => {
  if (isEditMode.value) {
    await exerciseStore.fetchExerciseDetail(props.exerciseId);
    if (exerciseStore.currentExercise) {
      const ex = exerciseStore.currentExercise;
      form.title = ex.title;
      form.description = ex.description;
      form.exercise_type = ex.exercise_type;
      form.test_cases = ex.test_cases ? [...ex.test_cases] : []; // Đảm bảo là mảng và deep copy
      if (ex.deadline) {
        // Chuyển đổi định dạng ISO string (từ backend) sang định dạng 'YYYY-MM-DDTHH:mm' cho input datetime-local
        // Backend của bạn trả về '%Y-%m-%d %H:%M:%S', cần chuyển sang ISO string trước khi slice
        const dateObj = new Date(ex.deadline.replace(' ', 'T'));
        form.deadline = dateObj.toISOString().slice(0, 16);
      } else {
        form.deadline = null;
      }
    }
  }
});

const addTestCase = () => {
  form.test_cases.push({ input: '', output: '' });
};

const removeTestCase = (index) => {
  form.test_cases.splice(index, 1);
};

const handleSubmit = async () => {
  try {
    const payload = {
      title: form.title,
      description: form.description,
      exercise_type: form.exercise_type,
      // Chỉ gửi test_cases nếu loại bài tập là CODE
      test_cases: form.exercise_type === 'CODE' ? form.test_cases : [],
      // Chuyển đổi định dạng deadline từ datetime-local sang YYYY-MM-DD HH:MM:SS
      deadline: form.deadline ? new Date(form.deadline).toISOString().slice(0, 19).replace('T', ' ') : null
    };

    if (isEditMode.value) {
      await exerciseStore.updateExercise(props.exerciseId, payload);
      alert('Cập nhật bài tập thành công!');
    } else {
      await exerciseStore.createExercise(props.lessonId, payload);
      alert('Tạo bài tập thành công!');
    }
    router.back(); // Quay lại trang trước (LessonDetail)
  } catch (error) {
    alert(`Lỗi: ${error.message}`);
    console.error('Error submitting form:', error);
  }
};
</script>

<style scoped>
/* (Giữ nguyên phần style đã cung cấp trước đó) */
.exercise-form-container {
  max-width: 800px;
  margin: 30px auto;
  padding: 25px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  color: #333;
  font-size: 2.2em;
  margin-bottom: 25px;
}

.loading-message, .error-message {
  text-align: center;
  font-size: 1.1em;
  padding: 15px;
  border-radius: 5px;
  margin-bottom: 20px;
}

.loading-message {
  color: #007bff;
  background-color: #e7f3ff;
  border: 1px solid #cce5ff;
}

.error-message {
  color: #dc3545;
  background-color: #f8d7da;
  border: 1px solid #f5c6cb;
}

.exercise-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #555;
}

.form-control {
  width: calc(100% - 20px);
  padding: 12px;
  border: 1px solid #ced4da;
  border-radius: 8px;
  font-size: 1em;
  transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.form-control:focus {
  border-color: #007bff;
  box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
  outline: none;
}

textarea.form-control {
  resize: vertical;
  min-height: 120px;
}

.test-cases-section {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  background-color: #fdfdfd;
}

.test-cases-section h3 {
  margin-top: 0;
  color: #444;
  font-size: 1.5em;
}

.test-cases-section .hint {
  font-size: 0.9em;
  color: #777;
  margin-bottom: 15px;
}

.test-case-item {
  border: 1px dashed #d6eaff;
  background-color: #f0f8ff;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  position: relative;
  padding-right: 60px; /* Space for delete button */
}

.test-case-item .form-group {
  margin-bottom: 10px;
}

.remove-test-case-button {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  font-size: 0.9em;
  cursor: pointer;
  transition: background-color 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.remove-test-case-button:hover {
  background-color: #c82333;
}

.add-test-case-button {
  background-color: #28a745;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1em;
  transition: background-color 0.3s ease;
}

.add-test-case-button:hover {
  background-color: #218838;
}

.form-actions {
  display: flex;
  justify-content: flex-end; /* Căn nút sang phải */
  gap: 15px;
  margin-top: 20px;
}

.submit-form-button, .cancel-button {
  padding: 12px 25px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1em;
  transition: background-color 0.3s ease, transform 0.2s ease;
}

.submit-form-button {
  background-color: #007bff;
  color: white;
}

.submit-form-button:hover:not(:disabled) {
  background-color: #0056b3;
  transform: translateY(-2px);
}

.submit-form-button:disabled {
  background-color: #a0ccee;
  cursor: not-allowed;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
}

.cancel-button:hover {
  background-color: #5a6268;
}
</style>