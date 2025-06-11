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
const extractionLlmResponseSchema = ref<Record<string, never>>({})

let refreshes = 0

let refreshTimeoutId: number | null = null

async function refresh() {
  const extractionBatchPromise = client.GET(`/api/extraction-batches/{id}`, { params: { path: { id: props.id } } })
  const extractionLlmResponseSchemaPromise = client.GET('/api/extraction-llm-response-schema')

  const extractionBatchResponse = await extractionBatchPromise
  if (extractionBatchResponse.response.status === 404) {
    found.value = false
    extractionBatch.value = null
  } else {
    found.value = true
    assert(extractionBatchResponse.data !== undefined)
    extractionBatch.value = extractionBatchResponse.data

    let needsRefresh = false
    for (const page of extractionBatchResponse.data.pages) {
      if (page.assistantResponse === null) {
        needsRefresh = true
      } else {
        for (const exercise of page.exercises) {
          if (extractionBatchResponse.data.runClassification && exercise.exerciseClass === null) {
            needsRefresh = true
            break
          }
          if (exercise.adaptation !== null && preprocessAdaptation(exercise.adaptation).status.kind === 'inProgress') {
            needsRefresh = true
            break
          }
        }
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

  const extractionLlmResponseSchemaResponse = await extractionLlmResponseSchemaPromise
  if (extractionLlmResponseSchemaResponse.data !== undefined) {
    extractionLlmResponseSchema.value = extractionLlmResponseSchemaResponse.data
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
      <EditExtractionBatchForm :extractionBatch :extractionLlmResponseSchema />
    </template>
    <template v-else-if="found === false">
      <h1>Not found</h1>
    </template>
  </div>
</template>
