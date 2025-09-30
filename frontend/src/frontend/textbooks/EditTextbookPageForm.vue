<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

import { useAuthenticatedClient, type Textbook } from '../ApiClient'
import AdaptableExercisePreview from '@/frontend/common/AdaptableExercisePreview.vue'

const props = defineProps<{
  textbook: Textbook
  pageNumber: number
}>()

const emit = defineEmits<{
  (e: 'textbook-updated'): void
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()

async function removeExercise(exercise_id: string, removed: boolean) {
  await client.PUT('/api/textbooks/{textbook_id}/exercises/{exercise_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, exercise_id }, query: { removed } },
  })
  emit('textbook-updated')
}

const page = computed(() => {
  for (const range of props.textbook.ranges) {
    for (const p of range.pages) {
      if (p.pageNumber === props.pageNumber) {
        return p
      }
    }
  }
  return null
})
</script>

<template>
  <template v-if="page !== null && !page.removedFromTextbook">
    <template v-for="exercise in page.exercises">
      <h5 v-if="exercise.removedFromTextbook">
        <span class="removed">{{ t('exercise') }} {{ exercise.exerciseNumber }}</span>
        ({{ t('removed') }})
        <button @click="removeExercise(exercise.id, false)">{{ t('reAdd') }}</button>
      </h5>
      <AdaptableExercisePreview
        v-else
        :headerLevel="5"
        context="textbookByBatch"
        :index="null"
        :exercise
        @exerciseRemoved="() => removeExercise(exercise.id, true)"
        @batchUpdated="emit('textbook-updated')"
      />
    </template>
  </template>
</template>

<i18n>
en:
  exercise: Exercise
  reAdd: Re-add
  removed: removed
fr:
  exercise: Exercice
  reAdd: Rajouter
  removed: enlevé
</i18n>
