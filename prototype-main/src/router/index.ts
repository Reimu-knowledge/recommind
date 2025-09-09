import { createRouter, createWebHistory } from 'vue-router';
import LoginView from '../views/LoginView.vue';
import StudentView from '../views/StudentView.vue';
import TeacherView from '../views/TeacherView.vue';

const routes = [
  { 
    path: '/', 
    redirect: '/login' 
  },
  { 
    path: '/login', 
    name: 'Login',
    component: LoginView,
    meta: { requiresAuth: false }
  },
  { 
    path: '/student', 
    name: 'Student',
    component: StudentView,
    meta: { requiresAuth: true, role: 'student' }
  },
  { 
    path: '/teacher', 
    name: 'Teacher',
    component: TeacherView,
    meta: { requiresAuth: true, role: 'teacher' }
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 路由守卫
router.beforeEach((to, from, next) => {
  // 模拟用户认证状态（实际项目中应从localStorage或Pinia中获取）
  const isAuthenticated = localStorage.getItem('userToken') !== null;
  const userRole = localStorage.getItem('userRole');
  
  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      // 未登录，重定向到登录页
      next('/login');
    } else if (to.meta.role && to.meta.role !== userRole) {
      // 角色不匹配，重定向到对应角色页面
      if (userRole === 'student') {
        next('/student');
      } else if (userRole === 'teacher') {
        next('/teacher');
      } else {
        next('/login');
      }
    } else {
      // 认证通过
      next();
    }
  } else {
    // 不需要认证的页面
    if (to.path === '/login' && isAuthenticated) {
      // 已登录用户访问登录页，重定向到对应角色页面
      if (userRole === 'student') {
        next('/student');
      } else if (userRole === 'teacher') {
        next('/teacher');
      } else {
        next();
      }
    } else {
      next();
    }
  }
});

export default router;
