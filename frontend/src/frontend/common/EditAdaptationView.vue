<script setup lang="ts">
import { match } from 'ts-pattern'

import { useAuthenticatedClient, type Adaptation } from '@/frontend/ApiClient'
import assert from '$/assert'
import EditAdaptationForm from './EditAdaptationForm.vue'
import { type Breadcrumbs } from '@/frontend/basic/BreadcrumbsStore'
import AutoRefresh from '@/frontend/basic/AutoRefresh.vue'

const props = defineProps<{
  id: string
}>()

const client = useAuthenticatedClient()

async function load() {
  const response = await client.GET(`/api/adaptations/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    return null
  } else {
    assert(response.data !== undefined)
    return { ...response.data, needsRefresh: false }
  }
}

function breadcrumbs(adaptation: Adaptation) {
  const breadcrumbs = match(adaptation.belongsTo)
    .returnType<Breadcrumbs>()
    .with({ kind: 'textbook' }, ({ id, title }) => [
      { textKey: 'textbooks' },
      { textKey: 'existingTextbook', textArgs: { title }, to: { name: 'textbook', params: { id } } },
    ])
    .with({ kind: 'adaptation-batch' }, ({ id }) => [
      { textKey: 'sandbox' },
      { textKey: 'existingAdaptationBatch', textArgs: { id }, to: { name: 'adaptation-batch', params: { id } } },
    ])
    .with({ kind: 'classification-batch' }, ({ id }) => [
      { textKey: 'sandbox' },
      {
        textKey: 'existingClassificationBatch',
        textArgs: { id },
        to: { name: 'classification-batch', params: { id } },
      },
    ])
    .with({ kind: 'extraction-batch' }, ({ id }) => [
      { textKey: 'sandbox' },
      { textKey: 'existingExtractionBatch', textArgs: { id }, to: { name: 'extraction-batch', params: { id } } },
    ])
    .exhaustive()

  breadcrumbs.push({ textKey: 'existingAdaptation', textArgs: { id: adaptation.id }, to: {} })

  return breadcrumbs
}
</script>

<template>
  <AutoRefresh :load :breadcrumbs>
    <template v-slot="{ data: adaptation, refresh }">
      <EditAdaptationForm :adaptation @adaptationUpdated="refresh" />
    </template>
  </AutoRefresh>
</template>
