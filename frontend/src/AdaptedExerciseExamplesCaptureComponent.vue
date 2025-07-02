<script setup lang="ts">
import MiniatureScreen from './MiniatureScreen.vue'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'

import type { AdaptedExercise } from '@/apiClient'

defineProps<{
  adaptedExercise: AdaptedExercise
}>()
</script>

<template>
  <MiniatureScreen :fullScreen="true">
    <AdaptedExerciseRenderer :adaptedExercise :navigateUsingArrowKeys="false" />
  </MiniatureScreen>
</template>
