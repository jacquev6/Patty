<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { useApiClient } from './apiClient'

const router = useRouter()
const client = useApiClient()

const input =
  ref(`Aujourd'hui, l'école est fermée à cause de la neige ! Les enfants sont ravis, mais les parents un peu moins...

Les enfants ont enfilé leurs bottes, leurs moufles et leurs bonnets.
Ils sont prêts à aller jouer dehors.`)

async function submit() {
  console.log(input.value)
  const response = await client.POST('/api/tokenization', {
    body: {
      input_text: input.value,
    },
  })

  if (response.data !== undefined) {
    router.push({ name: 'tokenization', params: { id: response.data.id } })
  }
}
</script>

<template>
  <h1>Input text</h1>
  <textarea v-model="input" rows="10" cols="80"></textarea>
  <p><button @click="submit">Submit</button></p>
</template>
