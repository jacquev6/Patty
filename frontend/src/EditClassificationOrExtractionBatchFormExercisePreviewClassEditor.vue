<script setup lang="ts">
import { onMounted, reactive } from 'vue'

import IdentifiedUser from './IdentifiedUser.vue'
import WhiteSpace from './WhiteSpace.vue'
import { useAuthenticatedClient } from './apiClient'

const model = defineModel<string>()

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
  <WhiteSpace />
  <span class="user">(fixed by <IdentifiedUser />)</span>
</template>

<style scoped>
span.user {
  color: grey;
}
</style>
