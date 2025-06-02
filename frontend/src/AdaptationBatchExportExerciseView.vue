<script setup lang="ts">
import { computed } from 'vue'

import type { AdaptedExercise } from './apiClient'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'

type Data = {
  exerciseId: string
  studentAnswersStorageKey: string
  adaptedExercise: AdaptedExercise
}[]

const data = JSON.parse('##TO_BE_SUBSTITUTED_ADAPTATION_BATCH_EXPORT_DATA##') as Data // @todo Factorize with AdaptationBatchExportIndexView.vue

const props = defineProps<{
  id: string
}>()

const exercise = computed(() => {
  const exercise = data.find((exercise) => exercise.exerciseId === props.id)
  if (!exercise) {
    throw new Error('Exercise not found')
  }
  return exercise
})
</script>

<template>
  <AdaptedExerciseRenderer :navigateUsingArrowKeys="true" v-bind="exercise" style="height: 100vh" />
</template>
