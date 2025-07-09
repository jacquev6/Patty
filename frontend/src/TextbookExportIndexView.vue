<script setup lang="ts">
import { computed, ref } from 'vue'
import { match, P } from 'ts-pattern'
import { useI18n } from 'vue-i18n'

import TextbookExportExercisesList from './TextbookExportExercisesList.vue'
import TriColoredInput from './TriColoredInput.vue'
import VirtualNumericalKeyboard from './VirtualNumericalKeyboard.vue'
import VirtualEraser from './VirtualEraser.vue'
import WhiteSpace from './WhiteSpace.vue'
import type { Data, Exercise } from './TextbookExportRootView.vue'

const props = defineProps<{
  data: Data
}>()

const { t } = useI18n()

const pageNumberFilter = ref<string>('')
const exerciseNumberFilter = ref<string>('')

type Filtered =
  | { kind: 'nothing' }
  | { kind: 'message'; message: string }
  | { kind: 'exercises'; exercises: Exercise[] }

const filtered = computed(() => {
  return match([pageNumberFilter.value, exerciseNumberFilter.value])
    .returnType<Filtered>()
    .with(['', ''], () => ({ kind: 'nothing' }))
    .with(['', P.string], () => {
      return { kind: 'message', message: t('message.noPage') }
    })
    .with([P.string, P.string], ([pageString, number]) => {
      const page = parseInt(pageString, 10)
      const exercises = props.data.exercises.filter((exercise) => exercise.pageNumber === page)
      if (exercises.length === 0) {
        return { kind: 'message', message: t('message.unexistingPage', { page }) }
      } else if (number === '') {
        return { kind: 'exercises', exercises }
      } else if (Number.isNaN(Number.parseInt(number))) {
        const exercises2 = exercises.filter((exercise) =>
          exercise.exerciseNumber.toLowerCase().includes(number.toLowerCase()),
        )
        if (exercises2.length === 0) {
          return { kind: 'message', message: t('message.unexistingExercise1', { number }) }
        } else {
          return { kind: 'exercises', exercises: exercises2 }
        }
      } else {
        const exercise = exercises.find((exercise) => exercise.exerciseNumber === number)
        if (exercise === undefined) {
          return { kind: 'message', message: t('message.unexistingExercise2', { number }) }
        } else {
          return { kind: 'exercises', exercises: [exercise] }
        }
      }
    })
    .exhaustive()
})
</script>

<template>
  <p class="title">{{ t('title') }} {{ data.title }}</p>
  <p>
    {{ t('pageNumberFilter') }} <wbr /><TriColoredInput
      :digitsOnly="true"
      v-model="pageNumberFilter"
      data-cy="page-number-filter"
    />
  </p>
  <p>
    {{ t('exerciseNumberFilter') }} <wbr /><TriColoredInput
      :digitsOnly="false"
      v-model="exerciseNumberFilter"
      data-cy="exercise-number-filter"
    />
  </p>
  <p>
    <VirtualNumericalKeyboard />
    <WhiteSpace />
    <VirtualEraser />
  </p>

  <template v-if="filtered.kind === 'nothing'"></template>
  <p class="message" v-else-if="filtered.kind === 'message'">{{ filtered.message }}</p>
  <template v-else-if="filtered.kind === 'exercises'">
    <TextbookExportExercisesList :exercises="filtered.exercises" />
  </template>
  <template v-else>{{ ((status: never) => status)(filtered) }}</template>
</template>

<style scoped>
*,
:deep(*) {
  font-family: Arial, sans-serif;
  font-size: 32px;
  word-spacing: 0.26em;
  white-space-collapse: preserve;
}

.title {
  font-weight: bold;
  text-align: center;
}

.message {
  color: red;
  font-weight: bold;
}
</style>

<i18n>
fr:
  title: 'Livre :'
  pageNumberFilter: 'Quelle page ?'
  exerciseNumberFilter: 'Quel exercice ?'
  message:
    noPage: Indique le numéro de la page.
    unexistingPage: La page {page} n'existe pas.
    unexistingExercise1: L'exercice {number} n'existe pas.
    unexistingExercise2: L'exercice numéro {number} n'existe pas.
</i18n>
