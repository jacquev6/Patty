<script setup lang="ts">
import { type Adaptation } from '@/frontend/ApiClient'
import AdaptableExercisePreview, {
  makePreviewAbleExercise_forAdaptation,
} from '@/frontend/common/AdaptableExercisePreview.vue'

defineProps<{
  headerLevel: 1 | 2 | 3 | 4 | 5 | 6
  index: number
  adaptation: Adaptation
  headerText: string | null
  showPageAndExercise: boolean
}>()
</script>

<template>
  <AdaptableExercisePreview
    :headerLevel
    :showPageAndExercise
    :exercise="makePreviewAbleExercise_forAdaptation(index, adaptation, headerText)"
  />
</template>
