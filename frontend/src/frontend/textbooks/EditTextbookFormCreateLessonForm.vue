<!--
MALIN Platform https://malin.cahiersfantastiques.fr/
Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
-->

<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'

import BusyBox from '$/BusyBox.vue'
import assert from '$/assert'
import { useAuthenticatedClient } from '@/frontend/ApiClient'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'

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

function parseLessonFileName(fileName: string) {
  const match = fileName.match(/P(\d+)Leçon\..*/)
  if (match === null) {
    return null
  }
  return parseInt(match[1])
}

async function upload() {
  busy.value = true
  assert(input.value !== null)
  assert(input.value.files !== null)

  const files: {
    file: File
    pageNumber: number
  }[] = []

  badFileName.value = false
  for (let index = 0; index < input.value.files.length; index++) {
    const file = input.value.files.item(index)
    assert(file !== null)
    const pageNumber = parseLessonFileName(file.name)
    badFileName.value ||= pageNumber === null
    if (pageNumber !== null) {
      files.push({ file, pageNumber })
    }
  }

  if (!badFileName.value) {
    for (const { file, pageNumber } of files) {
      assert(pageNumber !== null)
      const response = await client.POST('/api/textbooks/{textbook_id}/lessons', {
        params: {
          path: {
            textbook_id: props.textbookId,
          },
        },
        body: {
          creator: identifiedUser.identifier,
          pageNumber,
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
      <input ref="input" data-cy="lessons" type="file" multiple="true" @change="upload" accept=".docx,.odt,.pdf" />
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
  open: "Open one or several Word or PDF files:"
  fileNamePattern: "Files must be named like \"P57Leçon.docx\" for lesson page 57."
fr:
  open: "Ouvrir un ou plusieurs fichiers Word ou PDF :"
  fileNamePattern: "Les fichiers doivent être nommés comme \"P57Leçon.docx\" pour la leçon page 57."
</i18n>
