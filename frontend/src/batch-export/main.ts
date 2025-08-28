import { createApp } from 'vue'
import 'modern-normalize/modern-normalize.css'
import { createRouter, createWebHashHistory } from 'vue-router'

import BatchExportRootView from './RootView.vue'
import BatchExportIndexView from './IndexView.vue'
import BatchExportExerciseView from './ExerciseView.vue'

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

const app = createApp(BatchExportRootView)

app.use(router)

app.mount('#app')
