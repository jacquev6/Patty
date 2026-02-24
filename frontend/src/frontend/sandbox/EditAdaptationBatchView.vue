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
import { type AdaptationBatch, useAuthenticatedClient } from '@/frontend/ApiClient'
import assert from '$/assert'
import EditAdaptationBatchForm from './EditAdaptationBatchForm.vue'
import AutoRefresh from '@/frontend/basic/AutoRefresh.vue'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

async function load() {
  const response = await client.GET(`/api/adaptation-batches/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    return null
  } else {
    assert(response.data !== undefined)
    return response.data
  }
}

function breadcrumbs({ id }: AdaptationBatch) {
  return [{ textKey: 'sandbox' }, { textKey: 'existingAdaptationBatch', textArgs: { id }, to: {} }]
}
</script>

<template>
  <AutoRefresh :reloadOnChanges="{ id }" :load :breadcrumbs>
    <template v-slot="{ data: adaptationBatch }">
      <EditAdaptationBatchForm :adaptationBatch />
    </template>
  </AutoRefresh>
</template>
