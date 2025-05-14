<script setup lang="ts">
import { computed } from 'vue'

import { type Data } from './TextbookExportIndexView.vue'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'

const data = JSON.parse('##TO_BE_SUBSTITUTED_TEXTBOOK_EXPORT_DATA##') as Data // @todo Factorize with TextbookExportIndexView.vue

const props = defineProps<{
  id: string
}>()

const exercise = computed(() => {
  const exercise = data.exercises.find((exercise) => exercise.exerciseId === props.id)
  if (!exercise) {
    throw new Error('Exercise not found')
  }
  return exercise
})
</script>

<template>
  <AdaptedExerciseRenderer :navigateUsingArrowKeys="true" v-bind="exercise" style="height: 100vh" />
</template>
