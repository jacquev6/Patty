import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import 'modern-normalize/modern-normalize.css'
import { createPinia } from 'pinia'

import pdfjs from './pdfjs'
import './main.css'
import IndexView from './IndexView.vue'
import CreateAdaptationBatchView from './CreateAdaptationBatchView.vue'
import CreateClassificationBatchView from './CreateClassificationBatchView.vue'
import CreateExtractionBatchView from './CreateExtractionBatchView.vue'
import EditAdaptationView from './EditAdaptationView.vue'
import EditAdaptationBatchView from './EditAdaptationBatchView.vue'
import EditExtractionBatchView from './EditExtractionBatchView.vue'
import FrontendRootView from './FrontendRootView.vue'
import ExamplesView from './ExamplesView.vue'
import EditTextbookView from './EditTextbookView.vue'
import EditClassificationBatchView from './EditClassificationBatchView.vue'

pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'index',
      component: IndexView,
    },
    {
      path: '/new-extraction-batch',
      name: 'create-extraction-batch',
      component: CreateExtractionBatchView,
    },
    {
      path: '/extraction-batch-:id',
      name: 'extraction-batch',
      component: EditExtractionBatchView,
      props: true,
    },
    {
      path: '/new-classification-batch',
      name: 'create-classification-batch',
      component: CreateClassificationBatchView,
    },
    {
      path: '/classification-batch-:id',
      name: 'classification-batch',
      component: EditClassificationBatchView,
      props: true,
    },
    {
      path: '/new-adaptation-batch',
      name: 'create-adaptation-batch',
      component: CreateAdaptationBatchView,
      props: (route) => ({ base: route.query.base ?? null }),
    },
    {
      path: '/adaptation-batch-:id',
      name: 'adaptation-batch',
      component: EditAdaptationBatchView,
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
