<script setup lang="ts">
import { ref, onMounted } from 'vue'

import CreateClassificationBatchForm from './CreateClassificationBatchForm.vue'
import { type LlmModel, useAuthenticatedClient } from './apiClient'

const client = useAuthenticatedClient()

const availableLlmModels = ref<LlmModel[]>([])

onMounted(async () => {
  const response = await client.GET('/api/available-llm-models')
  if (response.data !== undefined) {
    availableLlmModels.value = response.data
  }
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <CreateClassificationBatchForm v-if="availableLlmModels.length !== 0" :availableLlmModels />
  </div>
</template>
