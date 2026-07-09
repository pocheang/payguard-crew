import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('./views/Login.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('./layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('./views/Dashboard.vue')
      },
      {
        path: 'audit/single',
        name: 'SingleAudit',
        component: () => import('./views/SingleAudit.vue')
      },
      {
        path: 'audit/batch',
        name: 'BatchAudit',
        component: () => import('./views/BatchAudit.vue')
      },
      {
        path: 'review/pending',
        name: 'PendingReviews',
        component: () => import('./views/PendingReviews.vue')
      },
      {
        path: 'review/:transactionId',
        name: 'ReviewDetail',
        component: () => import('./views/ReviewDetail.vue')
      },
      {
        path: 'reports',
        name: 'Reports',
        component: () => import('./views/Reports.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else if (to.path === '/login' && authStore.isAuthenticated) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
