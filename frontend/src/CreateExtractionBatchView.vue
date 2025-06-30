<script setup lang="ts">
import { ref, onMounted } from 'vue'

import CreateExtractionBatchForm from './CreateExtractionBatchForm.vue'
import { type ExtractionStrategy, useAuthenticatedClient } from './apiClient'
import { useBreadcrumbsStore } from './BreadcrumbsStore'

const client = useAuthenticatedClient()
const breadcrumbsStore = useBreadcrumbsStore()

const latestExtractionStrategy = ref<ExtractionStrategy | null>(null)

onMounted(async () => {
  const response = await client.GET('/api/latest-extraction-strategy')
  if (response.data !== undefined) {
    latestExtractionStrategy.value = response.data
  }

  breadcrumbsStore.set([{ textKey: 'sandbox' }, { textKey: 'newExtractionBatch', to: {} }])
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateExtractionBatchForm v-if="latestExtractionStrategy !== null" :latestExtractionStrategy />
  </div>
</template>
