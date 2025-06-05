<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

import { type LlmModel, useAuthenticatedClient } from './apiClient'
import IdentifiedUser from './IdentifiedUser.vue'
import { useIdentifiedUserStore } from './IdentifiedUserStore'

defineProps<{
  availableLlmModels: LlmModel[]
}>()

const router = useRouter()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const disabled = false // @todo Disable when no PDF file has been opened

const busy = ref(false)

async function submit() {
  busy.value = true
  const response = await client.POST('/api/extraction-batches', {
    body: {
      creator: identifiedUser.identifier,
    },
  })
  busy.value = false
  if (response.data !== undefined) {
    router.push({ name: 'extraction-batch', params: { id: response.data.id } })
  }
}
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: <IdentifiedUser /></p>
  <p><button @click="submit" :disabled>Submit</button></p>
</template>
