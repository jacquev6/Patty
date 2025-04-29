<script setup lang="ts">
import { ref, watch } from 'vue'
import jsonStringify from 'json-stringify-pretty-compact'
import { useMagicKeys } from '@vueuse/core'

import type { AdaptedExercise } from '@/apiClient'
import MiniatureScreen from './MiniatureScreen.vue'
import AdaptedExerciseRenderer from './AdaptedExercise/AdaptedExerciseRenderer.vue'
import FixedColumns from './FixedColumns.vue'

type Example = {
  title: string
  exercise: AdaptedExercise
}

const examples: Example[] = [
  {
    title: 'Edit sentence',
    exercise: {
      format: 'v1',
      instruction: {
        lines: [
          {
            contents: [
              { kind: 'text', text: 'Recopie' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'chaque' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'phrase' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'en' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'rétablissant' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'la' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'ponctuation' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'comme' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'dans' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'l' },
              { kind: 'text', text: "'" },
              { kind: 'text', text: 'exemple' },
              { kind: 'text', text: '.' },
            ],
          },
        ],
      },
      example: {
        lines: [
          {
            contents: [
              { kind: 'text', text: 'la' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'nuit' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'dans' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'le' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'ciel' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'les' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'étoiles' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'brillent' },
            ],
          },
          {
            contents: [
              { kind: 'arrow' },
              { kind: 'text', text: 'La' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'nuit' },
              { kind: 'text', text: ',' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'dans' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'le' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'ciel' },
              { kind: 'text', text: ',' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'les' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'étoiles' },
              { kind: 'whitespace' },
              { kind: 'text', text: 'brillent' },
              { kind: 'text', text: '.' },
            ],
          },
        ],
      },
      hint: null,
      statement: {
        pages: [
          {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'a' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  {
                    kind: 'editableTextInput',
                    contents: [
                      { kind: 'text', text: 'souvent' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'dans' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'le' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'noir' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'j' },
                      { kind: 'text', text: "'" },
                      { kind: 'text', text: 'ai' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'peur' },
                    ],
                  },
                ],
              },
            ],
          },
          {
            lines: [
              {
                contents: [
                  { kind: 'text', text: 'b' },
                  { kind: 'text', text: '.' },
                  { kind: 'whitespace' },
                  {
                    kind: 'editableTextInput',
                    contents: [
                      { kind: 'text', text: 'parfois' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'en' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'plein' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'jour' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'j' },
                      { kind: 'text', text: "'" },
                      { kind: 'text', text: 'ai' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'peur' },
                      { kind: 'whitespace' },
                      { kind: 'text', text: 'aussi' },
                    ],
                  },
                ],
              },
            ],
          },
        ],
      },
      reference: null,
    },
  },
]

const fullScreenIndex = ref<number | null>(null)
const { Escape } = useMagicKeys()

watch(Escape, () => {
  fullScreenIndex.value = null
})
</script>

<template>
  <div style="padding-left: 5px; padding-right: 5px">
    <template v-for="(example, exampleIndex) in examples" :key="example.title">
      <h1>{{ example.title }}</h1>
      <FixedColumns :columns="[1, 1]">
        <template #col-1>
          <pre>{{ jsonStringify(example.exercise) }}</pre>
        </template>
        <template #col-2>
          <MiniatureScreen :fullScreen="fullScreenIndex === exampleIndex">
            <AdaptedExerciseRenderer
              :navigateUsingArrowKeys="fullScreenIndex === exampleIndex"
              :adaptedExercise="example.exercise"
            />
            <button v-if="fullScreenIndex === exampleIndex" class="exitFullScreen" @click="fullScreenIndex = null">
              Exit full screen (Esc)
            </button>
          </MiniatureScreen>
          <button @click="fullScreenIndex = exampleIndex">Full screen</button>
        </template>
      </FixedColumns>
    </template>
  </div>
</template>

<style scoped>
button.exitFullScreen {
  position: absolute;
  left: 50%;
  transform: translate(-50%, 0);
  bottom: 2rem;
}
</style>
