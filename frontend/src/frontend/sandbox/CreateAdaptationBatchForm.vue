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
import { computed, reactive, ref, watch } from 'vue'
import deepCopy from 'deep-copy'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

import { type BaseAdaptationBatch, useAuthenticatedClient } from '@/frontend/ApiClient'
import BusyBox from '$/BusyBox.vue'
import ResizableColumns from '$/ResizableColumns.vue'
import AdaptationStrategyEditor from '@/frontend/common/AdaptationStrategyEditor.vue'
import { useIdentifiedUserStore } from '@/frontend/basic/IdentifiedUserStore'
import { type InputWithFile } from './CreateAdaptationBatchFormInputEditor.vue'
import CreateAdaptationBatchFormInputsEditor from './CreateAdaptationBatchFormInputsEditor.vue'

const props = defineProps<{
  baseAdaptationBatch: BaseAdaptationBatch
}>()

const router = useRouter()
const { t } = useI18n()

const client = useAuthenticatedClient()

const identifiedUser = useIdentifiedUserStore()

const strategy = reactive(deepCopy(props.baseAdaptationBatch.strategy))
const inputs = reactive<InputWithFile[]>(deepCopy(props.baseAdaptationBatch.inputs))
watch(
  () => props.baseAdaptationBatch,
  (newValue) => {
    Object.assign(strategy, deepCopy(newValue.strategy))
    inputs.splice(0, inputs.length, ...deepCopy(newValue.inputs))
  },
)

const busy = ref(false)

async function submit() {
  busy.value = true

  const response = await client.POST('/api/adaptation-batches', {
    body: {
      creator: identifiedUser.identifier,
      strategy,
      inputs: cleanedUpInputs.value,
    },
  })
  busy.value = false
  if (response.data !== undefined) {
    router.push({ name: 'adaptation-batch', params: { id: response.data.id } })
  }
}

const cleanedUpInputs = computed(() =>
  inputs
    .filter((input) => input.text.trim() !== '')
    .map(({ pageNumber, exerciseNumber, text }) => ({ pageNumber, exerciseNumber, text })),
)

const disabled = computed(() => {
  return strategy.settings.systemPrompt.trim() === '' || cleanedUpInputs.value.length === 0
})

const availableStrategySettings = computed(() => props.baseAdaptationBatch.availableStrategySettings)

const columns = [
  { name: 'col-1', width: 1 },
  { name: 'col-2', width: 1 },
]
</script>

<template>
  <BusyBox :busy>
    <ResizableColumns :columns>
      <template #col-1>
        <AdaptationStrategyEditor :availableStrategySettings :disabled="false" v-model="strategy" />
      </template>
      <template #col-2>
        <h1>{{ t('inputs') }}</h1>
        <p>
          <button @click="submit" :disabled>{{ t('submit') }}</button>
        </p>
        <CreateAdaptationBatchFormInputsEditor headers="h2" v-model="inputs" />
      </template>
    </ResizableColumns>
  </BusyBox>
</template>

<i18n>
en:
  inputs: Inputs
  submit: Submit
fr:
  inputs: Entrées
  submit: Soumettre
</i18n>
