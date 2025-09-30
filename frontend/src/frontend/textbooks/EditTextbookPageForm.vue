<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'

import { useAuthenticatedClient, type TextbookPage } from '../ApiClient'
import AdaptableExercisePreview from '@/frontend/common/AdaptableExercisePreview.vue'
import BugMarker from '@/reusable/BugMarker.vue'

const props = defineProps<{
  textbookPage: TextbookPage
}>()

const emit = defineEmits<{
  (e: 'textbook-updated'): void
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()

const textbook = computed(() => props.textbookPage.textbook)

async function removeExercise(exercise_id: string, removed: boolean) {
  await client.PUT('/api/textbooks/{textbook_id}/exercises/{exercise_id}/removed', {
    params: { path: { textbook_id: textbook.value.id, exercise_id }, query: { removed } },
  })
  emit('textbook-updated')
}
</script>

<template>
  <h1>{{ t('titleAndPage', { title: textbook.title, pageNumber: textbookPage.number }) }}</h1>
  <template v-for="exercise in textbookPage.exercises">
    <h2 v-if="exercise.removedFromTextbook">
      <span class="removed">{{ t('exercise') }} {{ exercise.exerciseNumber }}</span>
      ({{ t('removed') }})
      <button @click="removeExercise(exercise.id, false)">{{ t('reAdd') }}</button>
    </h2>
    <AdaptableExercisePreview
      v-else-if="exercise.kind === 'adaptable'"
      :headerLevel="2"
      context="textbookByBatch"
      :index="null"
      :exercise
      @exerciseRemoved="() => removeExercise(exercise.id, true)"
      @batchUpdated="emit('textbook-updated')"
    />
    <template v-else-if="exercise.kind === 'external'">
      <h2>
        {{ t('exercise') }} {{ exercise.exerciseNumber }}
        <button @click="removeExercise(exercise.id, true)">{{ t('remove') }}</button>
      </h2>
      <p>{{ exercise.originalFileName }}</p>
    </template>
    <BugMarker v-else is="p" m="Unknown exercise kind" :v="exercise" />
  </template>
</template>

<i18n>
en:
  titleAndPage: '{title}, page {pageNumber}'
  exercise: Exercise
  reAdd: Re-add
  remove: Remove
  removed: removed
fr:
  titleAndPage: '{title}, page {pageNumber}'
  exercise: Exercice
  reAdd: Rajouter
  remove: Enlever
  removed: enlevé
</i18n>
