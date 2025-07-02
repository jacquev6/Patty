<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import { type Textbook, useAuthenticatedClient } from './apiClient'
import EditTextbookForm from './EditTextbookForm.vue'
import assert from './assert'
import { preprocess as preprocessAdaptation } from './adaptations'
import { useBreadcrumbsStore } from './BreadcrumbsStore'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()
const breadcrumbsStore = useBreadcrumbsStore()

const found = ref<boolean | null>(null)
const textbook = ref<Textbook | null>(null)
const availableStrategySettings = ref<string[] | null>(null)

let refreshes = 0

let refreshTimeoutId: number | null = null

async function refresh() {
  const response = await client.GET(`/api/textbooks/{id}`, { params: { path: { id: props.id } } })
  if (response.response.status === 404) {
    found.value = false
    textbook.value = null
  } else {
    found.value = true
    assert(response.data !== undefined)
    textbook.value = response.data.textbook
    availableStrategySettings.value = response.data.availableStrategySettings
    breadcrumbsStore.set([
      { textKey: 'textbooks' },
      { textKey: 'existingTextbook', textArgs: { title: textbook.value.title }, to: {} },
    ])
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
    <template v-if="availableStrategySettings !== null && textbook !== null">
      <EditTextbookForm :availableStrategySettings :textbook @textbookUpdated="textbookUpdated" />
    </template>
    <template v-else-if="found === false">
      <h1>Not found</h1>
    </template>
  </div>
</template>
