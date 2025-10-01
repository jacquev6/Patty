<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'

import BusyBox from '$/BusyBox.vue'
import assert from '$/assert'
import { useAuthenticatedClient } from '@/frontend/ApiClient'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import { parseExerciseFileName } from '@/frontend/sandbox/CreateAdaptationBatchFormInputsEditor.vue'

const props = defineProps<{
  textbookId: string
}>()

const emit = defineEmits<{
  (e: 'textbook-updated'): void
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const input = useTemplateRef('input')

const busy = ref(false)

const badFileName = ref(false)

async function upload() {
  busy.value = true
  assert(input.value !== null)
  assert(input.value.files !== null)

  const files: {
    file: File
    pageNumber: number
    exerciseNumber: string
  }[] = []

  badFileName.value = false
  for (let index = 0; index < input.value.files.length; index++) {
    const file = input.value.files.item(index)
    assert(file !== null)
    const { pageNumber, exerciseNumber } = parseExerciseFileName(file.name)
    badFileName.value ||= pageNumber === null || exerciseNumber === null
    if (pageNumber !== null && exerciseNumber !== null) {
      files.push({ file, pageNumber, exerciseNumber })
    }
  }

  if (!badFileName.value) {
    for (const { file, pageNumber, exerciseNumber } of files) {
      assert(pageNumber !== null)
      assert(exerciseNumber !== null)
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

    emit('textbook-updated')
    input.value.value = ''
  }

  busy.value = false
}
</script>

<template>
  <BusyBox :busy>
    <p>
      {{ t('open') }}
      <input
        ref="input"
        data-cy="external-files"
        type="file"
        multiple="true"
        @change="upload"
        accept=".docx,.xlsx,.odt,.pdf,.ggb"
      />
    </p>
    <p :class="{ error: badFileName }">({{ t('fileNamePattern') }})</p>
  </BusyBox>
</template>

<style scoped>
.error {
  color: red;
  font-weight: bold;
}
</style>

<i18n>
en:
  open: "Open one or several Word, Excel, PDF or GeoGebra files:"
  fileNamePattern: "Files must be named like \"P42Ex3.docx\" for exercise 3 page 42."
fr:
  open: "Ouvrir un ou plusieurs fichiers Word, Excel, PDF ou GeoGebra :"
  fileNamePattern: "Les fichiers doivent être nommés comme \"P42Ex3.docx\" pour l'exercice 3 page 42."
</i18n>
