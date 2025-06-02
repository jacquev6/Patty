import { createApp } from 'vue'
import 'modern-normalize/modern-normalize.css'
import { createRouter, createWebHashHistory, RouterView } from 'vue-router'

import AdaptationBatchExportIndexView from './AdaptationBatchExportIndexView.vue'
import AdaptationBatchExportExerciseView from './AdaptationBatchExportExerciseView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'index',
      component: AdaptationBatchExportIndexView,
    },
    {
      path: '/:id',
      name: 'exercise',
      component: AdaptationBatchExportExerciseView,
      props: true,
    },
  ],
})

const app = createApp(RouterView)

app.use(router)

app.mount('#app')
