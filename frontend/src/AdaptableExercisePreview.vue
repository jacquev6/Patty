<script lang="ts">
import { type PreprocessedAdaptation } from './adaptations'

export type PreviewableExercise =
  | {
      kind: 'adaptation'
      index: number
      adaptation: {
        id: string
        input: PreprocessedAdaptation['input']
        status: PreprocessedAdaptation['status']
      }
    }
  | {
      kind: 'classificationOrExtraction'
      headerText: string
      classificationWasRequested: boolean
      exercise: {
        id: string
        pageNumber: number | null
        exerciseNumber: string | null
        fullText: string
        exerciseClass: string | null
        reclassifiedBy: string | null
        exerciseClassHasSettings: boolean
      }
      adaptationWasRequested: boolean
      adaptation: {
        id: string
        status: PreprocessedAdaptation['status']
      } | null
      submitAdaptationsWithRecentSettings: () => Promise<void>
    }
  | {
      kind: 'textbook'
      adaptation: {
        id: string
        status: PreprocessedAdaptation['status']
      } | null
      exercise: {
        exerciseNumber: string
        fullText: string
        exerciseClass: string | null
        exerciseClassHasSettings: boolean
      }
    }

export function makePreviewAbleExercise_forAdaptation(
  index: number,
  adaptation: {
    id: string

    input: PreprocessedAdaptation['input']
    status: PreprocessedAdaptation['status']
  },
): PreviewableExercise {
  return {
    kind: 'adaptation',
    index,
    adaptation,
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
    status: PreprocessedAdaptation['status']
  } | null,
  submitAdaptationsWithRecentSettings: () => Promise<void>,
): PreviewableExercise {
  return {
    headerText,
    classificationWasRequested,
    kind: 'classificationOrExtraction',
    adaptationWasRequested,
    adaptation,
    exercise,
    submitAdaptationsWithRecentSettings,
  }
}

export function makePreviewAbleExercise_forTextbook(
  exercise: {
    exerciseNumber: string
    fullText: string
    exerciseClass: string | null
    exerciseClassHasSettings: boolean
  },
  adaptation: {
    id: string
    status: PreprocessedAdaptation['status']
  } | null,
): PreviewableExercise {
  return {
    kind: 'textbook',
    adaptation,
    exercise,
  }
}
</script>

<script setup lang="ts">
import { useTemplateRef } from 'vue'

import AdaptableExercisePreview_LeftColumn from './AdaptableExercisePreview_LeftColumn.vue'
import AdaptableExercisePreview_RightColumn from './AdaptableExercisePreview_RightColumn.vue'
import FixedColumns from './FixedColumns.vue'

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
        >
          <slot v-if="$slots.default"></slot>
        </AdaptableExercisePreview_LeftColumn>
      </template>
      <template #col-2>
        <AdaptableExercisePreview_RightColumn ref="rightColumn" :headerLevel :exercise />
      </template>
    </FixedColumns>
  </div>
</template>
