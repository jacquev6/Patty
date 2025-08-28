<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

import { type AdaptationBatch } from '@/apiClient'
import ResizableColumns from '@/ResizableColumns.vue'
import AdaptationStrategyEditor from '@/AdaptationStrategyEditor.vue'
import AdaptationPreview from './EditAdaptationBatchFormAdaptationPreview.vue'
import { preprocess as preprocessAdaptation } from '@/adaptations'
import { useAuthenticationTokenStore } from '@/AuthenticationTokenStore'

const props = defineProps<{
  adaptationBatch: AdaptationBatch
}>()

const { t } = useI18n()
const authenticationTokenStore = useAuthenticationTokenStore()

const adaptations = computed(() => props.adaptationBatch.adaptations.map(preprocessAdaptation))
</script>

<template>
  <ResizableColumns :columns="[1, 2]">
    <template #col-1>
      <p>{{ t('createdBy') }} {{ adaptationBatch.createdBy }}</p>
      <AdaptationStrategyEditor
        :availableStrategySettings="[]"
        :disabled="true"
        :modelValue="adaptationBatch.strategy"
      />
    </template>
    <template #col-2>
      <p>
        <RouterLink :to="{ name: 'create-adaptation-batch', query: { base: adaptationBatch.id } }">
          {{ t('newBatchBasedOnThisOne') }}
        </RouterLink>
      </p>
      <p>
        <I18nT keypath="download">
          <a :href="`/api/export/adaptation-batch/${adaptationBatch.id}.html?token=${authenticationTokenStore.token}`">
            {{ t('standaloneHtml') }}
          </a>
          <a :href="`/api/export/adaptation-batch/${adaptationBatch.id}.json?token=${authenticationTokenStore.token}`">
            {{ t('jsonData') }}
          </a>
        </I18nT>
      </p>
      <h1>{{ t('inputs') }}</h1>
      <AdaptationPreview
        v-for="(adaptation, index) in adaptations"
        :headerLevel="2"
        :index
        :adaptation
        :headerText="null"
        :showPageAndExercise="true"
      />
    </template>
  </ResizableColumns>
</template>

<i18n>
en:
  createdBy: "Created by:"
  newBatchBasedOnThisOne: New batch based on this one
  download: Download {0} or {1}
  standaloneHtml: standalone HTML
  jsonData: JSON data
  inputs: Inputs
fr:
  createdBy: "Créé par :"
  newBatchBasedOnThisOne: Nouveau batch basé sur celui-ci
  download: Télécharger {0} ou {1}
  standaloneHtml: le HTML autonome
  jsonData: les données JSON
  inputs: Entrées
</i18n>
