<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { match, P } from 'ts-pattern'
import { useI18n } from 'vue-i18n'

import TextbookExportExercisesList from './ExercisesList.vue'
import TriColoredInput from './TriColoredInput.vue'
import VirtualNumericalKeyboard from './VirtualNumericalKeyboard.vue'
import VirtualEraser from './VirtualEraser.vue'
import WhiteSpace from '$/WhiteSpace.vue'
import type { Data, Exercise, Lesson } from './RootView.vue'
import assert from '$/assert'
import { useDisplayPreferences } from './displayPreferences'

const props = defineProps<{
  data: Data
}>()

const { t } = useI18n()

const pageNumberFilter = ref<string>('')

const pageNumberInput = useTemplateRef('pageNumberInput')

type Filtered =
  | { kind: 'nothing' }
  | { kind: 'noSuchPage' }
  | { kind: 'exercises'; lessons: Lesson[]; exercises: Exercise[] }

const filtered = computed(() => {
  return match(pageNumberFilter.value)
    .returnType<Filtered>()
    .with('', () => ({ kind: 'nothing' }))
    .with(P.string, (pageString) => {
      const page = parseInt(pageString, 10)
      const lessons = props.data.lessons.filter((lesson) => lesson.pageNumber === page)
      const exercises = props.data.exercises.filter((exercise) => exercise.pageNumber === page)
      if (lessons.length === 0 && exercises.length === 0) {
        return { kind: 'noSuchPage' }
      } else {
        return { kind: 'exercises', lessons, exercises }
      }
    })
    .exhaustive()
})

const { tricolored } = useDisplayPreferences()

const tricoloredProxy = computed<'true' | 'false'>({
  get: () => (tricolored.value ? 'true' : 'false'),
  set: (value: string) => {
    tricolored.value = value === 'true'
  },
})

onMounted(() => {
  assert(pageNumberInput.value !== null)
  pageNumberInput.value.$el.focus()
})
</script>

<template>
  <div class="container">
    <p class="title">{{ data.title }}</p>
    <p>
      <label><input type="radio" value="false" v-model="tricoloredProxy" /> {{ t('textInBlack') }}</label>
    </p>
    <p>
      <label><input type="radio" value="true" v-model="tricoloredProxy" /> {{ t('linesInColor') }}</label>
    </p>
    <p>
      {{ t('pageNumberFilter') }} <wbr /><TriColoredInput
        ref="pageNumberInput"
        :digitsOnly="true"
        v-model="pageNumberFilter"
        data-cy="page-number-filter"
      />
    </p>
    <p>
      <VirtualNumericalKeyboard />
      <WhiteSpace />
      <VirtualEraser />
    </p>

    <template v-if="filtered.kind === 'nothing'"></template>
    <p class="message" v-else-if="filtered.kind === 'noSuchPage'">{{ t('noSuchPage', { page: pageNumberFilter }) }}</p>
    <template v-else-if="filtered.kind === 'exercises'">
      <TextbookExportExercisesList :lessons="filtered.lessons" :exercises="filtered.exercises" />
    </template>
    <template v-else>{{ ((status: never) => status)(filtered) }}</template>
  </div>
</template>

<style scoped>
*,
:deep(*) {
  font-family: Arial, sans-serif;
  font-size: 32px;
  word-spacing: 0.26em;
  white-space-collapse: preserve;
}

.container {
  margin-left: 0.5em;
  margin-right: 0.5em;
}

.title {
  font-weight: bold;
  text-align: center;
}

.message {
  color: red;
}
</style>

<i18n>
fr:
  pageNumberFilter: 'Numéro de page :'
  noSuchPage: La page {page} n'existe pas.
  textInBlack: "Texte en noir"
  linesInColor: "Lignes en couleur"
</i18n>
