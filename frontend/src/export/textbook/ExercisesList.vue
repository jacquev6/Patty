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
import { computed } from 'vue'
import _ from 'lodash'

import HorizontalScrollingControls from '@/adapted-exercise/HorizontalScrollingControls.vue'
import type { Exercise as FullExercise, Lesson } from './RootView.vue'
import { match, P } from 'ts-pattern'
import { useI18n } from 'vue-i18n'

type Exercise =
  | Pick<FullExercise & { kind: 'adapted' }, 'kind' | 'exerciseId' | 'exerciseNumber'>
  | (FullExercise & { kind: 'external' })

const props = defineProps<{
  exercises: Exercise[]
  lessons: Lesson[]
}>()

const { t } = useI18n()

function hasExt(ext: string) {
  return (filename: string) => filename.endsWith(ext)
}

const columns = computed(() => {
  const columns: (Lesson | Exercise | null)[][] = _.chunk([...props.lessons, ...props.exercises], 4)
  const missing = 4 - columns[columns.length - 1]!.length
  for (let i = 0; i < missing; i++) {
    columns[columns.length - 1]!.push(null)
  }
  return columns
})

function makeExerciseTitle(exercise: Exercise) {
  const prefix = Number.isNaN(Number.parseInt(exercise.exerciseNumber)) ? '' : 'Exercice '
  return match(exercise)
    .with({ kind: 'adapted' }, () => prefix + exercise.exerciseNumber)
    .with({ kind: 'external', originalFileName: P.select() }, (originalFileName) => {
      const suffix = match(originalFileName)
        .with(P.string, hasExt('.pdf'), () => 'PDF')
        .with(P.string, hasExt('.docx'), () => 'Word')
        .with(P.string, hasExt('.odt'), () => 'LibreOffice Writer')
        .with(P.string, hasExt('.xlsx'), () => 'Excel')
        .with(P.string, hasExt('.ods'), () => 'LibreOffice Calc')
        .with(P.string, hasExt('.ggb'), () => 'GeoGebra')
        .otherwise(() => 'Logiciel externe')
      return `${prefix}${exercise.exerciseNumber} - ${suffix}`
    })
    .exhaustive()
}

function makeLessonSuffix(lesson: Lesson) {
  return match(lesson.originalFileName)
    .with(P.string, hasExt('.pdf'), () => 'PDF')
    .with(P.string, hasExt('.docx'), () => 'Word')
    .with(P.string, hasExt('.odt'), () => 'LibreOffice Writer')
    .otherwise(() => 'Logiciel externe')
}

// Until https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Uint8Array/fromBase64
// is widely available:
function Uint8ArrayFromBase64(base64: string) {
  return Uint8Array.from(Array.from(atob(base64)).map((letter) => letter.charCodeAt(0)))
}

function openData(subject: { data: string; originalFileName: string }) {
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([Uint8ArrayFromBase64(subject.data)]))
  a.download = subject.originalFileName
  a.click()
  URL.revokeObjectURL(a.href)
}
</script>

<template>
  <HorizontalScrollingControls :navigateUsingArrowKeys="true" :scrollBy="250">
    <div class="container">
      <div v-for="(column, columnIndex) in columns">
        <template v-for="row in column">
          <template v-if="row === null">
            <div class="exercise" style="visibility: hidden"><p>&nbsp;</p></div>
          </template>
          <template v-else-if="row.kind === 'adapted'">
            <RouterLink
              :to="{ name: 'exercise', params: { id: row.exerciseId }, query: { closable: 'true' } }"
              target="_blank"
            >
              <div class="exercise" :class="`exercise${columnIndex % 3}`">
                <p>{{ makeExerciseTitle(row) }}</p>
              </div>
            </RouterLink>
          </template>
          <template v-else-if="row.kind === 'external'">
            <a @click="openData(row)">
              <div class="exercise" :class="`exercise${columnIndex % 3}`">
                <p>{{ makeExerciseTitle(row) }}</p>
              </div>
            </a>
          </template>
          <template v-else-if="'data' in row">
            <a @click="openData(row)">
              <div class="exercise" :class="`exercise${columnIndex % 3}`">
                <p>{{ t('lesson') }} - {{ makeLessonSuffix(row) }}</p>
              </div>
            </a>
          </template>
          <template v-else>
            {{ ((e: never) => console.log('Unexpected exercise', e))(row) }}
          </template>
        </template>
      </div>
    </div>
  </HorizontalScrollingControls>
</template>

<style scoped>
.container {
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
  margin: 2px 8px;
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

<i18n>
fr:
  lesson: Leçon
</i18n>
