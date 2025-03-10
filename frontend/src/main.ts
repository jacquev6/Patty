import { createApp } from 'vue'
import { createRouter, createWebHistory, RouterView } from 'vue-router'

import IndexView from './IndexView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'index',
      component: IndexView,
    },
  ],
})

const app = createApp(RouterView)

app.use(router)

app.mount('#app')
