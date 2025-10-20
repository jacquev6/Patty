<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAuthenticatedClient, type Textbook, type TextbookPage } from '../ApiClient'
import AdaptableExercisePreview from '@/frontend/common/AdaptableExercisePreview.vue'
import BugMarker from '@/reusable/BugMarker.vue'
import WhiteSpace from '@/reusable/WhiteSpace.vue'
import assert from '$/assert'

const props = defineProps<{
  textbook: Textbook
  page: TextbookPage
}>()

const emit = defineEmits<{
  (e: 'textbook-updated'): void
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()
const router = useRouter()

async function removeExercise(exercise_id: string, removed: boolean) {
  await client.PUT('/api/textbooks/{textbook_id}/exercises/{exercise_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, exercise_id }, query: { removed } },
  })
  emit('textbook-updated')
}

async function removePage() {
  assert(props.page.id !== null)
  await client.PUT('/api/textbooks/{textbook_id}/pages/{page_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, page_id: props.page.id }, query: { removed: true } },
  })
  router.push({ name: 'textbook', params: { id: props.textbook.id } })
}

const previousPage = computed(() => {
  const pagesWithExercisesBefore = props.textbook.pagesWithExercises.filter((n) => n < props.page.number)
  if (pagesWithExercisesBefore.length === 0) {
    return null
  } else {
    return { number: Math.max(...pagesWithExercisesBefore) }
  }
})
const nextPage = computed(() => {
  const pagesWithExercisesAfter = props.textbook.pagesWithExercises.filter((n) => n > props.page.number)
  if (pagesWithExercisesAfter.length === 0) {
    return null
  } else {
    return { number: Math.min(...pagesWithExercisesAfter) }
  }
})

const allExercisesHaveBeenApproved = computed(
  () =>
    props.page.exercises.filter(
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
  <h1>
    {{ t('titleAndPage', { title: textbook.title, pageNumber: page.number }) }}
    <span v-if="page.needsRefresh" class="inProgress"> ({{ t('inProgress') }})</span>
    <template v-if="textbook.singlePdf !== null">
      <WhiteSpace />
      <button @click="removePage">{{ t('remove') }}</button>
    </template>
  </h1>
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
  <template v-for="exercise in page.exercises">
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
span.inProgress {
  color: grey;
  font-size: 80%;
}

label.disabled {
  color: gray;
}
</style>

<i18n>
en:
  titleAndPage: '{title}, page {pageNumber}'
  inProgress: in progress, will refresh
  noPreviousPage: 'No previous page with exercises'
  noNextPage: 'No next page with exercises'
  previousPage: 'Previous page with exercises: {number}'
  nextPage: 'Next page with exercises: {number}'
  showOnlyExercisesNotYetApproved: 'Show only exercises not yet approved'
  showAllExercises: 'Show all exercises'
  exercise: Exercise
  reAdd: Re-add
  remove: Remove
  removed: removed
fr:
  titleAndPage: '{title}, page {pageNumber}'
  inProgress: en cours, se mettra à jour
  noPreviousPage: 'Pas de page précédente avec des exercices'
  previousPage: 'Page précédente avec des exercices : {number}'
  noNextPage: 'Pas de page suivante avec des exercices'
  nextPage: 'Page suivante avec des exercices : {number}'
  showOnlyExercisesNotYetApproved: 'Afficher uniquement les exercices pas encore validés'
  showAllExercises: 'Afficher tous les exercices'
  exercise: Exercice
  reAdd: Rajouter
  remove: Enlever
  removed: enlevé
</i18n>
