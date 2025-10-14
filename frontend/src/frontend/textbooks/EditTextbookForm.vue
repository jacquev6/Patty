<script setup lang="ts">
import { useI18n } from 'vue-i18n'

import { type Textbook, useAuthenticatedClient } from '@/frontend/ApiClient'
import { useAuthenticationTokenStore } from '@/frontend/basic/AuthenticationTokenStore'
import EditTextbookFormCreateExternalExerciseForm from './EditTextbookFormCreateExternalExerciseForm.vue'
import EditTextbookFormAddPdfRangeForm from './EditTextbookFormAddPdfRangeForm.vue'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import WhiteSpace from '$/WhiteSpace.vue'

const props = defineProps<{
  textbook: Textbook
}>()

const emit = defineEmits<{
  (e: 'textbook-updated'): void
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()

const authenticationTokenStore = useAuthenticationTokenStore()

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

function download() {
  window.location.href = `/api/export/textbook/${props.textbook.id}.html?token=${authenticationTokenStore.token}`
}
</script>

<template>
  <h1>
    <span>
      {{ textbook.title
      }}<template v-if="textbook.pagesCount !== null"> ({{ t('pagesCount', { count: textbook.pagesCount }) }})</template>
      <template v-if="textbook.publisher !== null">, {{ textbook.publisher }}</template>
      <template v-if="textbook.year !== null">, {{ textbook.year }}</template>
      <template v-if="textbook.isbn !== null"> ({{ t('isbn') }}: {{ textbook.isbn }})</template>
    </span>
    <WhiteSpace />
    <button @click="download">{{ t('downloadHtml') }}</button>
  </h1>
  <h2>{{ t('pagesWithExercises') }}</h2>
  <ul class="rangePages">
    <li v-for="pageNumber in textbook.pagesWithExercises">
      <RouterLink :to="{ name: 'textbook-page', params: { textbookId: textbook.id, pageNumber } }">
        {{ pageNumber }}
      </RouterLink>
    </li>
  </ul>
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
          <template #provider>{{ t('modelForExtraction') }}</template></LlmModelSelector
        >,
        <LlmModelSelector :availableLlmModels="[]" :disabled="true" :modelValue="range.modelForAdaptation">
          <template #provider>{{ t('modelForAdaptation') }}</template>
        </LlmModelSelector>
      </p>
      <p>{{ t('extractedPagesHeader') }}</p>
      <ul class="rangePages">
        <li v-for="page in range.pages">
          <span :class="{ removed: page.removedFromTextbook }">
            {{ page.pageNumber }}
            <!-- <RouterLink
              :to="{ name: 'textbook-page', params: { textbookId: textbook.id, pageNumber: page.pageNumber } }"
            >
              {{ t('viewDetails') }}
            </RouterLink> -->
          </span>
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
        </li>
      </ul>
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

<style scoped>
.removed {
  text-decoration: line-through;
}

span.inProgress {
  color: gray;
  font-size: 70%;
}

ul.rangePages {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7em;
}

ul.rangePages li {
  flex: 0 1 auto;
  white-space: nowrap;
  margin-right: 2em;
}
</style>

<i18n>
en:
  isbn: ISBN
  pagesCount: "{count} pages"
  downloadHtml: Download
  pagesWithExercises: "Pages with exercises"
  newTextbookPdf: New textbook PDF
  existingTextbookPdfs: Existing textbook PDFs
  inProgress: "(in progress, will refresh when done)"
  newExternalExercises: New external exercise(s)
  existingExternalExercises: Existing external exercises
  exercise: Exercise
  page: Page
  reAdd: Re-add
  remove: Remove
  removed: removed
  modelForExtraction: "Model provider for extraction:"
  modelForAdaptation: "for adaptation:"
  pages: "Pages {textbookFrom} to {textbookTo} (from {pdfName} pages {pdfFrom} to {pdfTo})"
  extractedPagesHeader: "Extracted pages:"
  viewDetails: "View details"
fr:
  isbn: ISBN
  pagesCount: "{count} pages"
  downloadHtml: Télécharger
  pagesWithExercises: "Pages avec des exercices"
  newTextbookPdf: Nouveau PDF de manuel
  existingTextbookPdfs: PDF de manuel existants
  inProgress: "(en cours, se mettra à jour quand terminé)"
  newExternalExercises: Nouvel exercice externe
  existingExternalExercises: Exercices externes existants
  exercise: Exercice
  page: Page
  reAdd: Rajouter
  remove: Enlever
  removed: enlevé
  modelForExtraction: "Fournisseur de modèle pour l'extraction :"
  modelForAdaptation: "pour l'adaptation :"
  pages: "Pages {textbookFrom} à {textbookTo} (de {pdfName} pages {pdfFrom} à {pdfTo})"
  extractedPagesHeader: "Pages extraites :"
  viewDetails: "Voir les détails"
</i18n>
