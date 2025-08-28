<script setup lang="ts">
import { onMounted, reactive } from 'vue'

import { useAuthenticatedClient } from '@/apiClient'

const model = defineModel<string>({ required: true })

const client = useAuthenticatedClient()

const classNames = reactive<string[]>([])

onMounted(async () => {
  const response = await client.GET('/api/exercise-classes')
  if (response.data !== undefined) {
    classNames.splice(0, classNames.length, ...response.data)
  }
})
</script>

<template>
  <select data-cy="exercise-class" v-model="model">
    <option v-for="name in classNames">{{ name }}</option>
  </select>
</template>

<style scoped>
span.user {
  color: grey;
}
</style>
