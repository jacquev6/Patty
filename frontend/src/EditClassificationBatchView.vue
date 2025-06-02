<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

import { type ClassificationBatch, useAuthenticatedClient } from './apiClient'
import assert from './assert'
import EditClassificationBatchForm from './EditClassificationBatchForm.vue'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

const found = ref<boolean | null>(null)
const classificationBatch = ref<ClassificationBatch | null>(null)
let refreshes = 0

let refreshTimeoutId: number | null = null

async function refresh() {
  const response = await client.GET(`/api/classification-batches/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    found.value = false
    classificationBatch.value = null
  } else {
    found.value = true
    assert(response.data !== undefined)
    classificationBatch.value = response.data

    let needsRefresh = false
    for (const exercise of classificationBatch.value.exercises) {
      if (exercise.exerciseClass === null) {
        needsRefresh = true
        break
      }
    }
    if (needsRefresh) {
      refreshTimeoutId = setTimeout(refresh, 500 * Math.pow(1.1, refreshes))
      refreshes++
    } else {
      refreshTimeoutId = null
      refreshes = 0
    }
  }
}

onMounted(refresh)

onUnmounted(() => {
  if (refreshTimeoutId !== null) {
    clearTimeout(refreshTimeoutId)
    refreshTimeoutId = null
  }
  refreshes = 0
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <template v-if="classificationBatch !== null">
      <EditClassificationBatchForm :classificationBatch />
    </template>
    <template v-else-if="found === false">
      <h1>Not found</h1>
    </template>
  </div>
</template>
