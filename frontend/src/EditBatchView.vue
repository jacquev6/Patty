<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { type Batch, client } from './apiClient'
import assert from './assert'
import EditBatchForm from './EditBatchForm.vue'
import { preprocess as preprocessAdaptation } from './adaptations'

const props = defineProps<{
  id: string
}>()

const found = ref<boolean | null>(null)
const batch = ref<Batch | null>(null)
let refreshes = 0

async function refresh() {
  const response = await client.GET(`/api/adaptation/batch/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    found.value = false
    batch.value = null
  } else {
    found.value = true
    assert(response.data !== undefined)
    batch.value = response.data

    let needsRefresh = false
    for (const adaptation of batch.value.adaptations) {
      if (preprocessAdaptation(adaptation).status.kind === 'inProgress') {
        needsRefresh = true
        break
      }
    }
    if (needsRefresh) {
      setTimeout(refresh, 500 * Math.pow(1.1, refreshes))
      refreshes++
    }
  }
}

onMounted(refresh)
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <template v-if="batch !== null">
      <EditBatchForm :batch />
    </template>
    <template v-else-if="found === false">
      <h1>Not found</h1>
    </template>
  </div>
</template>
