<script setup lang="ts">
import { type Textbook } from '@/apiClient'
import { computed } from 'vue'

import { preprocess as preprocessAdaptation } from '@/adaptations'
import AdaptableExercisePreview, { makePreviewAbleExercise_forTextbook } from '@/AdaptableExercisePreview.vue'

type Exercise = Textbook['ranges'][number]['pages'][number]['exercises'][number]

const props = defineProps<{
  exercise: Exercise
}>()

const emit = defineEmits<{
  (e: 'exercise-removed'): void
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
  />
</template>
