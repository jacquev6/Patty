import { createApp } from 'vue'
import 'modern-normalize/modern-normalize.css'
import { createRouter, createWebHashHistory } from 'vue-router'
import messages from '@intlify/unplugin-vue-i18n/messages'
import { createI18n } from 'vue-i18n'

import RootView from './RootView.vue'
import IndexView from './IndexView.vue'
import ExerciseView from './ExerciseView.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'index',
      component: IndexView,
    },
    {
      path: '/:id',
      name: 'exercise',
      component: ExerciseView,
      props: true,
    },
  ],
})

const app = createApp(RootView)

app.use(router)
app.use(createI18n({ legacy: false, locale: 'fr', messages, globalInject: false }))

app.mount('#app')
