import api from './api'

/**
 * Gửi câu hỏi tới chatbot AI
 * @param {string} question
 * @returns {Promise}
 */
export const askChatbot = (question) => {
  return api.post('/ai/chatbot', { question })
}

/**
 * Gợi ý sửa lỗi code bằng AI
 * @param {string} code - Mã nguồn người dùng nhập
 * @param {string} language - Ngôn ngữ lập trình (python, perl, ...)
 * @returns {Promise}
 */
export const suggestFix = (code, language) => {
  return api.post('/ai/suggest-fix', { code, language })
}

/**
 * Sinh danh sách câu hỏi trắc nghiệm từ AI
 * @param {string} topic - Chủ đề (VD: biến, vòng lặp,...)
 * @param {string} difficulty - độ khó: 'dễ' | 'trung bình' | 'khó'
 * @param {number} num_questions - số lượng câu hỏi cần sinh
 * @returns {Promise}
 */
export const generateQuestions = (topic, difficulty = 'dễ', num_questions = 3) => {
  return api.post('/ai/generate-questions', {
    topic,
    difficulty,
    num_questions,
  })
}

/**
 * Lấy thông tin đánh giá năng lực hiện tại (chưa dùng nhiều)
 * @returns {Promise}
 */
export const getAssessment = () => {
  return api.get('/ai/assessment')
}
