<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script lang="ts">
import { type ExtractionBatch } from '@/frontend/ApiClient'

export type PreviewableExercise = ExtractionBatch['pages'][number]['exercises'][number]

export type Context = 'adaptation' | 'classification' | 'extraction' | 'textbook'
</script>

<script setup lang="ts">
import { useTemplateRef } from 'vue'

import AdaptableExercisePreview_LeftColumn from './AdaptableExercisePreviewLeftColumn.vue'
import AdaptableExercisePreview_RightColumn from './AdaptableExercisePreviewRightColumn.vue'
import FixedColumns from '$/FixedColumns.vue'

defineProps<{
  headerLevel: 1 | 2 | 3 | 4 | 5 | 6
  context: Context
  index: number | null
  exercise: PreviewableExercise
}>()

const emit = defineEmits<{
  (e: 'exercise-removed'): void
  (e: 'batch-updated'): void
  (e: 'submit-extractions-with-recent-settings'): void
}>()

const rightColumn = useTemplateRef('rightColumn')
</script>

<template>
  <div style="margin-top: 5px">
    <FixedColumns :columns="[1, 1]" :gutters="false">
      <template #col-1>
        <AdaptableExercisePreview_LeftColumn
          :headerLevel
          :context
          :index
          :exercise
          :rightColumn
          @exerciseRemoved="emit('exercise-removed')"
          @batchUpdated="emit('batch-updated')"
        />
      </template>
      <template #col-2>
        <AdaptableExercisePreview_RightColumn
          ref="rightColumn"
          :headerLevel
          :exercise
          :context
          @submitExtractionsWithRecentSettings="emit('submit-extractions-with-recent-settings')"
        />
      </template>
    </FixedColumns>
  </div>
</template>
