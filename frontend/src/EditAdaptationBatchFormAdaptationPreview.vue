<script setup lang="ts">
import type { PreprocessedAdaptation } from './adaptations'
import AdaptableExercisePreview, { makePreviewAbleExercise_forAdaptation } from './AdaptableExercisePreview.vue'

defineProps<{
  headerLevel: 1 | 2 | 3 | 4 | 5 | 6
  index: number
  adaptation: PreprocessedAdaptation
}>()
</script>

<template>
  <AdaptableExercisePreview
    :headerLevel
    :showPageAndExercise="false"
    :exercise="makePreviewAbleExercise_forAdaptation(index, adaptation)"
  >
    <slot></slot>
  </AdaptableExercisePreview>
</template>
