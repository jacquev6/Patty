<script setup lang="ts">
import { ref, onMounted } from 'vue'

import CreateExtractionBatchForm from './CreateExtractionBatchForm.vue'
import { type ExtractionStrategy, useAuthenticatedClient } from './apiClient'

const client = useAuthenticatedClient()

const latestExtractionStrategy = ref<ExtractionStrategy | null>(null)

onMounted(async () => {
  const response = await client.GET('/api/latest-extraction-strategy')
  if (response.data !== undefined) {
    latestExtractionStrategy.value = response.data
  }
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateExtractionBatchForm v-if="latestExtractionStrategy !== null" :latestExtractionStrategy />
  </div>
</template>
