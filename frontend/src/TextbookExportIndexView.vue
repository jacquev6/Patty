<script lang="ts">
export type Data = {
  title: string
  exercises: {
    exerciseId: string
    studentAnswersStorageKey: string
    pageNumber: number | null
    exerciseNumber: string | null
    adaptedExercise: AdaptedExercise
  }[]
}
</script>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { match, P } from 'ts-pattern'

import type { AdaptedExercise } from './apiClient'
import TextbookExportExercisesList from './TextbookExportExercisesList.vue'
import assert from './assert'
import TriColoredInput from './TriColoredInput.vue'
import VirtualNumericalKeyboard from './VirtualNumericalKeyboard.vue'
import VirtualEraser from './VirtualEraser.vue'
import WhiteSpace from './WhiteSpace.vue'

const data = JSON.parse('##TO_BE_SUBSTITUTED_TEXTBOOK_EXPORT_DATA##') as Data // @todo Factorize with TextbookExportExerciseView.vue

const pageNumberFilter = ref<string>('')
const exerciseNumberFilter = ref<string>('')

type FilterableExercise = {
  exerciseId: string
  pageNumber: number
  exerciseNumber: string
}

const filterableExercises = ((): FilterableExercise[] => {
  return data.exercises.map(({ exerciseId, pageNumber, exerciseNumber }) => {
    assert(pageNumber !== null)
    assert(exerciseNumber !== null)
    return {
      exerciseId,
      pageNumber,
      exerciseNumber,
    }
  })
})()

type Filtered =
  | { kind: 'nothing' }
  | { kind: 'message'; message: string }
  | { kind: 'exercises'; exercises: FilterableExercise[] }

const filtered = computed(() => {
  return match([pageNumberFilter.value, exerciseNumberFilter.value])
    .returnType<Filtered>()
    .with(['', ''], () => ({ kind: 'nothing' }))
    .with(['', P.string], () => {
      return { kind: 'message', message: 'Indique le numéro de la page.' }
    })
    .with([P.string, P.string], ([pageString, number]) => {
      const page = parseInt(pageString, 10)
      const exercises = filterableExercises.filter((exercise) => exercise.pageNumber === page)
      if (exercises.length === 0) {
        return { kind: 'message', message: `La page ${page} n'existe pas.` }
      } else if (number === '') {
        return { kind: 'exercises', exercises }
      } else if (Number.isNaN(Number.parseInt(number))) {
        const exercises2 = exercises.filter((exercise) =>
          exercise.exerciseNumber.toLowerCase().includes(number.toLowerCase()),
        )
        if (exercises2.length === 0) {
          return { kind: 'message', message: `L'exercice ${number} n'existe pas.` }
        } else {
          return { kind: 'exercises', exercises: exercises2 }
        }
      } else {
        const exercise = exercises.find((exercise) => exercise.exerciseNumber === number)
        if (exercise === undefined) {
          return { kind: 'message', message: `L'exercice numéro ${number} n'existe pas.` }
        } else {
          return { kind: 'exercises', exercises: [exercise] }
        }
      }
    })
    .exhaustive()
})
</script>

<template>
  <p class="title">Livre: {{ data.title }}</p>
  <p>
    Quelle page ? <wbr /><TriColoredInput :digitsOnly="true" v-model="pageNumberFilter" data-cy="page-number-filter" />
  </p>
  <p>
    Quel exercice ? <wbr /><TriColoredInput
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
