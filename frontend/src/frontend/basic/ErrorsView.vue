<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { defineComponent, h, onMounted, ref } from 'vue'

import { useBreadcrumbsStore } from './BreadcrumbsStore'
import { useAuthenticatedClient, type ErrorCaughtByFrontend } from '@/frontend/ApiClient'
import assert from '$/assert'
import WhiteSpace from '$/WhiteSpace.vue'

const breadcrumbsStore = useBreadcrumbsStore()
const client = useAuthenticatedClient()

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const undef: any = undefined
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const nul: any = null

const triggerRepeatedAsserts = ref(false)
const emptyObjects = [{}, {}, {}, {}, {}, {}, {}, {}, {}, {}] as { notAnAttribute: { b: boolean } }[]

const TestComponent = defineComponent({
  name: 'TestComponent',
  props: {
    notAnAttribute: {
      type: Object as () => { b: boolean },
      required: true,
    },
  },
  setup(props) {
    return () => h('div', {}, props.notAnAttribute.b ? [] : [])
  },
})

const errors: [string, () => void][] = [
  ['Assert', () => assert(false)],
  ['Dereference undefined', () => undef.foo],
  ['Dereference null', () => nul.foo],
  ['Unhandled rejection', () => Promise.reject('This is the reason')],
  [
    'Throw exception',
    () => {
      throw new Error('This is the error')
    },
  ],
  ['Network error', () => fetch('http://not-a-host/not-a-path/')],
  [
    'Repeated undefined',
    () => {
      triggerRepeatedAsserts.value = true
    },
  ],
]

if (window.location.search.includes('reject')) {
  Promise.reject('This is the reason')
}

const existingErrors = ref<ErrorCaughtByFrontend[]>([])

onMounted(async () => {
  const response = await client.GET('/api/errors-caught-by-frontend')

  if (response.data !== undefined) {
    existingErrors.value = response.data.errors
  }

  breadcrumbsStore.set([{ textKey: 'errors', to: {} }])
})

const showOnlyWithoutGithubIssue = ref(false)
</script>

<template>
  <div>
    <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
    <h1>Generate synthetic errors</h1>
    <p>
      <template v-for="[title, f] of errors">
        <button @click="f">{{ title }}</button>
        <WhiteSpace />
      </template>
    </p>
    <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
    <h1>Previously caught</h1>
    <p>
      <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
      <label>
        Show only errors without a GitHub issue number
        <input v-model="showOnlyWithoutGithubIssue" type="checkbox" />
      </label>
    </p>
    <template v-for="error in existingErrors">
      <template v-if="!showOnlyWithoutGithubIssue || error.githubIssueNumber === null">
        <pre>{{ error }}</pre>
      </template>
    </template>
    <template v-if="triggerRepeatedAsserts">
      <TestComponent v-for="emptyObject in emptyObjects" :notAnAttribute="emptyObject.notAnAttribute" />
    </template>
  </div>
</template>
