<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import { useAuthenticatedClient, type Adaptation } from './apiClient'
import assert from './assert'
import EditAdaptationForm from './EditAdaptationForm.vue'
import { preprocess as preprocessAdaptation } from './adaptations'
import { useBreadcrumbsStore, type Breadcrumbs } from './BreadcrumbsStore'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()
const breadcrumbsStore = useBreadcrumbsStore()

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
  const response = await client.GET(`/api/adaptations/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    found.value = false
    apiAdaptation.value = null
  } else {
    found.value = true
    assert(response.data !== undefined)
    apiAdaptation.value = response.data

    const breadcrumbs: Breadcrumbs = [{ text: 'Sandbox' }]
    if (apiAdaptation.value.extractionBatchId !== null) {
      breadcrumbs.push({
        text: `Extraction batch ${apiAdaptation.value.extractionBatchId}`,
        to: { name: 'extraction-batch', params: { id: apiAdaptation.value.extractionBatchId } },
      })
    } else if (apiAdaptation.value.classificationBatchId !== null) {
      breadcrumbs.push({
        text: `Classification batch ${apiAdaptation.value.classificationBatchId}`,
        to: { name: 'classification-batch', params: { id: apiAdaptation.value.classificationBatchId } },
      })
    } else if (apiAdaptation.value.adaptationBatchId !== null) {
      breadcrumbs.push({
        text: `Adaptation batch ${apiAdaptation.value.adaptationBatchId}`,
        to: { name: 'adaptation-batch', params: { id: apiAdaptation.value.adaptationBatchId } },
      })
    }

    breadcrumbs.push({ text: `Adaptation ${apiAdaptation.value.id}`, to: {} })

    breadcrumbsStore.set(breadcrumbs)
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
