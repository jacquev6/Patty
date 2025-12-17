<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { type Textbook, useAuthenticatedClient } from '@/frontend/ApiClient'
import AddManualExercisesToPageForm from './AddManualExercisesToPageForm.vue'
import assert from '$/assert'
import AutoRefresh from '@/frontend/basic/AutoRefresh.vue'

const props = defineProps<{
  textbookId: string
  pageNumber: number
}>()

const client = useAuthenticatedClient()

type Data = {
  textbook: Textbook
  exerciseClasses: string[]
  needsRefresh: boolean
}

async function load() {
  const textbookPromise = client.GET('/api/textbooks/{id}', {
    params: { path: { id: props.textbookId } },
  })

  const exerciseClassesPromise = client.GET('/api/exercise-classes')

  const [textbookResponse, exerciseClassesResponse] = await Promise.all([textbookPromise, exerciseClassesPromise])

  if (textbookResponse.response.status === 404) {
    return null
  } else {
    assert(textbookResponse.data !== undefined)
    assert(exerciseClassesResponse.data !== undefined)
    return { textbook: textbookResponse.data, exerciseClasses: exerciseClassesResponse.data, needsRefresh: false }
  }
}

function breadcrumbs({ textbook: { title } }: Data) {
  return [
    { textKey: 'textbooks' },
    { textKey: 'existingTextbook', textArgs: { title }, to: { name: 'textbook', params: { id: props.textbookId } } },
    {
      textKey: 'textbookPage',
      textArgs: { number: props.pageNumber } as Record<string, string | number>,
      to: { name: 'textbook-page', params: { textbookId: props.textbookId, pageNumber: props.pageNumber } },
    },
    { textKey: 'addManualExercisesToPage' },
  ]
}
</script>

<template>
  <AutoRefresh :reloadOnChanges="{ textbookId, pageNumber }" :load :breadcrumbs>
    <template v-slot="{ data: { exerciseClasses } }">
      <AddManualExercisesToPageForm :textbookId :exerciseClasses :pageNumber />
    </template>
  </AutoRefresh>
</template>
