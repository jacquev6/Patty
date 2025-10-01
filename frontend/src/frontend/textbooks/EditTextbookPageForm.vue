<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'

import { useAuthenticatedClient, type TextbookPage } from '../ApiClient'
import AdaptableExercisePreview from '@/frontend/common/AdaptableExercisePreview.vue'
import BugMarker from '@/reusable/BugMarker.vue'
import WhiteSpace from '@/reusable/WhiteSpace.vue'

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

const previousPage = computed(() => (props.textbookPage.number <= 1 ? null : { number: props.textbookPage.number - 1 }))
const nextPage = computed(() =>
  textbook.value.pagesCount !== null && props.textbookPage.number >= textbook.value.pagesCount
    ? null
    : { number: props.textbookPage.number + 1 },
)

const allExercisesHaveBeenApproved = computed(
  () =>
    props.textbookPage.exercises.filter(
      (e) => e.kind === 'adaptable' && e.adaptationStatus.kind === 'success' && e.adaptationStatus.approved === null,
    ).length === 0,
)

const exercisesToShowRequestedByUser = ref<'notApproved' | 'all'>('all')

const exercisesToShow = computed({
  get: () => (allExercisesHaveBeenApproved.value ? 'all' : exercisesToShowRequestedByUser.value),
  set: (v) => {
    exercisesToShowRequestedByUser.value = v
  },
})
</script>

<template>
  <h1>{{ t('titleAndPage', { title: textbook.title, pageNumber: textbookPage.number }) }}</h1>
  <p>
    <span v-if="!previousPage">{{ t('noPreviousPage') }}</span>
    <RouterLink
      v-else
      :to="{ name: 'textbook-page', params: { textbookId: textbook.id, pageNumber: previousPage.number } }"
    >
      {{ t('previousPage', { number: previousPage.number }) }}
    </RouterLink>
    -
    <span v-if="!nextPage">{{ t('noNextPage') }}</span>
    <RouterLink
      v-else
      :to="{ name: 'textbook-page', params: { textbookId: textbook.id, pageNumber: nextPage.number } }"
    >
      {{ t('nextPage', { number: nextPage.number }) }}
    </RouterLink>
  </p>
  <p>
    <label :class="{ disabled: allExercisesHaveBeenApproved }">
      {{ t('showOnlyExercisesNotYetApproved') }}
      <input
        type="radio"
        name="showAllExercises"
        v-model="exercisesToShow"
        value="notApproved"
        :disabled="allExercisesHaveBeenApproved"
      />
    </label>
    <WhiteSpace />
    <label>
      <input type="radio" name="showAllExercises" v-model="exercisesToShow" value="all" />
      {{ t('showAllExercises') }}
    </label>
  </p>
  <template v-for="exercise in textbookPage.exercises">
    <template
      v-if="
        exercisesToShow === 'all' ||
        exercise.kind === 'external' ||
        exercise.adaptationStatus.kind !== 'success' ||
        exercise.adaptationStatus.approved === null
      "
    >
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
</template>

<style scoped>
label.disabled {
  color: gray;
}
</style>

<i18n>
en:
  titleAndPage: '{title}, page {pageNumber}'
  noPreviousPage: 'No previous page'
  noNextPage: 'No next page'
  previousPage: 'Previous page: {number}'
  nextPage: 'Next page: {number}'
  showOnlyExercisesNotYetApproved: 'Show only exercises not yet approved'
  showAllExercises: 'Show all exercises'
  exercise: Exercise
  reAdd: Re-add
  remove: Remove
  removed: removed
fr:
  titleAndPage: '{title}, page {pageNumber}'
  noPreviousPage: 'Pas de page précédente'
  previousPage: 'Page précédente : {number}'
  noNextPage: 'Pas de page suivante'
  nextPage: 'Page suivante : {number}'
  showOnlyExercisesNotYetApproved: 'Afficher uniquement les exercices pas encore validés'
  showAllExercises: 'Afficher tous les exercices'
  exercise: Exercice
  reAdd: Rajouter
  remove: Enlever
  removed: enlevé
</i18n>
