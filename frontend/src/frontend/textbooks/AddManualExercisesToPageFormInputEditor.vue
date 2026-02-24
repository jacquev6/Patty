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

<script lang="ts">
export type InputWithFile = {
  exerciseNumber: string | null
  inputFile?: string
  exerciseClass: string | null
  text: string
}
</script>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { computed, useTemplateRef } from 'vue'

import InputForNonEmptyStringOrNull from '$/InputForNonEmptyStringOrNull.vue'
import TextArea from '$/TextArea.vue'
import WhiteSpace from '$/WhiteSpace.vue'

defineProps<{
  headers: string
  exerciseClasses: string[]
  index: number
}>()

const model = defineModel<InputWithFile>({ required: true })

const { t } = useI18n()

const exerciseNumberProxy = computed({
  get: () => model.value.exerciseNumber,
  set: (value) => {
    model.value.exerciseNumber = value
    model.value.inputFile = undefined
  },
})

const textProxy = computed({
  get: () => model.value.text,
  set: (value) => {
    model.value.text = value
    model.value.inputFile = undefined
  },
})

const textArea = useTemplateRef('textArea')

defineExpose({
  focus() {
    if (textArea.value !== null) {
      textArea.value.wrapped.focus()
    }
  },
})
</script>

<template>
  <component :is="headers">
    {{ t('input') }} {{ index }}
    <template v-if="model.inputFile !== undefined">
      <span class="discreet">({{ model.inputFile }})</span>
    </template>
    <template v-if="model.text.trim() === ''">
      <WhiteSpace />
      <span class="discreet">{{ t('emptyIgnored') }}</span>
    </template>
  </component>
  <p>
    {{ t('exerciseNumber') }}
    <InputForNonEmptyStringOrNull data-cy="input-exercise-number" v-model="exerciseNumberProxy" />,
    {{ t('exerciseClass') }}
    <select data-cy="input-exercise-class" v-model="model.exerciseClass">
      <!-- eslint-disable-next-line @intlify/vue-i18n/no-raw-text -->
      <option :value="null">--</option>
      <option v-for="name in exerciseClasses" :key="name" :value="name">{{ name }}</option>
    </select>
  </p>
  <TextArea ref="textArea" data-cy="input-text" v-model="textProxy"></TextArea>
</template>

<style scoped>
.discreet {
  font-size: 70%;
  color: grey;
}
</style>

<i18n lang="yaml">
en:
  input: 'Input'
  emptyIgnored: '(empty, ignored)'
  exerciseNumber: 'Exercise number:'
  exerciseClass: 'type:'
fr:
  input: 'Entrée'
  emptyIgnored: '(vide, ignorée)'
  exerciseNumber: "Numéro d'exercice :"
  exerciseClass: 'type :'
</i18n>
