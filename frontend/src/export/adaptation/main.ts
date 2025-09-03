import { createApp } from 'vue'
import 'modern-normalize/modern-normalize.css'
import messages from '@intlify/unplugin-vue-i18n/messages'
import { createI18n } from 'vue-i18n'

import MainView from './MainView.vue'

const app = createApp(MainView)
app.use(createI18n({ legacy: false, locale: 'fr', messages, globalInject: false }))

app.mount('#app')
