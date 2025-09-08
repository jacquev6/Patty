<script setup lang="ts">
import { computed } from 'vue'

import { type Textbook } from '@/frontend/ApiClient'
import { preprocess as preprocessAdaptation } from '@/frontend/Adaptations'
import AdaptableExercisePreview, {
  makePreviewAbleExercise_forTextbook,
} from '@/frontend/common/AdaptableExercisePreview.vue'

type Exercise = Textbook['ranges'][number]['pages'][number]['exercises'][number]

const props = defineProps<{
  exercise: Exercise
}>()

const emit = defineEmits<{
  (e: 'exercise-removed'): void
  (e: 'batch-updated'): void
}>()

const adaptation = computed(() => {
  if (props.exercise.adaptation === null) {
    return null
  } else {
    return preprocessAdaptation(props.exercise.adaptation)
  }
})
</script>

<template>
  <AdaptableExercisePreview
    :headerLevel="5"
    :showPageAndExercise="false"
    :exercise="makePreviewAbleExercise_forTextbook(exercise, adaptation)"
    @exerciseRemoved="emit('exercise-removed')"
    @batchUpdated="emit('batch-updated')"
  />
</template>
