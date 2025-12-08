<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { type Textbook, type TextbookPage, useAuthenticatedClient } from '@/frontend/ApiClient'
import EditTextbookPageForm from './EditTextbookPageForm.vue'
import assert from '$/assert'
import AutoRefresh from '@/frontend/basic/AutoRefresh.vue'

const props = defineProps<{
  textbookId: string
  pageNumber: number
}>()

const client = useAuthenticatedClient()

type Data = {
  textbook: Textbook
  page: TextbookPage
  needsRefresh: boolean
}

async function load() {
  const textbookPromise = client.GET('/api/textbooks/{id}', {
    params: { path: { id: props.textbookId } },
  })
  const pagePromise = client.GET(`/api/textbooks/{id}/pages/{number}`, {
    params: { path: { id: props.textbookId, number: props.pageNumber } },
  })

  const [textbookResponse, pageResponse] = await Promise.all([textbookPromise, pagePromise])
  if (textbookResponse.response.status === 404 || pageResponse.response.status === 404) {
    return null
  } else {
    assert(textbookResponse.data !== undefined)
    assert(pageResponse.data !== undefined)
    return { textbook: textbookResponse.data, page: pageResponse.data, needsRefresh: pageResponse.data.needsRefresh }
  }
}

function breadcrumbs({ textbook: { title } }: Data) {
  return [
    { textKey: 'textbooks' },
    { textKey: 'existingTextbook', textArgs: { title }, to: { name: 'textbook', params: { id: props.textbookId } } },
    { textKey: 'textbookPage', textArgs: { number: props.pageNumber } as Record<string, string | number>, to: {} },
  ]
}
</script>

<template>
  <AutoRefresh :reloadOnChanges="{ textbookId, pageNumber }" :load :breadcrumbs>
    <template v-slot="{ data: { textbook, page }, refresh }">
      <EditTextbookPageForm :textbook :page @textbookUpdated="refresh" />
    </template>
  </AutoRefresh>
</template>
