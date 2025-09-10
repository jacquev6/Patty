<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { type Textbook, useAuthenticatedClient } from '@/frontend/ApiClient'
import AdaptationPreview from '@/frontend/sandbox/EditAdaptationBatchFormAdaptationPreview.vue'
import { useAuthenticationTokenStore } from '@/frontend/basic/AuthenticationTokenStore'
import EditTextbookFormCreateExternalExerciseForm from './EditTextbookFormCreateExternalExerciseForm.vue'
import EditTextbookFormAddPdfRangeForm from './EditTextbookFormAddPdfRangeForm.vue'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import WhiteSpace from '$/WhiteSpace.vue'
import EditTextbookFormExercisePreview from './EditTextbookFormExercisePreview.vue'

const props = defineProps<{
  textbook: Textbook
  availableStrategySettings: string[]
}>()

const emit = defineEmits<{
  (e: 'textbook-updated'): void
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()

const authenticationTokenStore = useAuthenticationTokenStore()

const view = ref<'batch' | 'page'>('batch')

async function removeExercise(exercise_id: string, removed: boolean) {
  await client.PUT('/api/textbooks/{textbook_id}/exercises/{exercise_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, exercise_id }, query: { removed } },
  })
  emit('textbook-updated')
}

async function removePage(page_id: string, removed: boolean) {
  await client.PUT('/api/textbooks/{textbook_id}/pages/{page_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, page_id }, query: { removed } },
  })
  emit('textbook-updated')
}

async function removeRange(range_id: string, removed: boolean) {
  await client.PUT('/api/textbooks/{textbook_id}/ranges/{range_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, range_id }, query: { removed } },
  })
  emit('textbook-updated')
}
</script>

<template>
  <h1>
    {{ textbook.title }}<template v-if="textbook.publisher !== null">, {{ textbook.publisher }}</template
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
    <h2>{{ t('newTextbookPdf') }}</h2>
    <EditTextbookFormAddPdfRangeForm :textbookId="textbook.id" @textbookUpdated="emit('textbook-updated')" />
    <h2>{{ t('existingTextbookPdfs') }}</h2>
    <template v-for="range in textbook.ranges">
      <h3>
        <span :class="{ removed: range.removedFromTextbook }">
          {{
            t('pages', {
              textbookFrom: range.textbookFirstPageNumber,
              textbookTo: range.textbookFirstPageNumber + range.pagesCount - 1,
              pdfName: range.pdfFileNames[0],
              pdfFrom: range.pdfFirstPageNumber,
              pdfTo: range.pdfFirstPageNumber + range.pagesCount - 1,
            })
          }}
        </span>
        <template v-if="range.removedFromTextbook">
          ({{ t('removed') }})
          <button @click="removeRange(range.id, false)">{{ t('reAdd') }}</button>
        </template>
        <template v-else>
          <WhiteSpace />
          <button @click="removeRange(range.id, true)">{{ t('remove') }}</button>
        </template>
      </h3>
      <template v-if="!range.removedFromTextbook">
        <p>
          <LlmModelSelector :availableLlmModels="[]" :disabled="true" :modelValue="range.modelForExtraction">
            <template #provider>{{ t('modelForExtraction') }}</template>
          </LlmModelSelector>
        </p>
        <p>
          <LlmModelSelector :availableLlmModels="[]" :disabled="true" :modelValue="range.modelForAdaptation">
            <template #provider>{{ t('modelForAdaptation') }}</template>
          </LlmModelSelector>
        </p>
        <template v-for="page in range.pages">
          <h4>
            <span :class="{ removed: page.removedFromTextbook }">{{ t('page') }} {{ page.pageNumber }}</span>
            <template v-if="page.inProgress">
              <WhiteSpace />
              <span class="inProgress">{{ t('inProgress') }}</span>
            </template>
            <template v-else-if="page.removedFromTextbook">
              ({{ t('removed') }})
              <button @click="removePage(page.id, false)">{{ t('reAdd') }}</button>
            </template>
            <template v-else>
              <WhiteSpace />
              <button @click="removePage(page.id, true)">{{ t('remove') }}</button>
            </template>
          </h4>
          <template v-if="!page.removedFromTextbook">
            <template v-for="exercise in page.exercises">
              <h5 v-if="exercise.removedFromTextbook">
                <span class="removed">{{ t('exercise') }} {{ exercise.exerciseNumber }}</span>
                ({{ t('removed') }})
                <button @click="removeExercise(exercise.id, false)">{{ t('reAdd') }}</button>
              </h5>
              <EditTextbookFormExercisePreview
                v-else
                :exercise
                @exerciseRemoved="() => removeExercise(exercise.id, true)"
                @batchUpdated="emit('textbook-updated')"
              />
            </template>
          </template>
        </template>
      </template>
    </template>
    <h2 id="external-exercises">{{ t('newExternalExercises') }}</h2>
    <EditTextbookFormCreateExternalExerciseForm :textbookId="textbook.id" @textbookUpdated="emit('textbook-updated')" />
    <h2>{{ t('existingExternalExercises') }}</h2>
    <template v-for="externalExercise in textbook.externalExercises">
      <h3 v-if="externalExercise.removedFromTextbook">
        <span class="removed">{{ externalExercise.originalFileName }}</span> ({{ t('removed') }})
        <button @click="removeExercise(externalExercise.id, false)">{{ t('reAdd') }}</button>
      </h3>
      <h3 v-else>
        {{ externalExercise.originalFileName }}
        <button @click="removeExercise(externalExercise.id, true)">{{ t('remove') }}</button>
      </h3>
    </template>
  </template>
  <template v-else>
    <template v-for="page in textbook.pages">
      <h2>{{ t('page') }} {{ page.number }}</h2>
      <template v-for="exercise in page.exercises">
        <template v-if="exercise.kind === 'adaptable'">
          <AdaptationPreview
            :headerLevel="3"
            :index="0"
            :exercise
            :headerText="`${t('exercise')} ${exercise.exerciseNumber}`"
            :showPageAndExercise="false"
          />
        </template>
        <template v-else-if="exercise.kind === 'external'">
          <h3>{{ t('exercise') }} {{ exercise.exerciseNumber }}</h3>
          <p>{{ exercise.originalFileName }}</p>
        </template>
      </template>
    </template>
  </template>
</template>

<style scoped>
.removed {
  text-decoration: line-through;
}

span.inProgress {
  color: gray;
  font-size: 70%;
}
</style>

<i18n>
en:
  isbn: ISBN
  downloadHtml: Download standalone HTML
  viewBy: View by
  viewByBatch: PDFs and external exercises
  viewByPage: page
  viewByBatchDescription: in creation order, including errors and removed adaptations. PDFs first, external exercises
  viewByBatchDescriptionBelow: below
  viewByPageDescription: sorted by page and exercise number, including only successful not-removed adaptations. Adapted PDFs and external exercises together.
  modifiedBy: Modified by
  newTextbookPdf: New textbook PDF
  existingTextbookPdfs: Existing textbook PDFs
  inProgress: "(in progress, will refresh when done)"
  newExternalExercises: New external exercise(s)
  existingExternalExercises: Existing external exercises
  exercise: Exercise
  page: Page
  input: input
  reAdd: Re-add
  remove: Remove
  removed: removed
  modelForExtraction: "Model provider for extraction:"
  modelForAdaptation: "Model provider for adaptation:"
  pages: "Pages {textbookFrom} to {textbookTo} (from {pdfName} pages {pdfFrom} to {pdfTo})"
fr:
  isbn: ISBN
  downloadHtml: Télécharger le HTML autonome
  viewBy: Afficher par
  viewByBatch: PDFs et exercices externes
  viewByPage: page
  viewByBatchDescription: dans l'ordre de création, y compris les erreurs et les adaptations supprimées. PDFs d'abord, exercices externes
  viewByBatchDescriptionBelow: en dessous
  viewByPageDescription: trié par page et numéro d'exercice, y compris uniquement les adaptations réussies non supprimées. PDFs adaptés et exercices externes ensemble.
  modifiedBy: Modifié par
  newTextbookPdf: Nouveau PDF de manuel
  existingTextbookPdfs: PDF de manuel existants
  inProgress: "(en cours, se mettra à jour quand terminé)"
  newExternalExercises: Nouvel exercice externe
  existingExternalExercises: Exercices externes existants
  exercise: Exercice
  page: Page
  input: entrée
  reAdd: Rajouter
  remove: Enlever
  removed: enlevé
  modelForExtraction: "Fournisseur de modèle pour l'extraction :"
  modelForAdaptation: "Fournisseur de modèle pour l'adaptation :"
  pages: "Pages {textbookFrom} à {textbookTo} (de {pdfName} pages {pdfFrom} à {pdfTo})"
</i18n>
