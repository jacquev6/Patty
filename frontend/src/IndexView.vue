<script setup lang="ts">
import { onMounted, reactive } from 'vue'

import { type Batches, client } from './apiClient'
import assert from './assert'

const batches = reactive<Batches['batches']>([])

onMounted(async () => {
  const response = await client.GET('/api/adaptation/batches')

  assert(response.data !== undefined)

  batches.splice(0, batches.length, ...response.data.batches)
})
</script>

<template>
  <h1>New batch</h1>
  <p><RouterLink :to="{ name: 'create-batch' }">New adaptation batch</RouterLink></p>

  <h1>Existing batches</h1>
  <ul>
    <li v-for="batch in batches">
      <RouterLink :to="{ name: 'batch', params: { id: batch.id } }">
        Batch {{ batch.id }}, created by {{ batch.createdBy }} on {{ batch.createdAt }}
      </RouterLink>
    </li>
  </ul>
</template>
