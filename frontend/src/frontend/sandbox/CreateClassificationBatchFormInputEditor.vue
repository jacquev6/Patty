<script lang="ts">
export type InputWithFile = {
  pageNumber: number | null
  exerciseNumber: string | null
  inputFile?: string
  instructionHintExampleText: string
  statementText: string
}
</script>

<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import WhiteSpace from '$/WhiteSpace.vue'
import InputForNumberOrNull from '$/InputForNumberOrNull.vue'
import InputForNonEmptyStringOrNull from '$/InputForNonEmptyStringOrNull.vue'
import TextArea from '$/TextArea.vue'
const { t } = useI18n()

defineProps<{
  headers: string
  index: number
}>()

const model = defineModel<InputWithFile>({ required: true })

const pageNumberProxy = computed({
  get: () => model.value.pageNumber,
  set: (value) => {
    model.value.pageNumber = value
    model.value.inputFile = undefined
  },
})

const exerciseNumberProxy = computed({
  get: () => model.value.exerciseNumber,
  set: (value) => {
    model.value.exerciseNumber = value
    model.value.inputFile = undefined
  },
})

const instructionHintExampleTextProxy = computed({
  get: () => model.value.instructionHintExampleText,
  set: (value) => {
    model.value.instructionHintExampleText = value
    model.value.inputFile = undefined
  },
})

const statementTextProxy = computed({
  get: () => model.value.statementText,
  set: (value) => {
    model.value.statementText = value
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
    <template v-if="model.instructionHintExampleText.trim() === '' && model.statementText.trim() === ''">
      <WhiteSpace />
      <span class="discreet">{{ t('emptyIgnored') }}</span>
    </template>
  </component>
  <p>
    {{ t('page') }}: <InputForNumberOrNull data-cy="input-page-number" v-model="pageNumberProxy" />,
    {{ t('exercise') }}:
    <InputForNonEmptyStringOrNull data-cy="input-exercise-number" v-model="exerciseNumberProxy" />
  </p>
  <p>{{ t('instructionHintExample') }}</p>
  <TextArea ref="textArea" data-cy="input-instruction-text" v-model="instructionHintExampleTextProxy"></TextArea>
  <p>{{ t('statement') }}</p>
  <TextArea data-cy="input-statement-text" v-model="statementTextProxy"></TextArea>
</template>

<style scoped>
.discreet {
  font-size: 70%;
  color: grey;
}
</style>

<i18n>
en:
  input: Input
  emptyIgnored: "(empty, ignored)"
  page: Page
  exercise: exercise
  instructionHintExample: "Instruction, hint and example:"
  statement: "Statement:"
fr:
  input: Entrée
  emptyIgnored: "(vide, ignoré)"
  page: Page
  exercise: exercice
  instructionHintExample: "Consigne, indice et exemple :"
  statement: "Énoncé :"
</i18n>
