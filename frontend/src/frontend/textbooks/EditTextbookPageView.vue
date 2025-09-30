<script setup lang="ts">
import { type Textbook, useAuthenticatedClient } from '@/frontend/ApiClient'
import EditTextbookPageForm from './EditTextbookPageForm.vue'
import assert from '$/assert'
import AutoRefresh from '@/frontend/basic/AutoRefresh.vue'

const props = defineProps<{
  textbookId: string
  pageNumber: number
}>()

const client = useAuthenticatedClient()

async function load() {
  const response = await client.GET(`/api/textbooks/{id}`, { params: { path: { id: props.textbookId } } })
  if (response.response.status === 404) {
    return null
  } else {
    assert(response.data !== undefined)
    return response.data
  }
}

function breadcrumbs({ title }: Textbook) {
  return [
    { textKey: 'textbooks' },
    { textKey: 'existingTextbook', textArgs: { title }, to: { name: 'textbook', params: { id: props.textbookId } } },
    { textKey: 'textbookPage', textArgs: { number: props.pageNumber } as Record<string, string | number>, to: {} },
  ]
}
</script>

<template>
  <AutoRefresh :load :breadcrumbs>
    <template v-slot="{ data: textbook, refresh }">
      <EditTextbookPageForm :textbook :pageNumber @textbookUpdated="refresh" />
    </template>
  </AutoRefresh>
</template>
