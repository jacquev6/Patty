<script setup lang="ts">
import { type AdaptationBatch } from '@/frontend/ApiClient'
import AdaptableExercisePreview, {
  makePreviewAbleExercise_forAdaptation,
} from '@/frontend/common/AdaptableExercisePreview.vue'

defineProps<{
  headerLevel: 1 | 2 | 3 | 4 | 5 | 6
  index: number
  exercise: AdaptationBatch['exercises'][number]
  headerText: string | null
  showPageAndExercise: boolean
}>()
</script>

<template>
  <AdaptableExercisePreview
    :headerLevel
    :showPageAndExercise
    :exercise="makePreviewAbleExercise_forAdaptation(index, exercise, exercise.adaptation, headerText)"
  />
</template>
