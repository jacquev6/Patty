import { createApp } from 'vue'
import { createRouter, createWebHistory, RouterView } from 'vue-router'
import 'modern-normalize/modern-normalize.css'

import './main.css'
import IndexView from './IndexView.vue'
import CreateAdaptationView from './CreateAdaptationView.vue'
import EditAdaptationView from './EditAdaptationView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'index',
      component: IndexView,
    },
    {
      path: '/new-adaptation',
      name: 'create-adaptation',
      component: CreateAdaptationView,
    },
    {
      path: '/adaptation-:id',
      name: 'adaptation',
      component: EditAdaptationView,
      props: true,
    },
  ],
})

const app = createApp(RouterView)

app.use(router)

app.mount('#app')
