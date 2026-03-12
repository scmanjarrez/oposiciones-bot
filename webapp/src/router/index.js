import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  { path: '/', component: () => import('../views/HomeView.vue') },
  { path: '/exam', component: () => import('../views/ExamSetupView.vue') },
  { path: '/study/blocks', component: () => import('../views/BlockSelectorView.vue') },
  { path: '/study/blocks/:blockId', component: () => import('../views/QuizView.vue') },
  { path: '/study/topics', component: () => import('../views/TopicSelectorView.vue') },
  { path: '/study/topics/:topicId', component: () => import('../views/QuizView.vue') },
  { path: '/study/years', component: () => import('../views/YearSelectorView.vue') },
  { path: '/study/years/:year', component: () => import('../views/QuizView.vue') },
  { path: '/results', component: () => import('../views/ResultsView.vue') },
  // fallback
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export default createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})
