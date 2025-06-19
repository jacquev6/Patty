<script setup lang="ts">
import { computed } from 'vue'

import type { Data } from './BatchExportRootView.vue'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'

const props = defineProps<{
  data: Data
  id: string
}>()

const exercise = computed(() => {
  const exercise = props.data.find((exercise) => exercise.exerciseId === props.id)
  if (!exercise) {
    throw new Error('Exercise not found')
  }
  return exercise
})
</script>

<template>
  <AdaptedExerciseRenderer :navigateUsingArrowKeys="true" v-bind="exercise" style="height: 100vh" />
</template>
