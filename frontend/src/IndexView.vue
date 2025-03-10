<script setup lang="ts">
import { onMounted, ref } from 'vue'
import createClient from 'openapi-fetch'

import type { paths } from './openapi'

const client = createClient<paths>()

const cheeseName = ref<string>('<loading>')
const disabled = ref<boolean>(false)

async function update() {
  disabled.value = true
  const response = await client.GET('/api/get-cheese')

  if (response.data !== undefined) {
    cheeseName.value = response.data.name
  }

  setTimeout(() => { disabled.value = false }, 1200)  // Avoid hitting Mistral rate limiting
}

onMounted(update)
</script>

<template>
  <p>French cheese: {{ cheeseName }}</p>
  <p><button @click="update" :disabled>Another?</button></p>
</template>
