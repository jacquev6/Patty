// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import 'modern-normalize/modern-normalize.css'
import { createPinia } from 'pinia'
import messages from '@intlify/unplugin-vue-i18n/messages'
import { createI18n } from 'vue-i18n'

import pdfjs from '$/pdfjs'
import './main.css'
import IndexView from './IndexView.vue'
import CreateAdaptationBatchView from './sandbox/CreateAdaptationBatchView.vue'
import CreateClassificationBatchView from './sandbox/CreateClassificationBatchView.vue'
import CreateExtractionBatchView from './sandbox/CreateExtractionBatchView.vue'
import EditAdaptationView from './common/EditAdaptationView.vue'
import EditAdaptationBatchView from './sandbox/EditAdaptationBatchView.vue'
import EditExtractionBatchView from './sandbox/EditExtractionBatchView.vue'
import FrontendRootView from './basic/RootView.vue'
import AdaptedExerciseExamplesView from './AdaptedExerciseExamplesView.vue'
import EditTextbookView from './textbooks/EditTextbookView.vue'
import EditTextbookPageView from './textbooks/EditTextbookPageView.vue'
import EditClassificationBatchView from './sandbox/EditClassificationBatchView.vue'
import { useBreadcrumbsStore } from './basic/BreadcrumbsStore'
import ErrorsView from './basic/ErrorsView.vue'
import CreateTextbookView from './textbooks/CreateTextbookView.vue'

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
      path: '/new-textbook',
      name: 'create-textbook',
      component: CreateTextbookView,
    },
    {
      path: '/textbook-:id',
      name: 'textbook',
      component: EditTextbookView,
      props: true,
    },
    {
      path: '/textbook-:textbookId/page-:pageNumber',
      name: 'textbook-page',
      component: EditTextbookPageView,
      props: ({ params: { textbookId, pageNumber } }) => ({
        textbookId,
        pageNumber: Number.parseInt(pageNumber as string),
      }),
    },
    {
      path: '/adapted-exercice-examples',
      name: 'adapted-exercice-examples',
      component: AdaptedExerciseExamplesView,
    },
    {
      path: '/errors',
      component: ErrorsView,
      name: 'errors',
    },
  ],
})

export const app = createApp(FrontendRootView)

app.use(router)
app.use(createPinia())
app.use(
  createI18n({
    legacy: false,
    locale: 'en',
    messages,
    datetimeFormats: {
      en: {
        long: {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          hour12: true,
        },
        'long-date': {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        },
      },
      fr: {
        long: {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
          hour12: false,
        },
        'long-date': {
          year: 'numeric',
          month: 'long',
          day: 'numeric',
        },
      },
    },
    // Avoid using $t by mistake: it does not know about the [local scope](https://vue-i18n.intlify.dev/guide/essentials/scope.html#local-scope)
    // populated by the i18n tag in [single-file components](https://vue-i18n.intlify.dev/guide/advanced/sfc.html)
    globalInjection: false,
  }),
)

const breadcrumbsStore = useBreadcrumbsStore()

router.beforeEach(() => {
  breadcrumbsStore.set([])
  return true
})

app.mount('#app')
