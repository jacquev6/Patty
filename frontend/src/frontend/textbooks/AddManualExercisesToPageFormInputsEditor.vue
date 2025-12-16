<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'

import AddManualExercisesToPageFormInputEditor, {
  type InputWithFile,
} from './AddManualExercisesToPageFormInputEditor.vue'
import assert from '$/assert'

defineProps<{
  headers: string
  exerciseClasses: string[]
}>()

const { t } = useI18n()

const inputs = defineModel<InputWithFile[]>({ required: true })

const editors = useTemplateRef<InstanceType<typeof AddManualExercisesToPageFormInputEditor>[]>('editors')

watch(
  inputs,
  (inputs) => {
    if (inputs.length === 0 || inputs[inputs.length - 1].text !== '') {
      inputs.push({ exerciseNumber: null, exerciseClass: null, text: '' })
    }
    assert(inputs[inputs.length - 1].text === '')

    let popped = false
    while (inputs.length > 1 && inputs[inputs.length - 2].text === '') {
      inputs.pop()
      popped = true
    }
    if (popped && editors.value !== null) {
      editors.value[inputs.length - 1].focus()
    }
  },
  { deep: true, immediate: true },
)
</script>

<template>
  <p>
    {{ t('openFiles') }}
    <input data-cy="input-files" type="file" multiple="true" accept=".txt,.zip" />
  </p>
  <template v-for="index in inputs.length">
    <AddManualExercisesToPageFormInputEditor
      ref="editors"
      :index
      :headers
      :exerciseClasses
      v-model="inputs[index - 1]"
    />
  </template>
</template>

<i18n>
en:
  openFiles: "Open one or several text or zip files:"
fr:
  openFiles: "Ouvrir un ou plusieurs fichiers texte ou zip :"
</i18n>
