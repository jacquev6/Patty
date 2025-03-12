import { createApp } from 'vue'
import { createRouter, createWebHistory, RouterView } from 'vue-router'

import IndexView from './IndexView.vue'
import CreateTokenizationView from './CreateTokenizationView.vue'
import EditTokenizationView from './EditTokenizationView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'index',
      component: IndexView,
    },
    {
      path: '/new-tokenization',
      name: 'create-tokenization',
      component: CreateTokenizationView,
    },
    {
      path: '/tokenization-:id',
      name: 'tokenization',
      component: EditTokenizationView,
      props: true,
    },
  ],
})

const app = createApp(RouterView)

app.use(router)

app.mount('#app')
