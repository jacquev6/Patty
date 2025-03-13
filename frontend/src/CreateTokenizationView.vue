<script setup lang="ts">
import { onMounted, ref } from 'vue'

import CreateTokenizationForm from './CreateTokenizationForm.vue'
import { type PostTokenizationRequest, client } from './apiClient'

const availableLlmModels = ref<PostTokenizationRequest['llm_model'][]>([])

const defaultSystemPrompt = ref('')

const defaultInputText =
  ref(`Aujourd'hui, l'école est fermée à cause de la neige ! Les enfants sont ravis, mais les parents un peu moins...

Les enfants ont enfilé leurs bottes, leurs moufles et leurs bonnets.
Ils sont prêts à aller jouer dehors.`)

onMounted(async () => {
  const systemPromptPromise = client.GET('/api/tokenization/default-system-prompt')
  const llmModelsPromise = client.GET('/api/tokenization/available-llm-models')

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
  <CreateTokenizationForm
    v-if="availableLlmModels.length !== 0"
    :availableLlmModels
    :defaultSystemPrompt
    :defaultInputText
  />
</template>
