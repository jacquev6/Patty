import { createApp } from 'vue'
import { createRouter, createWebHistory, RouterView } from 'vue-router'
import 'modern-normalize/modern-normalize.css'
import { createPinia } from 'pinia'

import './main.css'
import IndexView from './IndexView.vue'
import CreateAdaptationView from './CreateAdaptationView.vue'
import CreateBatchView from './CreateBatchView.vue'
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
      path: '/new-batch',
      name: 'create-batch',
      component: CreateBatchView,
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
app.use(createPinia())

app.mount('#app')
