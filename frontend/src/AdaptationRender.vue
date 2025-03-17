<script setup lang="ts">
import type { Adaptation } from './apiClient'

defineProps<{
  adaptedExercise: Exclude<Adaptation['steps'][number]['adapted_exercise'], null>
}>()
</script>

<template>
  <p>{{ adaptedExercise.instructions }}</p>
  <p>{{ adaptedExercise.wording }}</p>
</template>
