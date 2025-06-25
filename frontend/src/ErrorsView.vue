<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useBreadcrumbsStore } from './BreadcrumbsStore'
import { useAuthenticatedClient, type ErrorCaughtByFrontend } from './apiClient'
import assert from './assert'
import WhiteSpace from './WhiteSpace.vue'

const breadcrumbsStore = useBreadcrumbsStore()
const client = useAuthenticatedClient()

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const undef: any = undefined
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const nul: any = null

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

  breadcrumbsStore.set([{ text: 'Errors', to: {} }])
})
</script>

<template>
  <div>
    <h1>Generate synthetic errors</h1>
    <p>
      <template v-for="[title, f] of errors">
        <button @click="f">{{ title }}</button>
        <WhiteSpace />
      </template>
    </p>
    <h1>Previously caught</h1>
    <pre v-for="error in existingErrors" :key="error.id">{{ error }}</pre>
  </div>
</template>
