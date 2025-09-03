<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { ref } from 'vue'

import { useAuthenticatedClient, type ClassificationBatch } from '@/frontend/ApiClient'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import EditClassificationOrExtractionBatchFormExercisePreview from './EditClassificationOrExtractionBatchFormExercisePreview.vue'
import { useAuthenticationTokenStore } from '@/frontend/basic/AuthenticationTokenStore'
import classificationCamembert20250520 from '@/frontend/sandbox/ClassificationCamembert20250520'
import { useApiConstantsStore } from '@/frontend/ApiConstantsStore'
import WhiteSpace from '$/WhiteSpace.vue'

const props = defineProps<{
  classificationBatch: ClassificationBatch
}>()

const emit = defineEmits<{
  (e: 'batch-updated'): void
}>()

const client = useAuthenticatedClient()
const { d } = useI18n({ useScope: 'global' })
const { t } = useI18n()

const authenticationTokenStore = useAuthenticationTokenStore()

const editingModelForAdaptation = ref(false)
const apiConstantsStore = useApiConstantsStore()
const llmModelForAdaptation = ref(apiConstantsStore.availableAdaptationLlmModels[0])
async function submitAdaptation() {
  editingModelForAdaptation.value = false
  await client.PUT('/api/classification-batches/{id}/model-for-adaptation', {
    params: { path: { id: props.classificationBatch.id } },
    body: llmModelForAdaptation.value,
  })
  emit('batch-updated')
}
</script>

<template>
  <h1>{{ t('settings') }}</h1>
  <p>{{ t('createdBy') }} {{ classificationBatch.createdBy }}</p>
  <p>
    <I18nT keypath="classificationModel">
      <code>{{ classificationCamembert20250520.fileName }}</code>
      <span>{{ classificationCamembert20250520.providedBy }}</span>
      <span>{{ d(classificationCamembert20250520.providedOn, 'long-date') }}</span>
    </I18nT>
  </p>
  <p>
    {{ t('classNamesProduced') }}
    <template v-for="(className, index) in classificationCamembert20250520.classesProduced">
      <template v-if="index !== 0">, </template>
      <code>{{ className }}</code>
    </template>
  </p>
  <p>
    {{ t('runAdaptation') }}
    <template v-if="classificationBatch.modelForAdaptation === null">
      <template v-if="editingModelForAdaptation">
        <I18nT keypath="runAdaptationYesUsing">
          <LlmModelSelector
            :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
            :disabled="false"
            :modelValue="llmModelForAdaptation"
          >
            <template #provider>{{ t('runAdaptationUsingProvider') }}</template>
            <template #model><WhiteSpace />{{ t('runAdaptationUsingModel') }}</template>
          </LlmModelSelector> </I18nT
        >: <button @click="submitAdaptation">{{ t('submit') }}</button>
      </template>
      <template v-else>
        {{ t('no') }}
        <span style="cursor: pointer" @click="editingModelForAdaptation = true">({{ t('change') }})</span>
      </template>
    </template>
    <template v-else>
      <I18nT keypath="runAdaptationYesUsing">
        <LlmModelSelector :availableLlmModels="[]" :disabled="true" :modelValue="llmModelForAdaptation">
          <template #provider>{{ t('runAdaptationUsingProvider') }}</template>
          <template #model><WhiteSpace />{{ t('runAdaptationUsingModel') }}</template>
        </LlmModelSelector> </I18nT
      >.
    </template>
  </p>
  <p>
    <I18nT keypath="download">
      <a
        :href="`/api/export/classification-batch/${classificationBatch.id}.html?token=${authenticationTokenStore.token}`"
      >
        {{ t('standaloneHtml') }}
      </a>
      <a
        :href="`/api/export/classification-batch/${classificationBatch.id}.json?token=${authenticationTokenStore.token}`"
      >
        {{ t('jsonData') }}
      </a>
    </I18nT>
  </p>
  <h1>{{ t('inputs') }}</h1>
  <template v-for="(exercise, index) in classificationBatch.exercises">
    <EditClassificationOrExtractionBatchFormExercisePreview
      :headerLevel="2"
      :batch="{ kind: 'classification', id: classificationBatch.id }"
      :headerText="`Input ${index + 1}`"
      :showPageAndExercise="true"
      :classificationWasRequested="true"
      :adaptationWasRequested="classificationBatch.modelForAdaptation !== null"
      :exercise
      @batchUpdated="emit('batch-updated')"
    />
  </template>
</template>

<i18n>
en:
  settings: Settings
  createdBy: "Created by:"
  classificationModel: "Classification model: {0}, provided by {1} by e-mail on {2}"
  classNamesProduced: "Class names produced:"
  change: 🖊️ change
  runAdaptation: "Run adaptation after classification:"
  runAdaptationYesUsing: "yes, using {0} with the latest settings for each known exercise class"
  runAdaptationUsingProvider: provider
  runAdaptationUsingModel: and model
  no: no
  submit: Submit
  download: Download {0} or {1}
  standaloneHtml: standalone HTML
  jsonData: JSON data
  inputs: Inputs
fr:
  settings: Paramètres
  createdBy: "Créé par :"
  classificationModel: "Modèle de classification : {0}, fourni par {1} par e-mail le {2}"
  classNamesProduced: "Noms de classe produits :"
  change: 🖊️ modifier
  runAdaptation: "Exécuter l'adaptation après la classification :"
  runAdaptationYesUsing: "oui, en utilisant {0} avec les derniers paramètres pour chaque classe d'exercice connue"
  runAdaptationUsingProvider: fournisseur
  runAdaptationUsingModel: et modèle
  no: non
  submit: Soumettre
  download: Télécharger {0} ou {1}
  standaloneHtml: le HTML autonome
  jsonData: les données JSON
  inputs: Entrées
</i18n>
