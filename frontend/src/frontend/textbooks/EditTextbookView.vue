<script setup lang="ts">
import { type Textbook, useAuthenticatedClient } from '@/frontend/ApiClient'
import EditTextbookForm from './EditTextbookForm.vue'
import assert from '$/assert'
import AutoRefresh from '@/frontend/basic/AutoRefresh.vue'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

async function load() {
  const response = await client.GET(`/api/textbooks/{id}`, { params: { path: { id: props.id } } })
  if (response.response.status === 404) {
    return null
  } else {
    assert(response.data !== undefined)
    return response.data
  }
}

function breadcrumbs({ textbook: { title } }: { textbook: Textbook }) {
  return [{ textKey: 'textbooks' }, { textKey: 'existingTextbook', textArgs: { title }, to: {} }]
}
</script>

<template>
  <AutoRefresh :load :breadcrumbs>
    <template v-slot="{ data: { textbook, availableStrategySettings }, refresh }">
      <EditTextbookForm :availableStrategySettings :textbook @textbookUpdated="refresh" />
    </template>
  </AutoRefresh>
</template>
