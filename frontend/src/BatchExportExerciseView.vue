<script setup lang="ts">
import { computed } from 'vue'

import type { AdaptedExercise } from './apiClient'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'

type Data = {
  exerciseId: string
  studentAnswersStorageKey: string
  adaptedExercise: AdaptedExercise
}[]

const data = JSON.parse('##TO_BE_SUBSTITUTED_BATCH_EXPORT_DATA##') as Data // @todo Factorize with BatchExportIndexView.vue
console.log('data', data)

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
  <AdaptedExerciseRenderer v-bind="exercise" style="height: 100vh" />
</template>
