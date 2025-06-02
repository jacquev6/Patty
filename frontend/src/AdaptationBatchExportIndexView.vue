<script setup lang="ts">
import type { AdaptedExercise } from './apiClient'

type Data = {
  exerciseId: string
  studentAnswersStorageKey: string
  adaptedExercise: AdaptedExercise
}[]

const data = JSON.parse('##TO_BE_SUBSTITUTED_ADAPTATION_BATCH_EXPORT_DATA##') as Data // @todo Factorize with AdaptationBatchExportExerciseView.vue
</script>

<template>
  <p v-for="exercise in data">
    <RouterLink :to="{ name: 'exercise', params: { id: exercise.exerciseId } }"
      >Exercise {{ exercise.exerciseId }}</RouterLink
    >
  </p>
</template>
