<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import { type Textbook, type LlmModel, useAuthenticatedClient } from './apiClient'
import EditTextbookForm from './EditTextbookForm.vue'
import assert from './assert'
import { preprocess as preprocessAdaptation } from './adaptations'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

const found = ref<boolean | null>(null)
const textbook = ref<Textbook | null>(null)
const availableStrategySettings = ref<string[] | null>(null)
const availableLlmModels = ref<LlmModel[] | null>(null)

let refreshes = 0

let refreshTimeoutId: number | null = null

async function refresh() {
  const llmModelsPromise = client.GET('/api/available-llm-models')
  const textbookPromise = client.GET(`/api/textbooks/{id}`, { params: { path: { id: props.id } } })

  const llmModelsResponse = await llmModelsPromise
  if (llmModelsResponse.data !== undefined) {
    availableLlmModels.value = llmModelsResponse.data
  }

  const textbookResponse = await textbookPromise
  if (textbookResponse.response.status === 404) {
    found.value = false
    textbook.value = null
  } else {
    found.value = true
    assert(textbookResponse.data !== undefined)
    textbook.value = textbookResponse.data.textbook
    availableStrategySettings.value = textbookResponse.data.availableStrategySettings
    refreshIfNeeded()
  }
}

onMounted(refresh)

onUnmounted(cancelRefresh)

function textbookUpdated(newTextbook: Textbook) {
  textbook.value = newTextbook
  refreshIfNeeded()
}

function refreshIfNeeded() {
  if (needsRefresh()) {
    refreshTimeoutId = window.setTimeout(refresh, 500 * Math.pow(1.1, refreshes))
    refreshes++
  } else {
    refreshTimeoutId = null
    refreshes = 0
  }
}

function needsRefresh() {
  assert(textbook.value !== null)
  for (const adaptationBatch of textbook.value.adaptationBatches) {
    for (const adaptation of adaptationBatch.adaptations) {
      if (preprocessAdaptation(adaptation).status.kind === 'inProgress') {
        return true
      }
    }
  }
  return false
}

function cancelRefresh() {
  if (refreshTimeoutId !== null) {
    window.clearTimeout(refreshTimeoutId)
    refreshTimeoutId = null
  }
  refreshes = 0
}
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <template v-if="availableLlmModels !== null && availableStrategySettings !== null && textbook !== null">
      <EditTextbookForm :availableLlmModels :availableStrategySettings :textbook @textbookUpdated="textbookUpdated" />
    </template>
    <template v-else-if="found === false">
      <h1>Not found</h1>
    </template>
  </div>
</template>
