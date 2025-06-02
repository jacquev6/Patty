<script setup lang="ts">
import { onMounted, reactive } from 'vue'

import { type AdaptationBatches, type Textbooks, useAuthenticatedClient } from './apiClient'
import assert from './assert'
import WhiteSpace from './WhiteSpace.vue'
import FixedColumns from './FixedColumns.vue'
import CreateTextbookForm from './CreateTextbookForm.vue'

const client = useAuthenticatedClient()

const adaptationBatches = reactive<AdaptationBatches['adaptationBatches']>([])
const textbooks = reactive<Textbooks['textbooks']>([])

onMounted(async () => {
  const adaptationBatchesPromise = client.GET(
    '/api/adaptation/adaptation-batches' /*, {headers: {Authorization: `Bearer ${authenticationTokenStore.token}`}}*/,
  )
  const textbooksPromise = client.GET(
    '/api/adaptation/textbooks' /*, {headers: {Authorization: `Bearer ${authenticationTokenStore.token}`}}*/,
  )

  const adaptationBatchesResponse = await adaptationBatchesPromise
  assert(adaptationBatchesResponse.data !== undefined)
  adaptationBatches.splice(0, adaptationBatches.length, ...adaptationBatchesResponse.data.adaptationBatches)

  const textbooksResponse = await textbooksPromise
  assert(textbooksResponse.data !== undefined)
  textbooks.splice(0, textbooks.length, ...textbooksResponse.data.textbooks)
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <FixedColumns :columns="[1, 1]">
      <template #col-1>
        <h1>Sandbox</h1>
        <h2>New batch</h2>
        <p>
          <RouterLink :to="{ name: 'create-classification-batch' }">New classification batch</RouterLink> (for exercises
          not yet classified)
        </p>
        <p>
          <RouterLink :to="{ name: 'create-adaptation-batch' }">New adaptation batch</RouterLink> (for exercises already
          classified by hand)
        </p>

        <h2>Existing classification batches</h2>
        <!-- <p>@todo List existing classification batches</p> -->

        <h2>Existing adaptation batches</h2>
        <ul>
          <li v-for="adaptationBatch in adaptationBatches">
            <RouterLink :to="{ name: 'adaptation-batch', params: { id: adaptationBatch.id } }">
              Batch {{ adaptationBatch.id }}
            </RouterLink>
            (<template v-if="adaptationBatch.strategySettingsName !== null"
              >{{ adaptationBatch.strategySettingsName }}<WhiteSpace /></template
            >using {{ adaptationBatch.model.provider }}/{{ adaptationBatch.model.name }}, created by
            {{ adaptationBatch.createdBy }} on {{ new Date(adaptationBatch.createdAt).toLocaleString() }})
          </li>
        </ul>
      </template>
      <template #col-2>
        <h1>Textbooks</h1>
        <h2>New textbook</h2>
        <CreateTextbookForm />
        <h2>Existing textbooks</h2>
        <ul>
          <li v-for="textbook in textbooks">
            <RouterLink :to="{ name: 'textbook', params: { id: textbook.id } }">{{ textbook.title }}</RouterLink>
            (created by {{ textbook.createdBy }} on {{ new Date(textbook.createdAt).toLocaleString() }})
          </li>
        </ul>
      </template>
    </FixedColumns>
  </div>
</template>
