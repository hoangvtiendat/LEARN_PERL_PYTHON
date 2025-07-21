import api from './api'

// ✅ Export tất cả các hàm với export có tên (named export)
export const getAllCourses = () => api.get('/courses')
export const getCourseDetails = (courseId) => api.get(`/courses/${courseId}`)
export const createCourse = (data) => api.post('/courses', data)
export const updateCourse = (courseId, data) => api.put(`/courses/${courseId}`, data)
export const deleteCourse = (courseId) => api.delete(`/courses/${courseId}`)

export const enrollCourse = (courseId) => api.post(`/courses/${courseId}/enroll`)
export const enrollStudent = (courseId, student_email) =>
  api.post(`/courses/${courseId}/enroll-student`, { student_email })
export const unenrollStudent = (courseId, student_email) =>
  api.post(`/courses/${courseId}/unenroll-student`, { student_email })

export const createLesson = (courseId, data) => api.post(`/courses/${courseId}/lessons`, data)
export const updateLesson = (lessonId, data) => api.put(`/courses/lessons/${lessonId}`, data)
export const deleteLesson = (lessonId) => api.delete(`/courses/lessons/${lessonId}`)
export const getLessonDetails = (lessonId) => api.get(`/courses/lessons/${lessonId}`)