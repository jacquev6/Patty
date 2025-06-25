import { createApp } from 'vue'
import 'modern-normalize/modern-normalize.css'
import { createRouter, createWebHashHistory } from 'vue-router'

import TextbookExportRootView from './TextbookExportRootView.vue'
import TextbookExportIndexView from './TextbookExportIndexView.vue'
import TextbookExportExerciseView from './TextbookExportExerciseView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'index',
      component: TextbookExportIndexView,
    },
    {
      path: '/:id',
      name: 'exercise',
      component: TextbookExportExerciseView,
      props: true,
    },
  ],
})

const app = createApp(TextbookExportRootView)

app.use(router)

app.mount('#app')
