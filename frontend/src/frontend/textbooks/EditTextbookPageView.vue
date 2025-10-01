<script setup lang="ts">
import { type TextbookPage, useAuthenticatedClient } from '@/frontend/ApiClient'
import EditTextbookPageForm from './EditTextbookPageForm.vue'
import assert from '$/assert'
import AutoRefresh from '@/frontend/basic/AutoRefresh.vue'

const props = defineProps<{
  textbookId: string
  pageNumber: number
}>()

const client = useAuthenticatedClient()

async function load() {
  const response = await client.GET(`/api/textbooks/{id}/pages/{number}`, {
    params: { path: { id: props.textbookId, number: props.pageNumber } },
  })
  if (response.response.status === 404) {
    return null
  } else {
    assert(response.data !== undefined)
    return response.data
  }
}

function breadcrumbs({ textbook: { title } }: TextbookPage) {
  return [
    { textKey: 'textbooks' },
    { textKey: 'existingTextbook', textArgs: { title }, to: { name: 'textbook', params: { id: props.textbookId } } },
    { textKey: 'textbookPage', textArgs: { number: props.pageNumber } as Record<string, string | number>, to: {} },
  ]
}
</script>

<template>
  <AutoRefresh :reloadOnChanges="{ textbookId, pageNumber }" :load :breadcrumbs>
    <template v-slot="{ data: textbookPage, refresh }">
      <EditTextbookPageForm :textbookPage @textbookUpdated="refresh" />
    </template>
  </AutoRefresh>
</template>
