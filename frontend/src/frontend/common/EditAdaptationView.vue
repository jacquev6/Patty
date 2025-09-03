<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { useAuthenticatedClient, type Adaptation } from '@/frontend/ApiClient'
import assert from '$/assert'
import EditAdaptationForm from './EditAdaptationForm.vue'
import { preprocess as preprocessAdaptation } from '@/frontend/Adaptations'
import { useBreadcrumbsStore, type Breadcrumbs } from '@/frontend/basic/BreadcrumbsStore'

const props = defineProps<{
  id: string
}>()

const { t } = useI18n()
const client = useAuthenticatedClient()
const breadcrumbsStore = useBreadcrumbsStore()

const found = ref<boolean | null>(null)
const apiAdaptation = ref<Adaptation | null>(null)

const adaptation = computed(() => {
  if (apiAdaptation.value === null) {
    return null
  } else {
    return preprocessAdaptation(apiAdaptation.value)
  }
})

onMounted(async () => {
  const response = await client.GET(`/api/adaptations/{id}`, { params: { path: { id: props.id } } })

  if (response.response.status === 404) {
    found.value = false
    apiAdaptation.value = null
  } else {
    found.value = true
    assert(response.data !== undefined)
    apiAdaptation.value = response.data

    const breadcrumbs: Breadcrumbs = []
    if (apiAdaptation.value.textbookId === null) {
      breadcrumbs.push({ textKey: 'sandbox' })
      if (apiAdaptation.value.extractionBatchId !== null) {
        breadcrumbs.push({
          textKey: 'existingExtractionBatch',
          textArgs: { id: apiAdaptation.value.extractionBatchId },
          to: { name: 'extraction-batch', params: { id: apiAdaptation.value.extractionBatchId } },
        })
      } else if (apiAdaptation.value.classificationBatchId !== null) {
        breadcrumbs.push({
          textKey: 'existingClassificationBatch',
          textArgs: { id: apiAdaptation.value.classificationBatchId },
          to: { name: 'classification-batch', params: { id: apiAdaptation.value.classificationBatchId } },
        })
      } else if (apiAdaptation.value.adaptationBatchId !== null) {
        breadcrumbs.push({
          textKey: 'existingAdaptationBatch',
          textArgs: { id: apiAdaptation.value.adaptationBatchId },
          to: { name: 'adaptation-batch', params: { id: apiAdaptation.value.adaptationBatchId } },
        })
      }
    } else {
      assert(apiAdaptation.value.textbookTitle !== null)
      breadcrumbs.push({ textKey: 'textbooks' })
      breadcrumbs.push({
        textKey: 'existingTextbook',
        textArgs: { title: apiAdaptation.value.textbookTitle },
        to: { name: 'textbook', params: { id: apiAdaptation.value.textbookId } },
      })
    }

    breadcrumbs.push({ textKey: 'existingAdaptation', textArgs: { id: apiAdaptation.value.id }, to: {} })

    breadcrumbsStore.set(breadcrumbs)
  }
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <template v-if="adaptation !== null">
      <EditAdaptationForm :adaptation @adaptationUpdated="apiAdaptation = $event" />
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
