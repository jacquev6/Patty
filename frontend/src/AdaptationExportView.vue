<script setup lang="ts">
import type { AdaptedExercise } from './apiClient'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'

type Data = {
  exerciseId: string
  adaptedExercise: AdaptedExercise
}

const data = JSON.parse('##TO_BE_SUBSTITUTED_ADAPTATION_EXPORT_DATA##') as Data
</script>

<template>
  <AdaptedExerciseRenderer v-bind="data" style="height: 100vh" />
</template>
