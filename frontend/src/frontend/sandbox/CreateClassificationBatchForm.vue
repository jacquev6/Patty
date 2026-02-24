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
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { useAuthenticatedClient } from '@/frontend/ApiClient'
import LlmModelSelector from '@/frontend/common/LlmModelSelector.vue'
import { type InputWithFile } from './CreateClassificationBatchFormInputEditor.vue'
import CreateClassificationBatchFormInputsEditor from './CreateClassificationBatchFormInputsEditor.vue'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import { useApiConstantsStore } from '@/frontend/ApiConstantsStore'
import classificationCamembert20250520 from '@/frontend/sandbox/ClassificationCamembert20250520'
import WhiteSpace from '$/WhiteSpace.vue'

const { t } = useI18n()
const apiConstantsStore = useApiConstantsStore()
const router = useRouter()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const runAdaptationAsString = ref<'yes' | 'no'>('no')

const llmModel = ref(apiConstantsStore.availableAdaptationLlmModels[0])

const runAdaptation = computed(() => runAdaptationAsString.value === 'yes')

const inputs = reactive<InputWithFile[]>([])

const cleanedUpInputs = computed(() =>
  inputs
    .filter((input) => input.instructionHintExampleText.trim() !== '' || input.statementText.trim() !== '')
    .map(({ pageNumber, exerciseNumber, instructionHintExampleText, statementText }) => ({
      pageNumber,
      exerciseNumber,
      instructionHintExampleText,
      statementText,
    })),
)

const disabled = computed(() => cleanedUpInputs.value.length === 0)

async function submit() {
  const response = await client.POST('/api/classification-batches', {
    body: {
      creator: identifiedUser.identifier,
      inputs: cleanedUpInputs.value,
      modelForAdaptation: runAdaptation.value ? llmModel.value : null,
    },
  })
  if (response.data !== undefined) {
    router.push({ name: 'classification-batch', params: { id: response.data.id } })
  }
}
</script>

<template>
  <h1>{{ t('settings') }}</h1>
  <p>
    {{ t('classNamesProduced') }}
    <template v-for="(className, index) in classificationCamembert20250520.classesProduced">
      <template v-if="index !== 0">, </template>
      <code>{{ className }}</code>
    </template>
  </p>
  <p>
    {{ t('runAdaptation') }}
    <select data-cy="run-adaptation" v-model="runAdaptationAsString">
      <option value="yes">{{ t('yes') }}</option>
      <option value="no">{{ t('no') }}</option>
    </select>
    <template v-if="runAdaptation">
      <WhiteSpace />
      <I18nT keypath="runAdaptationYesUsing">
        <LlmModelSelector
          :availableLlmModels="apiConstantsStore.availableAdaptationLlmModels"
          :disabled="false"
          v-model="llmModel"
        >
          <template #provider>{{ t('runAdaptationUsingProvider') }}</template>
          <template #model><WhiteSpace />{{ t('runAdaptationUsingModel') }}</template>
        </LlmModelSelector>
      </I18nT>
    </template>
  </p>
  <h1>{{ t('inputs') }}</h1>
  <p>
    <button @click="submit" :disabled>{{ t('submit') }}</button>
  </p>
  <CreateClassificationBatchFormInputsEditor headers="h2" v-model="inputs" />
</template>

<i18n>
en:
  settings: Settings
  classNamesProduced: "Class names produced:"
  runAdaptation: "Run adaptations after classification:"
  runAdaptationYesUsing: "using {0} with the latest settings for each known exercise class"
  runAdaptationUsingProvider: provider
  runAdaptationUsingModel: and model
  yes: yes
  no: no
  submit: Submit
  inputs: Inputs
fr:
  settings: Paramètres
  classNamesProduced: "Noms de classe produits :"
  runAdaptation: "Exécuter l'adaptation après la classification :"
  runAdaptationYesUsing: "en utilisant {0} avec les derniers paramètres pour chaque classe d'exercice connue"
  runAdaptationUsingProvider: fournisseur
  runAdaptationUsingModel: et modèle
  yes: oui
  no: non
  submit: Soumettre
  inputs: Entrées
</i18n>
