<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { type Batch } from './apiClient'
import ResizableColumns from './ResizableColumns.vue'
import AdaptationStrategyEditor from './AdaptationStrategyEditor.vue'
import AdaptationPreview from './EditBatchFormAdaptationPreview.vue'
import { preprocess as preprocessAdaptation } from './adaptations'

const props = defineProps<{
  batch: Batch
}>()

const strategy = ref(props.batch.strategy)
watch(
  () => props.batch.strategy,
  (newValue) => {
    strategy.value = newValue
  },
)

const adaptations = computed(() => props.batch.adaptations.map(preprocessAdaptation))
</script>

<template>
  <ResizableColumns :columns="[1, 2]">
    <template #col-1>
      <p>Created by: {{ batch.createdBy }}</p>
      <AdaptationStrategyEditor :availableLlmModels="[]" :disabled="true" v-model="strategy" />
    </template>
    <template #col-2>
      <h1>Inputs</h1>
      <AdaptationPreview v-for="(adaptation, index) in adaptations" :index :adaptation />
    </template>
  </ResizableColumns>
</template>
