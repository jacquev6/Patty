import { createApp } from 'vue'
import { createRouter, createWebHistory, RouterView } from 'vue-router'
import 'modern-normalize/modern-normalize.css'
import { createPinia } from 'pinia'

import './main.css'
import IndexView from './IndexView.vue'
import CreateBatchView from './CreateBatchView.vue'
import EditAdaptationView from './EditAdaptationView.vue'
import EditBatchView from './EditBatchView.vue'

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
      path: '/batch-:id',
      name: 'batch',
      component: EditBatchView,
      props: true,
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
