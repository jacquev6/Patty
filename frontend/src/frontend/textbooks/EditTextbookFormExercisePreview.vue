<script setup lang="ts">
import { type Textbook } from '@/frontend/ApiClient'
import AdaptableExercisePreview, {
  makePreviewAbleExercise_forTextbook,
} from '@/frontend/common/AdaptableExercisePreview.vue'

type Exercise = Textbook['ranges'][number]['pages'][number]['exercises'][number]

defineProps<{
  exercise: Exercise
}>()

const emit = defineEmits<{
  (e: 'exercise-removed'): void
  (e: 'batch-updated'): void
}>()
</script>

<template>
  <AdaptableExercisePreview
    :headerLevel="5"
    :showPageAndExercise="false"
    :exercise="makePreviewAbleExercise_forTextbook(exercise, exercise.adaptation)"
    @exerciseRemoved="emit('exercise-removed')"
    @batchUpdated="emit('batch-updated')"
  />
</template>
