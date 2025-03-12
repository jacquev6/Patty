<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useApiClient } from './apiClient'

const router = useRouter()
const client = useApiClient()

const systemPrompt = ref('')

const inputText =
  ref(`Aujourd'hui, l'école est fermée à cause de la neige ! Les enfants sont ravis, mais les parents un peu moins...

Les enfants ont enfilé leurs bottes, leurs moufles et leurs bonnets.
Ils sont prêts à aller jouer dehors.`)

const disabled = ref(true)

onMounted(async () => {
  const response = await client.GET('/api/default-tokenization-system-prompt')

  if (response.data !== undefined) {
    systemPrompt.value = response.data
    disabled.value = false
  }
})

async function submit() {
  disabled.value = true

  const responsePromise = client.POST('/api/tokenization', {
    body: {
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
  <h1>System prompt</h1>
  <textarea v-model="systemPrompt" rows="15" cols="120" :disabled></textarea>
  <h1>Input text</h1>
  <textarea v-model="inputText" rows="10" cols="120" :disabled></textarea>
  <p><button @click="submit" :disabled>Submit</button></p>
</template>
