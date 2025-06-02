<script setup lang="ts">
import { type ClassificationBatch } from './apiClient'
import LlmModelSelector from './LlmModelSelector.vue'

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
      with the latest settings for each class.</template
    >
  </p>
  <h1>Inputs</h1>
  <template v-for="(exercise, exerciseIndex) in classificationBatch.exercises">
    <h2>
      Input {{ exerciseIndex + 1
      }}<span v-if="exercise.exerciseClass === null" class="inProgress"> (in progress, will refresh when done)</span>
      <template v-else>: {{ exercise.exerciseClass }} </template>
    </h2>
  </template>
</template>

<style scoped>
span.inProgress {
  color: gray;
  font-size: 70%;
}
</style>
