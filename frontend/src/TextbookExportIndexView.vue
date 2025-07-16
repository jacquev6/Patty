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

type Filtered = { kind: 'nothing' } | { kind: 'noSuchPage' } | { kind: 'exercises'; exercises: Exercise[] }

const filtered = computed(() => {
  return match(pageNumberFilter.value)
    .returnType<Filtered>()
    .with('', () => ({ kind: 'nothing' }))
    .with(P.string, (pageString) => {
      const page = parseInt(pageString, 10)
      const exercises = props.data.exercises.filter((exercise) => exercise.pageNumber === page)
      if (exercises.length === 0) {
        return { kind: 'noSuchPage' }
      } else {
        return { kind: 'exercises', exercises }
      }
    })
    .exhaustive()
})
</script>

<template>
  <p class="title">{{ data.title }}</p>
  <p>
    {{ t('pageNumberFilter') }} <wbr /><TriColoredInput
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
}
</style>

<i18n>
fr:
  pageNumberFilter: 'Numéro de page :'
  exerciseNumberFilter: 'Quel exercice ?'
  noSuchPage: La page {page} n'existe pas.
</i18n>
