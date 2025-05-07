import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import 'modern-normalize/modern-normalize.css'
import { createPinia } from 'pinia'

import './main.css'
import IndexView from './IndexView.vue'
import CreateBatchView from './CreateBatchView.vue'
import EditAdaptationView from './EditAdaptationView.vue'
import EditBatchView from './EditBatchView.vue'
import FrontendRootView from './FrontendRootView.vue'
import ExamplesView from './ExamplesView.vue'
import EditTextbookView from './EditTextbookView.vue'

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
    {
      path: '/textbook-:id',
      name: 'textbook',
      component: EditTextbookView,
      props: true,
    },
    {
      path: '/examples',
      name: 'examples',
      component: ExamplesView,
    },
  ],
})

const app = createApp(FrontendRootView)

app.use(router)
app.use(createPinia())

app.mount('#app')
