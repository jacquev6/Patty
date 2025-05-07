import { createApp } from 'vue'
import 'modern-normalize/modern-normalize.css'
import { createRouter, createWebHashHistory, RouterView } from 'vue-router'

import BatchExportIndexView from './BatchExportIndexView.vue'
import BatchExportExerciseView from './BatchExportExerciseView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'index',
      component: BatchExportIndexView,
    },
    {
      path: '/:id',
      name: 'exercise',
      component: BatchExportExerciseView,
      props: true,
    },
  ],
})

const app = createApp(RouterView)

app.use(router)

app.mount('#app')
