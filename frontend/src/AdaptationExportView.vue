<script setup lang="ts">
import type { AdaptedExercise } from '@/apiClient'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'

type Data = {
  exerciseId: string
  adaptedExercise: AdaptedExercise
}

const data = JSON.parse('{{ data }}') as Data
</script>

<template>
  <AdaptedExerciseRenderer v-bind="data" style="height: 100vh" />
</template>
