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
import InputForNumberOrNull from './InputForNumberOrNull.vue'
import InputForNonEmptyStringOrNull from './InputForNonEmptyStringOrNull.vue'
import TextbookExportExercisesList from './TextbookExportExercisesList.vue'
import assert from './assert'

const data = JSON.parse('##TO_BE_SUBSTITUTED_TEXTBOOK_EXPORT_DATA##') as Data // @todo Factorize with TextbookExportExerciseView.vue

const pageNumberFilter = ref<number | null>(null)
const exerciseNumberFilter = ref<string | null>(null)

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
    .with([null, null], () => ({ kind: 'nothing' }))
    .with([null, P.nonNullable], () => {
      return { kind: 'message', message: 'Indique le numéro de la page.' }
    })
    .with([P.nonNullable, P.any], ([page, number]) => {
      const exercises = filterableExercises.filter((exercise) => exercise.pageNumber === page)
      if (exercises.length === 0) {
        return { kind: 'message', message: `La page ${page} n'existe pas.` }
      } else if (number === null) {
        return { kind: 'exercises', exercises }
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
  <p>Quelle page ? <InputForNumberOrNull v-model="pageNumberFilter" data-cy="page-number-filter" /></p>
  <p>
    Quelle exercice ? <InputForNonEmptyStringOrNull v-model="exerciseNumberFilter" data-cy="exercise-number-filter" />
  </p>

  <template v-if="filtered.kind === 'nothing'"></template>
  <p class="message" v-else-if="filtered.kind === 'message'">{{ filtered.message }}</p>
  <template v-else-if="filtered.kind === 'exercises'">
    <TextbookExportExercisesList :exercises="filtered.exercises" />
  </template>
  <template v-else>{{ ((status: never) => status)(filtered) }}</template>
</template>

<style scoped>
.title {
  font-size: 150%;
  font-weight: bold;
  text-align: center;
}

.message {
  color: red;
  font-weight: bold;
}
</style>
