<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { match } from 'ts-pattern'

import { useAuthenticatedClient, type Adaptation } from '@/frontend/ApiClient'
import assert from '$/assert'
import EditAdaptationForm from './EditAdaptationForm.vue'
import { useBreadcrumbsStore, type Breadcrumbs } from '@/frontend/basic/BreadcrumbsStore'

const props = defineProps<{
  id: string
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()
const breadcrumbsStore = useBreadcrumbsStore()

const found = ref<boolean | null>(null)
const adaptation = ref<Adaptation | null>(null)

onMounted(async () => {
  const response = await client.GET(`/api/adaptations/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    found.value = false
    adaptation.value = null
  } else {
    found.value = true
    assert(response.data !== undefined)
    adaptation.value = response.data

    const breadcrumbs = match(adaptation.value.belongsTo)
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

    breadcrumbs.push({ textKey: 'existingAdaptation', textArgs: { id: adaptation.value.id }, to: {} })

    breadcrumbsStore.set(breadcrumbs)
  }
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <template v-if="adaptation !== null">
      <EditAdaptationForm :adaptation @adaptationUpdated="adaptation = $event" />
    </template>
    <template v-else-if="found === false">
      <h1>{{ t('notFound') }}</h1>
    </template>
  </div>
</template>

<i18n>
en:
  notFound: Not found
fr:
  notFound: Non trouvé
</i18n>
