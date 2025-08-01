<script setup lang="ts">
import { computed } from 'vue'

import { type AdaptationBatch } from './apiClient'
import ResizableColumns from './ResizableColumns.vue'
import AdaptationStrategyEditor from './AdaptationStrategyEditor.vue'
import AdaptationPreview from './EditAdaptationBatchFormAdaptationPreview.vue'
import { preprocess as preprocessAdaptation } from './adaptations'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'

const props = defineProps<{
  adaptationBatch: AdaptationBatch
}>()

const authenticationTokenStore = useAuthenticationTokenStore()

const adaptations = computed(() => props.adaptationBatch.adaptations.map(preprocessAdaptation))
</script>

<template>
  <ResizableColumns :columns="[1, 2]">
    <template #col-1>
      <p>Created by: {{ adaptationBatch.createdBy }}</p>
      <AdaptationStrategyEditor
        :availableStrategySettings="[]"
        :disabled="true"
        :modelValue="adaptationBatch.strategy"
      />
    </template>
    <template #col-2>
      <p>
        <RouterLink :to="{ name: 'create-adaptation-batch', query: { base: adaptationBatch.id } }"
          >New batch based on this one</RouterLink
        >
      </p>
      <p>
        Download
        <a :href="`/api/export/adaptation-batch/${adaptationBatch.id}.html?token=${authenticationTokenStore.token}`"
          >standalone HTML</a
        >
        or
        <a :href="`/api/export/adaptation-batch/${adaptationBatch.id}.json?token=${authenticationTokenStore.token}`"
          >JSON data</a
        >
      </p>
      <h1>Inputs</h1>
      <AdaptationPreview v-for="(adaptation, index) in adaptations" header="h2" :index :adaptation />
    </template>
  </ResizableColumns>
</template>
