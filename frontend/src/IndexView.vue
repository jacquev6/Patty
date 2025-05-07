<script setup lang="ts">
import { onMounted, reactive } from 'vue'

import { type Batches, type Textbooks, client } from './apiClient'
import assert from './assert'
import WhiteSpace from './WhiteSpace.vue'
import FixedColumns from './FixedColumns.vue'
import CreateTextbookForm from './CreateTextbookForm.vue'

const batches = reactive<Batches['batches']>([])
const textbooks = reactive<Textbooks['textbooks']>([])

onMounted(async () => {
  const batchesPromise = client.GET('/api/adaptation/batches')
  const textbooksPromise = client.GET('/api/adaptation/textbooks')

  const batchesResponse = await batchesPromise
  assert(batchesResponse.data !== undefined)
  batches.splice(0, batches.length, ...batchesResponse.data.batches)

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
        <p><RouterLink :to="{ name: 'create-batch' }">New adaptation batch</RouterLink></p>

        <h2>Existing batches</h2>
        <ul>
          <li v-for="batch in batches">
            <RouterLink :to="{ name: 'batch', params: { id: batch.id } }"> Batch {{ batch.id }} </RouterLink>
            (<template v-if="batch.strategySettingsName !== null"
              >{{ batch.strategySettingsName }}<WhiteSpace /></template
            >using {{ batch.model.provider }}/{{ batch.model.name }}, created by {{ batch.createdBy }} on
            {{ new Date(batch.createdAt).toLocaleString() }})
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
