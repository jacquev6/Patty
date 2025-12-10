<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed } from 'vue'

import AdaptedExerciseRenderer from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import assert from '$/assert'
import type { Data } from './RootView.vue'
import { useDisplayPreferences } from './displayPreferences'

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

const { tricolored } = useDisplayPreferences()
</script>

<template>
  <AdaptedExerciseRenderer :navigateUsingArrowKeys="true" v-bind="exercise" style="height: 100vh" :tricolored />
</template>
