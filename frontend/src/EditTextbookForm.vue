<script setup lang="ts">
import { computed, ref } from 'vue'
import _ from 'lodash'

import { type LlmModel, type Textbook, client } from './apiClient'
import AdaptationPreview from './EditBatchFormAdaptationPreview.vue'
import { preprocess as preprocessAdaptation, type PreprocessedAdaptation } from './adaptations'
import EditTextbookFormCreateBatchForm from './EditTextbookFormCreateBatchForm.vue'
import assert from './assert'

const props = defineProps<{
  textbook: Textbook
  availableLlmModels: LlmModel[]
  availableStrategySettings: string[]
}>()

const emit = defineEmits<{
  (e: 'textbook-updated', textbook: Textbook): void
}>()

const view = ref<'batch' | 'page'>('batch')

const batches = computed(() =>
  props.textbook.batches.map((batch) => {
    return {
      ...batch,
      adaptations: batch.adaptations.map(preprocessAdaptation),
    }
  }),
)

const pages = computed(() => {
  const pages: Record<number, PreprocessedAdaptation[]> = {}
  for (const batch of batches.value) {
    if (!batch.removedFromTextbook) {
      for (const adaptation of batch.adaptations) {
        if (
          !adaptation.removedFromTextbook &&
          adaptation.input.pageNumber !== null &&
          adaptation.status.kind === 'success'
        ) {
          pages[adaptation.input.pageNumber] ??= []
          pages[adaptation.input.pageNumber].push(adaptation)
        }
      }
    }
  }

  for (const pageNumber in pages) {
    pages[pageNumber] = _.sortBy(pages[pageNumber], [
      ({ input: { exerciseNumber } }) => {
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

async function removeBatch(id: string, removed: boolean) {
  const response = await client.PUT('/api/adaptation/textbook/{textbook_id}/batch/{batch_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, batch_id: id }, query: { removed } },
  })
  assert(response.data !== undefined)
  emit('textbook-updated', response.data)
}

async function removeAdaptation(id: string, removed: boolean) {
  const response = await client.PUT('/api/adaptation/textbook/{textbook_id}/adaptation/{adaptation_id}/removed', {
    params: { path: { textbook_id: props.textbook.id, adaptation_id: id }, query: { removed } },
  })
  assert(response.data !== undefined)
  emit('textbook-updated', response.data)
}
</script>

<template>
  <h1>{{ textbook.title }}</h1>
  <p><a :href="`/api/adaptation/export/textbook-${textbook.id}.html`">Download standalone HTML</a></p>
  <p>
    View by
    <select data-cy="view-by" v-model="view">
      <option value="batch">batch</option>
      <option value="page">page</option></select
    >:
    <template v-if="view === 'batch'">in creation order, including errors and removed adaptations.</template>
    <template v-else>sorted by page and exercise number, including only successful not-removed adaptations.</template>
  </p>
  <template v-if="view === 'batch'">
    <h2>New batch</h2>
    <EditTextbookFormCreateBatchForm
      :availableLlmModels
      :availableStrategySettings
      :textbookId="textbook.id"
      @textbookUpdated="textbookUpdated"
    />
    <h2>Existing batches</h2>
    <template v-for="batch in batches">
      <template v-if="batch.removedFromTextbook">
        <h3>
          {{ batch.strategy.settings.name }} (removed) <button @click="removeBatch(batch.id, false)">Re-add</button>
        </h3>
      </template>
      <template v-else>
        <h3>{{ batch.strategy.settings.name }} <button @click="removeBatch(batch.id, true)">Remove</button></h3>
        <template v-for="(adaptation, index) in batch.adaptations">
          <template v-if="adaptation.removedFromTextbook">
            <h4 style="margin-top: 0">
              P{{ adaptation.input.pageNumber }}Ex{{ adaptation.input.exerciseNumber }} (input {{ index + 1 }}, removed)
              <button @click="removeAdaptation(adaptation.id, false)">Re-add</button>
            </h4>
          </template>
          <AdaptationPreview v-else header="h4" :index :adaptation>
            <h4 style="margin-top: 0">
              P{{ adaptation.input.pageNumber }}Ex{{ adaptation.input.exerciseNumber }} (input {{ index + 1 }})
              <button @click="removeAdaptation(adaptation.id, true)">Remove</button>
            </h4>
          </AdaptationPreview>
        </template>
      </template>
    </template>
  </template>
  <template v-else>
    <template v-for="(adaptations, pageNumber) in pages">
      <h2>Page {{ pageNumber }}</h2>
      <AdaptationPreview header="h3" v-for="(adaptation, index) in adaptations" :index :adaptation>
        <h3 style="margin-top: 0">Exercise {{ adaptation.input.exerciseNumber }}</h3>
      </AdaptationPreview>
    </template>
  </template>
</template>
