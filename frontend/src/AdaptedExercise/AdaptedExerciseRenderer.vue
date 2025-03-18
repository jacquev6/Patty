<script setup lang="ts">
import type { AdaptedExercise } from '@/apiClient'
import LineComponent from './components/LineComponent.vue'

defineProps<{
  adaptedExercise: AdaptedExercise
}>()
</script>

<template>
  <p v-for="{ contents } in adaptedExercise.instructions.lines">
    <LineComponent :contents />
  </p>
  <div v-for="page in adaptedExercise.wording.pages">
    <p v-for="{ contents } in page.lines">
      <LineComponent :contents />
    </p>
  </div>
</template>

<style scoped>
div {
  outline: 1px solid black;
}
</style>
