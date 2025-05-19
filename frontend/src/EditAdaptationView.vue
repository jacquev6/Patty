<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { useAuthenticatedClient, type Adaptation } from './apiClient'
import assert from './assert'
import EditAdaptationForm from './EditAdaptationForm.vue'
import { preprocess as preprocessAdaptation } from './adaptations'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

const found = ref<boolean | null>(null)
const apiAdaptation = ref<Adaptation | null>(null)

const adaptation = computed(() => {
  if (apiAdaptation.value === null) {
    return null
  } else {
    return preprocessAdaptation(apiAdaptation.value)
  }
})

onMounted(async () => {
  const response = await client.GET(`/api/adaptation/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    found.value = false
    apiAdaptation.value = null
  } else {
    found.value = true
    assert(response.data !== undefined)
    apiAdaptation.value = response.data
  }
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <template v-if="adaptation !== null">
      <EditAdaptationForm :adaptation @adaptationUpdated="apiAdaptation = $event" />
    </template>
    <template v-else-if="found === false">
      <h1>Not found</h1>
    </template>
  </div>
</template>
