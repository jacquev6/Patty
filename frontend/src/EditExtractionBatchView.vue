<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

import EditExtractionBatchForm from './EditExtractionBatchForm.vue'
import { type ExtractionBatch, useAuthenticatedClient } from './apiClient'
import assert from './assert'
import { preprocess as preprocessAdaptation } from './adaptations'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

const found = ref<boolean | null>(null)
const extractionBatch = ref<ExtractionBatch | null>(null)
let refreshes = 0

let refreshTimeoutId: number | null = null

async function refresh() {
  const response = await client.GET(`/api/extraction-batches/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    found.value = false
    extractionBatch.value = null
  } else {
    found.value = true
    assert(response.data !== undefined)
    extractionBatch.value = response.data

    let needsRefresh = false
    for (const page of response.data.pages) {
      if (page.done) {
        for (const exercise of page.exercises) {
          if (response.data.runClassification && exercise.exerciseClass === null) {
            needsRefresh = true
            break
          }
          if (exercise.adaptation !== null && preprocessAdaptation(exercise.adaptation).status.kind === 'inProgress') {
            needsRefresh = true
            break
          }
        }
      } else {
        needsRefresh = true
      }
      if (needsRefresh) {
        break
      }
    }
    if (needsRefresh) {
      refreshTimeoutId = window.setTimeout(refresh, 500 * Math.pow(1.1, refreshes))
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
    window.clearTimeout(refreshTimeoutId)
    refreshTimeoutId = null
  }
  refreshes = 0
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <template v-if="extractionBatch !== null">
      <EditExtractionBatchForm :extractionBatch />
    </template>
    <template v-else-if="found === false">
      <h1>Not found</h1>
    </template>
  </div>
</template>
