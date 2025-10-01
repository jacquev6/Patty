<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import {
  type ExtractionBatches,
  type ClassificationBatches,
  type AdaptationBatches,
  type Textbooks,
  useAuthenticatedClient,
} from './ApiClient'
import assert from '$/assert'
import WhiteSpace from '$/WhiteSpace.vue'
import FixedColumns from '$/FixedColumns.vue'
import CreateTextbookForm from './textbooks/CreateTextbookForm.vue'
import { makeAdaptationSettingsName } from '@/frontend/common/AdaptationStrategyEditor.vue'

const client = useAuthenticatedClient()
const { t } = useI18n()
const { d } = useI18n({ useScope: 'global' })

const extractionBatches = reactive<ExtractionBatches['extractionBatches']>([])
const nextExtractionBatchesChunkId = ref<string | null>(null)
const classificationBatches = reactive<ClassificationBatches['classificationBatches']>([])
const nextClassificationBatchesChunkId = ref<string | null>(null)
const adaptationBatches = reactive<AdaptationBatches['adaptationBatches']>([])
const nextAdaptationBatchesChunkId = ref<string | null>(null)
const textbooks = reactive<Textbooks['textbooks']>([])

onMounted(async () => {
  const extractionBatchesPromise = client.GET('/api/extraction-batches')
  const classificationBatchesPromise = client.GET('/api/classification-batches')
  const adaptationBatchesPromise = client.GET('/api/adaptation-batches')
  const textbooksPromise = client.GET('/api/textbooks')

  const extractionBatchesResponse = await extractionBatchesPromise
  assert(extractionBatchesResponse.data !== undefined)
  extractionBatches.splice(0, extractionBatches.length, ...extractionBatchesResponse.data.extractionBatches)
  nextExtractionBatchesChunkId.value = extractionBatchesResponse.data.nextChunkId

  const classificationBatchesResponse = await classificationBatchesPromise
  assert(classificationBatchesResponse.data !== undefined)
  classificationBatches.splice(
    0,
    classificationBatches.length,
    ...classificationBatchesResponse.data.classificationBatches,
  )
  nextClassificationBatchesChunkId.value = classificationBatchesResponse.data.nextChunkId

  const adaptationBatchesResponse = await adaptationBatchesPromise
  assert(adaptationBatchesResponse.data !== undefined)
  adaptationBatches.splice(0, adaptationBatches.length, ...adaptationBatchesResponse.data.adaptationBatches)
  nextAdaptationBatchesChunkId.value = adaptationBatchesResponse.data.nextChunkId

  const textbooksResponse = await textbooksPromise
  assert(textbooksResponse.data !== undefined)
  textbooks.splice(0, textbooks.length, ...textbooksResponse.data.textbooks)
})

async function loadNextExtractionBatchesChunk() {
  assert(nextExtractionBatchesChunkId.value !== null)
  const response = await client.GET('/api/extraction-batches', {
    params: { query: { chunkId: nextExtractionBatchesChunkId.value } },
  })
  assert(response.data !== undefined)
  extractionBatches.push(...response.data.extractionBatches)
  nextExtractionBatchesChunkId.value = response.data.nextChunkId
}

async function loadNextClassificationBatchesChunk() {
  assert(nextClassificationBatchesChunkId.value !== null)
  const response = await client.GET('/api/classification-batches', {
    params: { query: { chunkId: nextClassificationBatchesChunkId.value } },
  })
  assert(response.data !== undefined)
  classificationBatches.push(...response.data.classificationBatches)
  nextClassificationBatchesChunkId.value = response.data.nextChunkId
}

async function loadNextAdaptationBatchesChunk() {
  assert(nextAdaptationBatchesChunkId.value !== null)
  const response = await client.GET('/api/adaptation-batches', {
    params: { query: { chunkId: nextAdaptationBatchesChunkId.value } },
  })
  assert(response.data !== undefined)
  adaptationBatches.push(...response.data.adaptationBatches)
  nextAdaptationBatchesChunkId.value = response.data.nextChunkId
}

function textbookSummary(textbook: Textbooks['textbooks'][number]) {
  return [
    textbook.title + (textbook.pagesCount ? ` (${textbook.pagesCount} pages)` : ''),
    textbook.publisher,
    textbook.year ? textbook.year.toString() : null,
  ]
    .filter((part) => part !== null && part !== undefined)
    .join(', ')
}
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <FixedColumns :columns="[1, 1]">
      <template #col-1>
        <h1>{{ t('sandbox') }}</h1>
        <p>
          <RouterLink :to="{ name: 'adapted-exercice-examples' }">{{ t('adaptedExerciseExamples') }}</RouterLink>
        </p>
        <h2>{{ t('newBatch') }}</h2>
        <p>
          <RouterLink :to="{ name: 'create-extraction-batch' }">{{ t('newExtractionBatch.link') }}</RouterLink> ({{
            t('newExtractionBatch.comment')
          }})
        </p>
        <p>
          <RouterLink :to="{ name: 'create-classification-batch' }">{{ t('newClassificationBatch.link') }}</RouterLink>
          ({{ t('newClassificationBatch.comment') }})
        </p>
        <p>
          <RouterLink :to="{ name: 'create-adaptation-batch' }">{{ t('newAdaptationBatch.link') }}</RouterLink> ({{
            t('newAdaptationBatch.comment')
          }})
        </p>

        <h2>{{ t('existingExtractionBatches') }}</h2>
        <ul>
          <li v-for="extractionBatch in extractionBatches">
            <RouterLink :to="{ name: 'extraction-batch', params: { id: extractionBatch.id } }">
              {{ t('extractionBatch', [extractionBatch.id]) }}
            </RouterLink>
            ({{
              t('createdBy', { name: extractionBatch.createdBy, date: d(new Date(extractionBatch.createdAt), 'long') })
            }})
          </li>
          <li>
            <button :disabled="nextExtractionBatchesChunkId === null" @click="loadNextExtractionBatchesChunk">
              {{ t('loadMore') }}
            </button>
          </li>
        </ul>

        <h2>{{ t('existingClassificationBatches') }}</h2>
        <ul>
          <li v-for="classificationBatch in classificationBatches">
            <RouterLink :to="{ name: 'classification-batch', params: { id: classificationBatch.id } }">
              {{ t('classificationBatch', [classificationBatch.id]) }}
            </RouterLink>
            ({{
              t('createdBy', {
                name: classificationBatch.createdBy,
                date: d(new Date(classificationBatch.createdAt), 'long'),
              })
            }})
          </li>
          <li>
            <button :disabled="nextClassificationBatchesChunkId === null" @click="loadNextClassificationBatchesChunk">
              {{ t('loadMore') }}
            </button>
          </li>
        </ul>

        <h2>{{ t('existingAdaptationBatches') }}</h2>
        <ul>
          <li v-for="adaptationBatch in adaptationBatches">
            <RouterLink :to="{ name: 'adaptation-batch', params: { id: adaptationBatch.id } }">
              {{ t('adaptationBatch', [adaptationBatch.id]) }}
            </RouterLink>
            (<template v-if="adaptationBatch.strategySettingsIdentity !== null"
              >{{ makeAdaptationSettingsName(adaptationBatch.strategySettingsIdentity) }},<WhiteSpace /></template
            >{{ adaptationBatch.model.provider }}/{{ adaptationBatch.model.name }},
            {{
              t('createdBy', { name: adaptationBatch.createdBy, date: d(new Date(adaptationBatch.createdAt), 'long') })
            }})
          </li>
          <li>
            <button :disabled="nextAdaptationBatchesChunkId === null" @click="loadNextAdaptationBatchesChunk">
              {{ t('loadMore') }}
            </button>
          </li>
        </ul>
      </template>
      <template #col-2>
        <h1>{{ t('textbooks') }}</h1>
        <h2>{{ t('newTextbook') }}</h2>
        <CreateTextbookForm />
        <h2>{{ t('existingTextbooks') }}</h2>
        <ul>
          <li v-for="textbook in textbooks">
            <RouterLink :to="{ name: 'textbook', params: { id: textbook.id } }">{{
              textbookSummary(textbook)
            }}</RouterLink>
            ({{ t('createdBy', { name: textbook.createdBy, date: d(new Date(textbook.createdAt), 'long') }) }})
          </li>
        </ul>
      </template>
    </FixedColumns>
  </div>
</template>

<i18n>
en:
  sandbox: Sandbox
  adaptedExerciseExamples: Adapted exercise examples, with their JSON code.
  newBatch: New batch
  newExtractionBatch:
    link: New extraction batch
    comment: from a PDF
  newClassificationBatch:
    link: New classification batch
    comment: for exercises not yet classified
  newAdaptationBatch:
    link: New adaptation batch
    comment: for exercises already classified by hand
  existingExtractionBatches: Existing extraction batches
  existingClassificationBatches: Existing classification batches
  existingAdaptationBatches: Existing adaptation batches
  extractionBatch: "Batch E{0}"
  classificationBatch: "Batch C{0}"
  adaptationBatch: "Batch A{0}"

  textbooks: Textbooks
  newTextbook: New textbook
  existingTextbooks: Existing textbooks

  createdBy: "created by {name} on {date}"
  loadMore: Load more...
fr:
  sandbox: Bac à sable
  adaptedExerciseExamples: Exemples d'exercices adaptés, avec leur code JSON.
  newBatch: Nouveau batch
  newExtractionBatch:
    link: Nouveau batch d'extraction
    comment: à partir d'un PDF
  newClassificationBatch:
    link: Nouveau batch de classification
    comment: pour les exercices pas encore classés
  newAdaptationBatch:
    link: Nouveau batch d'adaptation
    comment: pour les exercices déjà classés à la main
  existingExtractionBatches: Batchs d'extraction existants
  existingClassificationBatches: Batchs de classification existants
  existingAdaptationBatches: Batchs d'adaptation existants
  extractionBatch: "Batch E{0}"
  classificationBatch: "Batch C{0}"
  adaptationBatch: "Batch A{0}"

  textbooks: Manuels
  newTextbook: Nouveau manuel
  existingTextbooks: Manuels existants

  createdBy: "créé par {name} le {date}"
  loadMore: Charger plus...
</i18n>
