<script setup lang="ts">
import { computed, ref } from 'vue'
import _ from 'lodash'

import PageNavigationControls from './AdaptedExercise/PageNavigationControls.vue'
import type { Exercise as FullExercise } from './TextbookExportIndexView.vue'
import { match, P } from 'ts-pattern'

type Exercise =
  | Pick<FullExercise & { kind: 'adapted' }, 'kind' | 'exerciseId' | 'exerciseNumber'>
  | (FullExercise & { kind: 'external' })

const props = defineProps<{
  exercises: Exercise[]
}>()

const pageIndex = ref(0)
const pagesCount = computed(() => Math.ceil(props.exercises.length / 4))

function hasExt(ext: string) {
  return (filename: string) => filename.endsWith(ext)
}

const columns = computed(() => {
  const columns: ((Exercise & { title: string }) | null)[][] = _.chunk(
    props.exercises.map((e) => {
      const prefix = Number.isNaN(Number.parseInt(e.exerciseNumber)) ? '' : 'Exercice '
      const suffix = match(e)
        .returnType<string>()
        .with({ kind: 'adapted' }, () => '')
        .with({ kind: 'external', originalFileName: P.select() }, (originalFileName) =>
          match(originalFileName)
            .returnType<string>()
            .with(P.string, hasExt('.pdf'), () => ` - PDF`)
            .with(P.string, hasExt('.docx'), () => ` - Word`)
            .with(P.string, hasExt('.odt'), () => ` - LibreOffice Writer`)
            .with(P.string, hasExt('.xlsx'), () => ` - Excel`)
            .with(P.string, hasExt('.ods'), () => ` - LibreOffice Calc`)
            .with(P.string, hasExt('.ggb'), () => ` - GeoGebra`)
            .otherwise(() => ' - Logiciel externe'),
        )
        .exhaustive()
      return { title: prefix + e.exerciseNumber + suffix, ...e }
    }),
    4,
  ).slice(pageIndex.value)
  const missing = 4 - columns[columns.length - 1]!.length
  for (let i = 0; i < missing; i++) {
    columns[columns.length - 1]!.push(null)
  }
  return columns
})

// Until https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Uint8Array/fromBase64
// is widely available:
function Uint8ArrayFromBase64(base64: string) {
  return Uint8Array.from(Array.from(atob(base64)).map((letter) => letter.charCodeAt(0)))
}

function openExternalExercise(exercise: Exercise & { kind: 'external' }) {
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([Uint8ArrayFromBase64(exercise.data)]))
  a.download = exercise.originalFileName
  a.click()
  URL.revokeObjectURL(a.href)
}
</script>

<template>
  <PageNavigationControls :navigateUsingArrowKeys="true" :pagesCount v-model="pageIndex">
    <div class="container">
      <div v-for="(column, columnIndex) in columns">
        <template v-for="exercise in column">
          <template v-if="exercise === null">
            <div class="exercise" style="visibility: hidden"><p>&nbsp;</p></div>
          </template>
          <template v-else-if="exercise.kind === 'adapted'">
            <RouterLink :to="{ name: 'exercise', params: { id: exercise.exerciseId } }" target="_blank">
              <div class="exercise" :class="`exercise${(pageIndex + columnIndex) % 3}`">
                <p>{{ exercise.title }}</p>
              </div>
            </RouterLink>
          </template>
          <template v-else-if="exercise.kind === 'external'">
            <a @click="openExternalExercise(exercise)">
              <div class="exercise" :class="`exercise${(pageIndex + columnIndex) % 3}`">
                <p>{{ exercise.title }}</p>
              </div>
            </a>
          </template>
          <template v-else>
            {{ ((e: never) => console.log('Unexpected exercise', e))(exercise) }}
          </template>
        </template>
      </div>
    </div>
  </PageNavigationControls>
</template>

<style scoped>
.container {
  overflow-x: hidden;
  display: flex;
}

p {
  margin: 0;
}

a {
  text-decoration: none;
  color: inherit;
}

.exercise {
  margin: 2px;
  padding: 0.7em 2em;
  border-width: 2px;
  border-style: solid;
  border-radius: 5px;
  cursor: pointer;
  text-wrap-mode: nowrap;
  border-color: var(--color);
  color: var(--color);
}

.exercise:hover {
  background-color: #ccc;
}

.exercise0 {
  --color: #00f;
}

.exercise1 {
  --color: #0c0;
}

.exercise2 {
  --color: #f00;
}
</style>
