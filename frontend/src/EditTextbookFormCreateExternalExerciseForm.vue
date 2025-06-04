<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'

import { type Textbook } from './apiClient'
import BusyBox from './BusyBox.vue'
import assert from './assert'
import { useAuthenticatedClient } from './apiClient'
import { useIdentifiedUserStore } from './IdentifiedUserStore'
import { parseExerciseFileName } from './CreateAdaptationBatchFormInputsEditor.vue'

const props = defineProps<{
  textbookId: string
}>()

const emit = defineEmits<{
  (e: 'textbook-updated', textbook: Textbook): void
}>()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const input = useTemplateRef('input')

const busy = ref(false)

async function upload() {
  busy.value = true
  assert(input.value !== null)
  assert(input.value.files !== null)
  for (let index = 0; index < input.value.files.length; index++) {
    const file = input.value.files.item(index)
    assert(file !== null)
    const { pageNumber, exerciseNumber } = parseExerciseFileName(file.name)
    const response = await client.POST('/api/textbooks/{textbook_id}/external-exercises', {
      params: {
        path: {
          textbook_id: props.textbookId,
        },
      },
      body: {
        creator: identifiedUser.identifier,
        pageNumber,
        exerciseNumber,
        originalFileName: file.name,
      },
    })
    assert(response.response.status === 200)
    assert(response.data !== undefined)
    const uploadResponse = await fetch(response.data.putUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': file.type,
      },
      body: file,
    })
    assert(uploadResponse.status === 200)
  }

  const textbookResponse = await client.GET(`/api/textbooks/{id}`, {
    params: { path: { id: props.textbookId } },
  })
  assert(textbookResponse.data !== undefined)
  emit('textbook-updated', textbookResponse.data.textbook)

  input.value.value = ''
  busy.value = false
}
</script>

<template>
  <BusyBox :busy>
    <p>
      Open one or several Word, Excel, PDF or GeoGebra files:
      <input
        ref="input"
        data-cy="external-files"
        type="file"
        multiple="true"
        @change="upload"
        accept=".docx,.xlsx,.odt,.pdf,.ggb"
      />
    </p>
  </BusyBox>
</template>
