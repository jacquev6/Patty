<script setup lang="ts">
import { onMounted, ref } from 'vue'

import { useApiClient } from './apiClient'

const client = useApiClient()

const cheeseName = ref<string>('<loading>')
const disabled = ref<boolean>(false)

async function update() {
  disabled.value = true
  const response = await client.GET('/api/get-cheese')

  if (response.data !== undefined) {
    cheeseName.value = response.data.name
  }

  setTimeout(() => {
    disabled.value = false
  }, 1200) // Avoid hitting MistralAi rate limiting
}

onMounted(update)
</script>

<template>
  <p>French cheese: {{ cheeseName }}</p>
  <p><button @click="update" :disabled>Another?</button></p>
  <p><RouterLink :to="{ name: 'create-tokenization' }">New tokenization</RouterLink></p>
</template>
