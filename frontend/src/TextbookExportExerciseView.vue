<script setup lang="ts">
import { computed } from 'vue'

import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'
import assert from './assert'
import type { Data } from './TextbookExportRootView.vue'

const props = defineProps<{
  id: string
  data: Data
}>()

const exercise = computed(() => {
  const exercise = props.data.exercises.find(
    (exercise) => exercise.kind === 'adapted' && exercise.exerciseId === props.id,
  )
  if (!exercise) {
    throw new Error('Exercise not found')
  }
  assert(exercise.kind === 'adapted')
  return exercise
})
</script>

<template>
  <AdaptedExerciseRenderer :navigateUsingArrowKeys="true" v-bind="exercise" style="height: 100vh" />
</template>
