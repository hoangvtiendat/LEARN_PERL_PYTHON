import { defineStore } from "pinia"
import { ref } from "vue"
import { courseService } from "@/services/courseService"

export const useCourseStore = defineStore("courses", () => {
  const courses = ref([])
  const currentCourse = ref(null)
  const currentLesson = ref(null)
  const isEnrolled = ref(false)
  const isLoading = ref(false)
  const error = ref(null)

  const fetchCourses = async () => {
    isLoading.value = true
    error.value = null
    try {
      const response = await courseService.getAllCourses()
      courses.value = response.courses || response
    } catch (err) {
      error.value = err.response?.data?.message || "Không thể tải danh sách khóa học."
      console.error("Error fetching courses:", err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchCourseDetail = async (id) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await courseService.getCourseById(id)
      const course = response.course || response
      currentCourse.value = course
      isEnrolled.value = course?.enrolled || false
    } catch (err) {
      error.value = err.response?.data?.message || "Không thể tải chi tiết khóa học."
      console.error("Error fetching course detail:", err)
    } finally {
      isLoading.value = false
    }
  }

  const fetchLessonDetail = async (courseId, lessonId) => {
    isLoading.value = true
    error.value = null
    try {
      const response = await courseService.getLessonById(courseId, lessonId)
      currentLesson.value = response.lesson || response
    } catch (err) {
      error.value = err.response?.data?.message || "Không thể tải chi tiết bài học."
      console.error("Error fetching lesson detail:", err)
    } finally {
      isLoading.value = false
    }
  }

  const enrollStudent = async (courseId) => {
    isLoading.value = true
    error.value = null
    try {
      const res = await courseService.enrollStudent(courseId)
      isEnrolled.value = true
      if (res.course) currentCourse.value = res.course
    } catch (err) {
      error.value = err.response?.data?.message || "Không thể ghi danh vào khóa học."
      console.error("Error enrolling:", err)
    } finally {
      isLoading.value = false
    }
  }

  const unenrollStudent = async (courseId) => {
    isLoading.value = true
    error.value = null
    try {
      await courseService.unenrollStudent(courseId)
      isEnrolled.value = false
    } catch (err) {
      error.value = err.response?.data?.message || "Không thể hủy ghi danh khóa học."
      console.error("Error unenrolling:", err)
    } finally {
      isLoading.value = false
    }
  }

  return {
    courses,
    currentCourse,
    currentLesson,
    isEnrolled,
    isLoading,
    error,
    fetchCourses,
    fetchCourseDetail,
    fetchLessonDetail,
    enrollStudent,
    unenrollStudent,
  }
})
