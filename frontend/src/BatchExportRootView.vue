<script lang="ts" setup>
import type { AdaptedExercise } from './apiClient'

export type Data = {
  exerciseId: string
  studentAnswersStorageKey: string
  adaptedExercise: AdaptedExercise
}[]

const data = JSON.parse('##TO_BE_SUBSTITUTED_BATCH_EXPORT_DATA##') as Data
</script>

<template>
  <RouterView v-slot="{ Component }">
    <component :is="Component" :data />
  </RouterView>
</template>
