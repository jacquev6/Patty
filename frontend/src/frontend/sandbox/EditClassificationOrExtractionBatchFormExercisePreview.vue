<script setup lang="ts">
import { match } from 'ts-pattern'

import { useAuthenticatedClient, type ClassificationBatch } from '@/frontend/ApiClient'
import AdaptableExercisePreview, {
  makePreviewAbleExercise_forClassificationOrExtraction,
} from '@/frontend/common/AdaptableExercisePreview.vue'

type BatchId = {
  kind: 'classification' | 'extraction'
  id: string
}

const props = defineProps<{
  batch: BatchId
  headerLevel: 1 | 2 | 3 | 4 | 5 | 6
  headerText: string
  showPageAndExercise: boolean
  classificationWasRequested: boolean
  adaptationWasRequested: boolean
  exercise: ClassificationBatch['exercises'][number]
}>()

const emit = defineEmits<{
  (e: 'batch-updated'): void
}>()

const client = useAuthenticatedClient()

async function submitAdaptationsWithRecentSettings() {
  await match(props.batch)
    .with({ kind: 'classification' }, () =>
      client.POST(`/api/classification-batches/{id}/submit-adaptations-with-recent-settings`, {
        params: { path: { id: props.batch.id } },
      }),
    )
    .with({ kind: 'extraction' }, () =>
      client.POST(`/api/extraction-batches/{id}/submit-adaptations-with-recent-settings`, {
        params: { path: { id: props.batch.id } },
      }),
    )
    .exhaustive()
  emit('batch-updated')
}
</script>

<template>
  <AdaptableExercisePreview
    :headerLevel
    :exercise="
      makePreviewAbleExercise_forClassificationOrExtraction(
        headerText,
        classificationWasRequested,
        exercise,
        adaptationWasRequested,
        exercise.adaptation,
        submitAdaptationsWithRecentSettings,
      )
    "
    :showPageAndExercise="showPageAndExercise"
    @batchUpdated="emit('batch-updated')"
  />
</template>
