<script lang="ts">
import { type Adaptation as ApiAdaptation } from '@/frontend/ApiClient'

type Exercise = {
  id: string
  pageNumber: number | null
  exerciseNumber: string | null
  fullText: string
  exerciseClass: string | null
  reclassifiedBy: string | null
  exerciseClassHasSettings: boolean
}

type Adaptation = {
  id: ApiAdaptation['id']
  status: ApiAdaptation['status']
}

export type PreviewableExercise = {
  kind: 'adaptation' | 'classificationOrExtraction' | 'textbook'
  index: number | null
  headerText: string | null
  classificationWasRequested: boolean
  exercise: Exercise
  adaptationWasRequested: boolean
  adaptation: Adaptation | null
  submitAdaptationsWithRecentSettings: (() => Promise<void>) | null
}

export function makePreviewAbleExercise_forAdaptation(
  index: number,
  exercise: {
    id: string
    pageNumber: number | null
    exerciseNumber: string | null
    fullText: string
    exerciseClass: string | null
    reclassifiedBy: string | null
    exerciseClassHasSettings: boolean
  },
  adaptation: {
    id: string
    status: Adaptation['status']
  },
  headerText: string | null,
): PreviewableExercise {
  return {
    kind: 'adaptation',
    index,
    headerText,
    classificationWasRequested: false,
    exercise,
    adaptationWasRequested: true,
    adaptation,
    submitAdaptationsWithRecentSettings: null,
  }
}

export function makePreviewAbleExercise_forClassificationOrExtraction(
  headerText: string,
  classificationWasRequested: boolean,
  exercise: {
    id: string
    pageNumber: number | null
    exerciseNumber: string | null
    fullText: string
    exerciseClass: string | null
    reclassifiedBy: string | null
    exerciseClassHasSettings: boolean
  },
  adaptationWasRequested: boolean,
  adaptation: {
    id: string
    status: Adaptation['status']
  } | null,
  submitAdaptationsWithRecentSettings: () => Promise<void>,
): PreviewableExercise {
  return {
    kind: 'classificationOrExtraction',
    index: null,
    headerText,
    classificationWasRequested,
    exercise,
    adaptationWasRequested,
    adaptation,
    submitAdaptationsWithRecentSettings,
  }
}

export function makePreviewAbleExercise_forTextbook(
  exercise: {
    id: string
    pageNumber: number | null
    exerciseNumber: string | null
    fullText: string
    exerciseClass: string | null
    reclassifiedBy: string | null
    exerciseClassHasSettings: boolean
  },
  adaptation: {
    id: string
    status: Adaptation['status']
  } | null,
): PreviewableExercise {
  return {
    kind: 'textbook',
    index: null,
    headerText: null,
    classificationWasRequested: true,
    exercise,
    adaptationWasRequested: true,
    adaptation,
    submitAdaptationsWithRecentSettings: null,
  }
}
</script>

<script setup lang="ts">
import { useTemplateRef } from 'vue'

import AdaptableExercisePreview_LeftColumn from './AdaptableExercisePreviewLeftColumn.vue'
import AdaptableExercisePreview_RightColumn from './AdaptableExercisePreviewRightColumn.vue'
import FixedColumns from '$/FixedColumns.vue'

defineProps<{
  headerLevel: 1 | 2 | 3 | 4 | 5 | 6
  exercise: PreviewableExercise
  showPageAndExercise: boolean
}>()

const emit = defineEmits<{
  (e: 'exercise-removed'): void
  (e: 'batch-updated'): void
}>()

const rightColumn = useTemplateRef('rightColumn')
</script>

<template>
  <div style="margin-top: 5px">
    <FixedColumns :columns="[1, 1]" :gutters="false">
      <template #col-1>
        <AdaptableExercisePreview_LeftColumn
          :headerLevel
          :exercise
          :rightColumn
          :showPageAndExercise
          @exerciseRemoved="emit('exercise-removed')"
          @batchUpdated="emit('batch-updated')"
        />
      </template>
      <template #col-2>
        <AdaptableExercisePreview_RightColumn ref="rightColumn" :headerLevel :exercise />
      </template>
    </FixedColumns>
  </div>
</template>
