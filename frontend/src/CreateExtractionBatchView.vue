<script setup lang="ts">
import { ref, onMounted } from 'vue'

import CreateExtractionBatchForm from './CreateExtractionBatchForm.vue'
import { type AdaptationLlmModel, useAuthenticatedClient } from './apiClient'

const client = useAuthenticatedClient()

const availableAdaptationLlmModels = ref<AdaptationLlmModel[]>([])

onMounted(async () => {
  const response = await client.GET('/api/available-adaptation-llm-models')
  if (response.data !== undefined) {
    availableAdaptationLlmModels.value = response.data
  }
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateExtractionBatchForm v-if="availableAdaptationLlmModels.length !== 0" :availableAdaptationLlmModels />
  </div>
</template>
