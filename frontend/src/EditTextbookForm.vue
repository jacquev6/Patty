<script setup lang="ts">
import { computed, ref } from 'vue'
import _ from 'lodash'
import { useI18n } from 'vue-i18n'

import { type Textbook, useAuthenticatedClient } from './apiClient'
import AdaptationPreview from './EditAdaptationBatchFormAdaptationPreview.vue'
import { preprocess as preprocessAdaptation, type PreprocessedAdaptation } from './adaptations'
import EditTextbookFormCreateAdaptationBatchForm from './EditTextbookFormCreateAdaptationBatchForm.vue'
import assert from './assert'
import { useAuthenticationTokenStore } from './AuthenticationTokenStore'
import EditTextbookFormCreateExternalExerciseForm from './EditTextbookFormCreateExternalExerciseForm.vue'

const props = defineProps<{
  textbook: Textbook
  availableStrategySettings: string[]
}>()

const emit = defineEmits<{
  (e: 'textbook-updated', textbook: Textbook): void
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()

const authenticationTokenStore = useAuthenticationTokenStore()

const view = ref<'batch' | 'page'>('batch')

const adaptationBatches = computed(() =>
  props.textbook.adaptationBatches.map((adaptationBatch) => {
    return {
      ...adaptationBatch,
      adaptations: adaptationBatch.adaptations.map(preprocessAdaptation),
    }
  }),
)

const pages = computed(() => {
  type Exercise =
    | {
        kind: 'adaptation'
        adaptation: PreprocessedAdaptation
      }
    | {
        kind: 'externalExercise'
        externalExercise: {
          pageNumber: number | null
          exerciseNumber: string | null
          originalFileName: string
        }
      }

  const pages: Record<number, Exercise[]> = {}
  for (const adaptationBatch of adaptationBatches.value) {
    if (!adaptationBatch.removedFromTextbook) {
      for (const adaptation of adaptationBatch.adaptations) {
        if (
          !adaptation.removedFromTextbook &&
          adaptation.input.pageNumber !== null &&
          adaptation.status.kind === 'success'
        ) {
          pages[adaptation.input.pageNumber] ??= []
          pages[adaptation.input.pageNumber].push({ kind: 'adaptation', adaptation })
        }
      }
    }
  }
  for (const externalExercise of props.textbook.externalExercises) {
    if (!externalExercise.removedFromTextbook && externalExercise.pageNumber !== null) {
      pages[externalExercise.pageNumber] ??= []
      pages[externalExercise.pageNumber].push({
        kind: 'externalExercise',
        externalExercise,
      })
    }
  }

  for (const pageNumber in pages) {
    pages[pageNumber] = _.sortBy(pages[pageNumber], [
      (exercise) => {
        const exerciseNumber =
          exercise.kind === 'adaptation'
            ? exercise.adaptation.input.exerciseNumber
            : exercise.externalExercise.exerciseNumber
        if (exerciseNumber === null) {
          return 0
        } else {
          const asNumber = parseInt(exerciseNumber)
          if (isNaN(asNumber)) {
            return 0
          } else {
            return asNumber
          }
        }
      },
      'input.exerciseNumber',
    ])
  }

  return pages
})

function textbookUpdated(textbook: Textbook) {
  emit('textbook-updated', textbook)
}

async function removeAdaptationBatch(id: string, removed: boolean) {
  const response = await client.PUT('/api/textbooks/{textbook_id}/adaptation-batches/{adaptation_batch_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, adaptation_batch_id: id }, query: { removed } },
  })
  assert(response.data !== undefined)
  emit('textbook-updated', response.data)
}

async function removeAdaptation(id: string, removed: boolean) {
  const response = await client.PUT('/api/textbooks/{textbook_id}/adaptations/{adaptation_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, adaptation_id: id }, query: { removed } },
  })
  assert(response.data !== undefined)
  emit('textbook-updated', response.data)
}

async function removeExternalExercise(id: string, removed: boolean) {
  const response = await client.PUT('/api/textbooks/{textbook_id}/external-exercises/{external_exercise_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, external_exercise_id: id }, query: { removed } },
  })
  assert(response.data !== undefined)
  emit('textbook-updated', response.data)
}
</script>

<template>
  <h1>
    {{ textbook.title }}<template v-if="textbook.editor !== null">, {{ textbook.editor }}</template
    ><template v-if="textbook.year !== null">, {{ textbook.year }}</template>
    <template v-if="textbook.isbn !== null"> ({{ t('isbn') }}: {{ textbook.isbn }})</template>
  </h1>
  <p>
    <a :href="`/api/export/textbook/${textbook.id}.html?token=${authenticationTokenStore.token}`">
      {{ t('downloadHtml') }}
    </a>
  </p>
  <p>
    {{ t('viewBy') }}
    <select data-cy="view-by" v-model="view">
      <option value="batch">{{ t('viewByBatch') }}</option>
      <option value="page">{{ t('viewByPage') }}</option></select
    >:
    <template v-if="view === 'batch'">
      {{ t('viewByBatchDescription') }}
      <a href="#external-exercises">{{ t('viewByBatchDescriptionBelow') }}</a
      >.
    </template>
    <template v-else>
      {{ t('viewByPageDescription') }}
    </template>
  </p>
  <template v-if="view === 'batch'">
    <h2>{{ t('newBatch') }}</h2>
    <EditTextbookFormCreateAdaptationBatchForm
      :availableStrategySettings
      :textbookId="textbook.id"
      @textbookUpdated="textbookUpdated"
    />
    <h2>{{ t('existingBatches') }}</h2>
    <template v-for="adaptationBatch in adaptationBatches">
      <template v-if="adaptationBatch.removedFromTextbook">
        <h3>
          <span class="removed">{{ adaptationBatch.strategy.settings.name }}</span> ({{ t('removed') }})
          <button @click="removeAdaptationBatch(adaptationBatch.id, false)">{{ t('reAdd') }}</button>
        </h3>
      </template>
      <template v-else>
        <h3>
          {{ adaptationBatch.strategy.settings.name }}
          <button @click="removeAdaptationBatch(adaptationBatch.id, true)">{{ t('remove') }}</button>
        </h3>
        <template v-for="(adaptation, index) in adaptationBatch.adaptations">
          <template v-if="adaptation.removedFromTextbook">
            <h4 style="margin-top: 0">
              <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
              <span class="removed">P{{ adaptation.input.pageNumber }}Ex{{ adaptation.input.exerciseNumber }}</span>
              ({{ t('input') }} {{ index + 1 }}, {{ t('removed') }})
              <button @click="removeAdaptation(adaptation.id, false)">{{ t('reAdd') }}</button>
            </h4>
          </template>
          <AdaptationPreview v-else header="h4" :index :adaptation>
            <h4 style="margin-top: 0">
              <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
              <span>P{{ adaptation.input.pageNumber }}Ex{{ adaptation.input.exerciseNumber }}</span>
              ({{ t('input') }} {{ index + 1 }})
              <button @click="removeAdaptation(adaptation.id, true)">{{ t('remove') }}</button>
            </h4>
          </AdaptationPreview>
        </template>
      </template>
    </template>
    <h2 id="external-exercises">{{ t('newExternalExercises') }}</h2>
    <EditTextbookFormCreateExternalExerciseForm :textbookId="textbook.id" @textbookUpdated="textbookUpdated" />
    <h2>{{ t('existingExternalExercises') }}</h2>
    <template v-for="externalExercise in textbook.externalExercises">
      <h3 v-if="externalExercise.removedFromTextbook">
        <span class="removed">{{ externalExercise.originalFileName }}</span> ({{ t('removed') }})
        <button @click="removeExternalExercise(externalExercise.id, false)">{{ t('reAdd') }}</button>
      </h3>
      <h3 v-else>
        {{ externalExercise.originalFileName }}
        <button @click="removeExternalExercise(externalExercise.id, true)">{{ t('remove') }}</button>
      </h3>
    </template>
  </template>
  <template v-else>
    <template v-for="(adaptations, pageNumber) in pages">
      <h2>{{ t('page') }} {{ pageNumber }}</h2>
      <template v-for="exercise in adaptations">
        <template v-if="exercise.kind === 'adaptation'">
          <AdaptationPreview header="h3" :index="0" :adaptation="exercise.adaptation">
            <h3 style="margin-top: 0">{{ t('exercise') }} {{ exercise.adaptation.input.exerciseNumber }}</h3>
          </AdaptationPreview>
        </template>
        <template v-else-if="exercise.kind === 'externalExercise'">
          <h3>{{ t('exercise') }} {{ exercise.externalExercise.exerciseNumber }}</h3>
          <p>{{ exercise.externalExercise.originalFileName }}</p>
        </template>
      </template>
    </template>
  </template>
</template>

<style scoped>
.removed {
  text-decoration: line-through;
}
</style>

<i18n>
en:
  isbn: ISBN
  downloadHtml: Download standalone HTML
  viewBy: View by
  viewByBatch: batch and external exercises
  viewByPage: page
  viewByBatchDescription: in creation order, including errors and removed adaptations. Batches first, external exercises
  viewByBatchDescriptionBelow: below
  viewByPageDescription: sorted by page and exercise number, including only successful not-removed adaptations. Batches and external exercises together.
  newBatch: New batch
  existingBatches: Existing batches
  newExternalExercises: New external exercise(s)
  existingExternalExercises: Existing external exercises
  exercise: Exercise
  page: Page
  input: input
  reAdd: Re-add
  remove: Remove
  removed: removed
fr:
  isbn: ISBN
  downloadHtml: Télécharger le HTML autonome
  viewBy: Afficher par
  viewByBatch: batch et exercices externes
  viewByPage: page
  viewByBatchDescription: dans l'ordre de création, y compris les erreurs et les adaptations supprimées. Batchs d'abord, exercices externes
  viewByBatchDescriptionBelow: en dessous
  viewByPageDescription: trié par page et numéro d'exercice, y compris uniquement les adaptations réussies non supprimées. Batchs et exercices externes ensemble.
  newBatch: Nouveau batch
  existingBatches: Batchs existants
  newExternalExercises: Nouvel exercice externe
  existingExternalExercises: Exercices externes existants
  exercise: Exercice
  page: Page
  input: entrée
  reAdd: Rajouter
  remove: Enlever
  removed: enlevé
</i18n>
