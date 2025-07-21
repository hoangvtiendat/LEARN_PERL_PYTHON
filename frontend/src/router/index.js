import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Auth Views
import Login from '@/views/auth/Login.vue'
import Register from '@/views/auth/Register.vue'
import ForgotPassword from '@/views/auth/ForgotPassword.vue'
import ResetPassword from '@/views/auth/ResetPassword.vue'
import TwoFactorAuth from '@/views/auth/TwoFactorAuth.vue'

// Dashboard Views
import StudentDashboard from '@/views/dashboard/StudentDashboard.vue'
import TeacherDashboard from '@/views/dashboard/TeacherDashboard.vue'
import AdminDashboard from '@/views/dashboard/AdminDashboard.vue'

// Course Views
import CourseList from '@/views/courses/CourseList.vue'
import CourseDetail from '@/views/courses/CourseDetail.vue'
import LessonDetail from '@/views/courses/LessonDetail.vue'

// Assignment Views
import AssignmentList from '@/views/assignments/AssignmentList.vue'
import AssignmentSubmission from '@/views/assignments/AssignmentSubmission.vue'
import GradingPage from '@/views/teacher/GradingPage.vue'

// Other Views
import OnlineIDE from '@/views/ide/OnlineIDE.vue'
import Profile from '@/views/profile/Profile.vue'
import UserManagement from '@/views/admin/UserManagement.vue'
import Reports from '@/views/admin/Reports.vue'
//=====
import Notification from '@/views/notifications/Notification.vue'
const notificationRoutes = [
  {
    path: '/notifications',
    name: 'Notifications',
    component: Notification,
    meta: { requiresAuth: true, roles: ['student'] }
  }
]
const authRoutes = [
  { path: '/login', name: 'Login', component: Login, meta: { requiresAuth: false } },
  { path: '/register', name: 'Register', component: Register, meta: { requiresAuth: false } },
  { path: '/forgot-password', name: 'ForgotPassword', component: ForgotPassword, meta: { requiresAuth: false } },
  { path: '/reset-password', name: 'ResetPassword', component: ResetPassword, meta: { requiresAuth: false } },
  { path: '/2fa', name: 'TwoFactorAuth', component: TwoFactorAuth, meta: { requiresAuth: false } },
]

const dashboardRoutes = [
  { path: '/dashboard', name: 'Dashboard', component: StudentDashboard, meta: { requiresAuth: true } },
  { path: '/teacher-dashboard', name: 'TeacherDashboard', component: TeacherDashboard, meta: { requiresAuth: true, roles: ['teacher', 'admin'] } },
  { path: '/admin-dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, roles: ['admin'] } },
]

const courseRoutes = [
  { path: '/courses', name: 'CourseList', component: CourseList, meta: { requiresAuth: true } },
  { path: '/courses/:id', name: 'CourseDetail', component: CourseDetail, props: true, meta: { requiresAuth: true } },
  { path: '/courses/:courseId/lessons/:lessonId', name: 'LessonDetail', component: LessonDetail, props: true, meta: { requiresAuth: true } },
]

const assignmentRoutes = [
  { path: '/assignments', name: 'AssignmentList', component: AssignmentList, meta: { requiresAuth: true } },
  { path: '/assignments/:id/submit', name: 'AssignmentSubmission', component: AssignmentSubmission, props: true, meta: { requiresAuth: true, roles: ['student'] } },
  { path: '/grading/:assignmentId/:submissionId', name: 'GradingPage', component: GradingPage, props: true, meta: { requiresAuth: true, roles: ['teacher', 'admin'] } },
]

const extraRoutes = [
  { path: '/chatbot', name: 'Chatbot', component: () => import('@/components/common/Chatbot.vue'), meta: { requiresAuth: true } },
  { path: '/ide', name: 'OnlineIDE', component: OnlineIDE, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/admin/users', name: 'UserManagement', component: UserManagement, meta: { requiresAuth: true, roles: ['admin'] } },
  { path: '/admin/reports', name: 'Reports', component: Reports, meta: { requiresAuth: true, roles: ['admin'] } },
]

const fallbackRoutes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

const routes = [
  ...authRoutes,
  ...dashboardRoutes,
  ...courseRoutes,
  ...assignmentRoutes,
  ...extraRoutes,
  ...notificationRoutes,
  ...fallbackRoutes,
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth
  const allowedRoles = to.meta.roles || []

  // Fetch user if token exists but user is not loaded
  if (localStorage.getItem('token') && !authStore.user && !authStore.twoFactorRequired) {
    try {
      await authStore.fetchProfile()
    } catch (error) {
      await authStore.logout()
      return next({ name: 'Login' })
    }
  }

  // 2FA Route
  if (to.name === 'TwoFactorAuth') {
    if (authStore.twoFactorRequired) return next()
    return next({ name: 'Login' })
  }

  // Protected Route
  if (requiresAuth) {
    if (!authStore.isAuthenticated) {
      return authStore.twoFactorRequired
        ? next({ name: 'TwoFactorAuth' })
        : next({ name: 'Login' })
    }

    // Role-based protection
    if (allowedRoles.length > 0 && !allowedRoles.includes(authStore.user.role)) {
      return next({ name: 'Dashboard' })
    }

    return next()
  }

  // Prevent accessing login/register pages when already authenticated
  const authPages = ['Login', 'Register', 'ForgotPassword', 'ResetPassword']
  if (!requiresAuth && authStore.isAuthenticated && authPages.includes(to.name)) {
    return next({ name: 'Dashboard' })
  }

  return next()
})

export default router
