<script setup lang="ts">
import { onMounted, ref } from 'vue'

import CreateAdaptationForm from './CreateAdaptationForm.vue'
import { type LlmModel, client } from './apiClient'

const availableLlmModels = ref<LlmModel[]>([])

const defaultSystemPrompt = ref('')

const defaultInputText = ref(`5 Complète avec "le vent" ou "la pluie"
a. Les feuilles sont chahutées par ...
b. Les vitres sont mouillées par ...
`)

onMounted(async () => {
  const systemPromptPromise = client.GET('/api/adaptation/default-system-prompt')
  const llmModelsPromise = client.GET('/api/available-llm-models')

  const systemPromptResponse = await systemPromptPromise
  if (systemPromptResponse.data !== undefined) {
    defaultSystemPrompt.value = systemPromptResponse.data
  }

  const llmModelsResponse = await llmModelsPromise
  if (llmModelsResponse.data !== undefined) {
    availableLlmModels.value = llmModelsResponse.data
  }
})
</script>

<template>
  <CreateAdaptationForm
    v-if="availableLlmModels.length !== 0"
    :availableLlmModels
    :defaultSystemPrompt
    :defaultInputText
  />
</template>
