<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { type MistralaiModelName, type OpenaiModelName, useApiClient } from './apiClient'

const router = useRouter()
const client = useApiClient()

const llmProviders = ['mistralai', 'openai'] as const
const llmProvider = ref<(typeof llmProviders)[number]>(llmProviders[0])

const mistralaiModels: MistralaiModelName[] = ['mistral-large-2411', 'mistral-small-2501']
const mistralaiModel = ref<MistralaiModelName>(mistralaiModels[0])

const openaiModels: OpenaiModelName[] = ['gpt-4o-2024-08-06', 'gpt-4o-mini-2024-07-18']
const openaiModel = ref<OpenaiModelName>(openaiModels[0])

const systemPrompt = ref('')

const inputText =
  ref(`Aujourd'hui, l'école est fermée à cause de la neige ! Les enfants sont ravis, mais les parents un peu moins...

Les enfants ont enfilé leurs bottes, leurs moufles et leurs bonnets.
Ils sont prêts à aller jouer dehors.`)

const disabled = ref(true)

onMounted(async () => {
  const response = await client.GET('/api/tokenization/default-system-prompt')

  if (response.data !== undefined) {
    systemPrompt.value = response.data
    disabled.value = false
  }
})

async function submit() {
  disabled.value = true

  const llm_model =
    llmProvider.value === 'mistralai'
      ? {
          provider: 'mistralai' as const,
          model: mistralaiModel.value,
        }
      : {
          provider: 'openai' as const,
          model: openaiModel.value,
        }

  const responsePromise = client.POST('/api/tokenization', {
    body: {
      llm_model,
      system_prompt: systemPrompt.value,
      input_text: inputText.value,
    },
  })

  const response = await responsePromise
  disabled.value = false

  if (response.data !== undefined) {
    router.push({ name: 'tokenization', params: { id: response.data.id } })
  }
}
</script>

<template>
  <h1>LLM provider and model name</h1>
  <select v-model="llmProvider" :disabled>
    <option v-for="llmProvider in llmProviders">{{ llmProvider }}</option>
  </select>
  <select v-if="llmProvider === 'mistralai'" v-model="mistralaiModel" :disabled>
    <option v-for="model in mistralaiModels">{{ model }}</option>
  </select>
  <select v-else v-model="openaiModel" :disabled>
    <option v-for="model in openaiModels">{{ model }}</option>
  </select>
  <h1>System prompt</h1>
  <textarea v-model="systemPrompt" rows="15" cols="120" :disabled></textarea>
  <h1>Input text</h1>
  <textarea v-model="inputText" rows="10" cols="120" :disabled></textarea>
  <p><button @click="submit" :disabled>Submit</button></p>
</template>
