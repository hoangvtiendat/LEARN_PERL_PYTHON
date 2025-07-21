<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';

const content = ref('');
const feedback = ref('');
const route = useRoute();
const exerciseId = route.params.exerciseId;

const submitExercise = async () => {
  const token = localStorage.getItem('access_token');
  const res = await axios.post(`http://localhost:5000/api/exercises/${exerciseId}/submit`, 
    { content: content.value }, 
    { headers: { Authorization: `Bearer ${token}` } }
  );
  feedback.value = res.data.feedback || 'Nộp bài thành công.';
};
</script>

<template>
  <div>
    <h2>Nộp bài tập</h2>
    <textarea v-model="content" rows="10" cols="50" placeholder="Nhập code hoặc nội dung bài làm"></textarea>
    <br/>
    <button @click="submitExercise">Nộp bài</button>
    <p v-if="feedback">{{ feedback }}</p>
  </div>
</template>
