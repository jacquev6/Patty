<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { computed, ref } from 'vue'

import { type Textbook, useAuthenticatedClient } from '@/frontend/ApiClient'
import { useAuthenticationTokenStore } from '@/frontend/basic/AuthenticationTokenStore'
import EditTextbookFormCreateExternalExerciseForm from './EditTextbookFormCreateExternalExerciseForm.vue'
import EditTextbookFormCreateLessonForm from './EditTextbookFormCreateLessonForm.vue'
import EditTextbookFormAddPdfRangeForm from './EditTextbookFormAddPdfRangeForm.vue'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import WhiteSpace from '$/WhiteSpace.vue'
import InputForNumberOrNull from '@/reusable/InputForNumberOrNull.vue'

const props = defineProps<{
  textbook: Textbook
}>()

const emit = defineEmits<{
  (e: 'textbook-updated'): void
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()
const router = useRouter()

const authenticationTokenStore = useAuthenticationTokenStore()

async function removeExercise(exercise_id: string, removed: boolean) {
  await client.PUT('/api/textbooks/{textbook_id}/exercises/{exercise_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, exercise_id }, query: { removed } },
  })
  emit('textbook-updated')
}

async function removeLesson(lesson_id: string, removed: boolean) {
  await client.PUT('/api/textbooks/{textbook_id}/lessons/{lesson_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, lesson_id }, query: { removed } },
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

const retryablePages = computed(
  () =>
    props.textbook.ranges
      .filter(({ markedAsRemoved }) => !markedAsRemoved)
      .flatMap(({ pages }) => pages)
      .filter(({ markedAsRemoved }) => !markedAsRemoved)
      .filter(({ status }) => status.kind === 'error') as ((typeof props.textbook.ranges)[0]['pages'][0] & {
      status: { kind: 'error' }
    })[],
)

const pageForMissingExercises = ref<number | null>(null)
</script>

<template>
  <h1>
    <span>
      {{ textbook.title
      }}<template v-if="textbook.pagesCount !== null">
        ({{ t('pagesCount', { count: textbook.pagesCount }) }})</template
      >
      <template v-if="textbook.publisher !== null">, {{ textbook.publisher }}</template>
      <template v-if="textbook.year !== null">, {{ textbook.year }}</template>
      <template v-if="textbook.isbn !== null"> ({{ t('isbn') }}: {{ textbook.isbn }})</template>
    </span>
    <WhiteSpace />
    <button @click="download">{{ t('downloadHtml') }}</button>
  </h1>
  <p>
    <I18nT keypath="download">
      <a :href="`/api/export/textbook/${textbook.id}-adapted-exercises.zip?token=${authenticationTokenStore.token}`">
        {{ t('zipDataForAdaptedExercises') }}
      </a>
    </I18nT>
  </p>
  <h2>
    {{ t('pagesWithExercises')
    }}<template v-if="textbook.needsRefresh">
      <span class="inProgress">{{ t('inProgress') }}</span></template
    >
  </h2>
  <ul class="rangePages">
    <li v-for="pageNumber in textbook.pagesWithExercises">
      <RouterLink :to="{ name: 'textbook-page', params: { textbookId: textbook.id, pageNumber } }">
        {{ pageNumber }}
      </RouterLink>
    </li>
  </ul>
  <template v-if="retryablePages.length !== 0">
    <h2>{{ t('pagesWithErrors') }}</h2>
    <p>{{ t('instructionsForPagesWithErrors') }}</p>
    <ul class="rangePages">
      <li v-for="page in retryablePages">
        {{ page.pageNumber }}
        <WhiteSpace />
        <span class="error">
          <template v-if="page.status.error === 'invalid-json'">{{ t('invalidJson') }}</template>
          <template v-else-if="page.status.error === 'not-json'">{{ t('notJson') }}</template>
          <template v-else-if="page.status.error === 'unknown'">{{ t('unknownError') }}</template>
        </span>
        <WhiteSpace />
        <button @click="removePage(page.id, true)">{{ t('remove') }}</button>
      </li>
    </ul>
  </template>
  <h2>{{ t('addMissingExercises') }}</h2>
  <p>
    <label>
      {{ t('addMissingExercisesOnPage') }} <InputForNumberOrNull type="number" v-model="pageForMissingExercises" />:
      <button
        :disabled="pageForMissingExercises === null"
        @click="
          router.push({
            name: 'add-manual-exercises',
            params: { textbookId: textbook.id, pageNumber: pageForMissingExercises },
          })
        "
      >
        {{ t('addMissingExercisesGo') }}
      </button>
    </label>
  </p>
  <h2 v-if="textbook.singlePdf === null">{{ t('newTextbookPdf') }}</h2>
  <h2 v-else>{{ t('importNewPages') }}</h2>
  <EditTextbookFormAddPdfRangeForm :textbook />
  <template v-if="textbook.singlePdf === null">
    <h2>{{ t('existingTextbookPdfs') }}</h2>
    <template v-for="range in textbook.ranges">
      <h3>
        <span :class="{ removed: range.markedAsRemoved }">
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
        <template v-if="range.markedAsRemoved">
          ({{ t('removed') }})
          <button @click="removeRange(range.id, false)">{{ t('reAdd') }}</button>
        </template>
        <template v-else>
          <WhiteSpace />
          <button @click="removeRange(range.id, true)">{{ t('remove') }}</button>
        </template>
      </h3>
      <template v-if="!range.markedAsRemoved">
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
            <span :class="{ removed: page.markedAsRemoved }">
              {{ page.pageNumber }}
              <!-- <RouterLink
                :to="{ name: 'textbook-page', params: { textbookId: textbook.id, pageNumber: page.pageNumber } }"
              >
                {{ t('viewDetails') }}
              </RouterLink> -->
            </span>
            <template v-if="page.status.kind === 'in-progress'">
              <WhiteSpace />
              <span class="inProgress">{{ t('inProgress') }}</span>
            </template>
            <template v-else-if="page.markedAsRemoved">
              ({{ t('removed') }})
              <button @click="removePage(page.id, false)">{{ t('reAdd') }}</button>
            </template>
            <template v-else>
              <template v-if="page.status.kind === 'error'">
                <WhiteSpace />
                <span class="error">
                  <template v-if="page.status.error === 'invalid-json'">{{ t('invalidJson') }}</template>
                  <template v-else-if="page.status.error === 'not-json'">{{ t('notJson') }}</template>
                  <template v-else-if="page.status.error === 'unknown'">{{ t('unknownError') }}</template>
                </span>
              </template>
              <WhiteSpace />
              <button @click="removePage(page.id, true)">{{ t('remove') }}</button>
            </template>
          </li>
        </ul>
      </template>
    </template>
  </template>
  <h2 id="external-exercises">{{ t('newExternalExercises') }}</h2>
  <EditTextbookFormCreateExternalExerciseForm :textbookId="textbook.id" @textbookUpdated="emit('textbook-updated')" />
  <h2>{{ t('existingExternalExercises') }}</h2>
  <template v-for="externalExercise in textbook.externalExercises">
    <h3 v-if="externalExercise.markedAsRemoved">
      <span class="removed">{{ externalExercise.originalFileName }}</span> ({{ t('removed') }})
      <button @click="removeExercise(externalExercise.id, false)">{{ t('reAdd') }}</button>
    </h3>
    <h3 v-else>
      {{ externalExercise.originalFileName }}
      <button @click="removeExercise(externalExercise.id, true)">{{ t('remove') }}</button>
    </h3>
  </template>
  <h2>{{ t('newLessons') }}</h2>
  <EditTextbookFormCreateLessonForm :textbookId="textbook.id" @textbookUpdated="emit('textbook-updated')" />
  <h2>{{ t('existingLessons') }}</h2>
  <template v-for="lesson in textbook.lessons">
    <h3 v-if="lesson.markedAsRemoved">
      <span class="removed">{{ lesson.originalFileName }}</span> ({{ t('removed') }})
      <button @click="removeLesson(lesson.id, false)">{{ t('reAdd') }}</button>
    </h3>
    <h3 v-else>
      {{ lesson.originalFileName }}
      <button @click="removeLesson(lesson.id, true)">{{ t('remove') }}</button>
    </h3>
  </template>
</template>

<style scoped>
.removed {
  text-decoration: line-through;
}

span.error {
  font-weight: bold;
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
  download: Download {0}
  zipDataForAdaptedExercises: JSON/ZIP data for adapted exercises
  pagesWithExercises: "Pages with exercises"
  pagesWithErrors: "Pages with extraction errors"
  instructionsForPagesWithErrors: You can try removing these pages then start the extraction again.
  importNewPages: Import new pages (PDF)
  addMissingExercises: Add missing exercises
  addMissingExercisesOnPage: "Add missing exercises on page"
  addMissingExercisesGo: Go
  newTextbookPdf: New textbook PDF
  existingTextbookPdfs: Existing textbook PDFs
  inProgress: "(in progress, will refresh when done)"
  invalidJson: Invalid JSON
  notJson: Not JSON
  unknownError: Unknown error
  newExternalExercises: New external exercise(s)
  existingExternalExercises: Existing external exercises
  newLessons: New lesson(s)
  existingLessons: Existing lessons
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
  download: Télécharger {0}
  zipDataForAdaptedExercises: les données JSON/ZIP des exercices adaptés
  pagesWithExercises: "Pages avec des exercices"
  pagesWithErrors: "Pages avec des erreurs d'extraction"
  instructionsForPagesWithErrors: "Vous pouvez essayer d'enlever ces pages puis d'en recommencer l'extraction."
  importNewPages: Importer de nouvelles pages (PDF)
  addMissingExercises: Ajouter des exercices manquants
  addMissingExercisesOnPage: "Ajouter des exercices manquants sur la page"
  addMissingExercisesGo: Valider
  newTextbookPdf: Nouveau PDF de manuel
  existingTextbookPdfs: PDF de manuel existants
  inProgress: "(en cours, se mettra à jour quand terminé)"
  invalidJson: JSON invalide
  notJson: Pas du JSON
  unknownError: Erreur inconnue
  newExternalExercises: Nouvel exercice externe
  existingExternalExercises: Exercices externes existants
  newLessons: Nouvelle leçon
  existingLessons: Leçons existantes
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
