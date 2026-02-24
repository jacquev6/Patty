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
