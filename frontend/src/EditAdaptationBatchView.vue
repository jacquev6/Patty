<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import { type AdaptationBatch, useAuthenticatedClient } from './apiClient'
import assert from './assert'
import EditAdaptationBatchForm from './EditAdaptationBatchForm.vue'
import { preprocess as preprocessAdaptation } from './adaptations'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

const found = ref<boolean | null>(null)
const adaptationBatch = ref<AdaptationBatch | null>(null)
let refreshes = 0

let refreshTimeoutId: number | null = null

async function refresh() {
  const response = await client.GET(`/api/adaptation/adaptation-batch/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    found.value = false
    adaptationBatch.value = null
  } else {
    found.value = true
    assert(response.data !== undefined)
    adaptationBatch.value = response.data

    let needsRefresh = false
    for (const adaptation of adaptationBatch.value.adaptations) {
      if (preprocessAdaptation(adaptation).status.kind === 'inProgress') {
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
    <template v-if="adaptationBatch !== null">
      <EditAdaptationBatchForm :adaptationBatch />
    </template>
    <template v-else-if="found === false">
      <h1>Not found</h1>
    </template>
  </div>
</template>
