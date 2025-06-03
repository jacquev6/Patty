<script setup lang="ts">
import { type ClassificationBatch } from './apiClient'
import LlmModelSelector from './LlmModelSelector.vue'
import EditClassificationBatchFormExercisePreview from './EditClassificationBatchFormExercisePreview.vue'

defineProps<{
  classificationBatch: ClassificationBatch
}>()
</script>

<template>
  <h1>Settings</h1>
  <p>Created by: {{ classificationBatch.createdBy }}</p>
  <p>
    Run adaptation after classification:
    <template v-if="classificationBatch.modelForAdaptation === null">no</template>
    <template v-else
      >yes, using
      <LlmModelSelector :availableLlmModels="[]" :disabled="true" :modelValue="classificationBatch.modelForAdaptation">
        <template #provider>provider</template>
        <template #model> and model</template>
      </LlmModelSelector>
      with the latest settings for each known exercise class.</template
    >
  </p>
  <h1>Inputs</h1>
  <template v-for="(exercise, index) in classificationBatch.exercises">
    <EditClassificationBatchFormExercisePreview
      header="h2"
      :adaptationWasRequested="classificationBatch.modelForAdaptation !== null"
      :exercise
      :index
    />
  </template>
</template>

<style scoped>
span.inProgress {
  color: gray;
  font-size: 70%;
}
</style>
