import { createApp } from 'vue'
import 'modern-normalize/modern-normalize.css'
import { createRouter, createWebHashHistory } from 'vue-router'
import messages from '@intlify/unplugin-vue-i18n/messages'
import { createI18n } from 'vue-i18n'

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
app.use(createI18n({ legacy: false, locale: 'fr', messages, globalInject: false }))

app.mount('#app')
