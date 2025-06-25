<script setup lang="ts">
import type { Data } from './BatchExportRootView.vue'

defineProps<{
  data: Data
}>()
</script>

<template>
  <p v-for="exercise in data">
    <RouterLink :to="{ name: 'exercise', params: { id: exercise.exerciseId } }"
      >Exercise {{ exercise.exerciseId }}</RouterLink
    >
  </p>
</template>
