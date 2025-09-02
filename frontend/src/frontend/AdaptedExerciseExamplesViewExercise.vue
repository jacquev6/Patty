<script setup lang="ts">
import { ref, watch } from 'vue'
import jsonStringify from 'json-stringify-pretty-compact'
import { useMagicKeys } from '@vueuse/core'
import { useI18n } from 'vue-i18n'

import type { AdaptedExercise } from './ApiClient'
import MiniatureScreen from '$/MiniatureScreen.vue'
import AdaptedExerciseRenderer, { type SpacingVariables } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import FixedColumns from '$/FixedColumns.vue'

export type Example = {
  title: string
  exercise: AdaptedExercise
  demos?: Record<string, () => void>
}

const props = defineProps<{
  example: Example
  spacingVariables: SpacingVariables
}>()

const { t } = useI18n()

const jsonJustCopied = ref(false)
async function copyJsonAsText() {
  await navigator.clipboard.writeText(jsonStringify(props.example.exercise))
  jsonJustCopied.value = true
  await new Promise((resolve) => setTimeout(resolve, 1000))
  jsonJustCopied.value = false
}

const fullScreen = ref(false)
const { Escape } = useMagicKeys()

watch(Escape, () => {
  fullScreen.value = false
})
</script>

<template>
  <FixedColumns :columns="[1, 1]">
    <template #col-1>
      <h2>{{ example.title }}</h2>
      <p>
        <button @click="fullScreen = true">{{ t('fullScreen') }}</button>
      </p>
      <p>
        <button @click="copyJsonAsText()">{{ t('copyJson') }}</button> <template v-if="jsonJustCopied">✅</template>
      </p>
      <details>
        <summary>{{ t('seeJson') }}</summary>
        <pre>{{ jsonStringify(example.exercise) }}</pre>
      </details>
    </template>
    <template #col-2>
      <MiniatureScreen :fullScreen>
        <AdaptedExerciseRenderer
          :navigateUsingArrowKeys="fullScreen"
          :spacingVariables
          :adaptedExercise="example.exercise"
        />
        <button v-if="fullScreen" class="exitFullScreen" @click="fullScreen = false">{{ t('exitFullScreen') }}</button>
      </MiniatureScreen>
    </template>
  </FixedColumns>
</template>

<i18n>
en:
  fullScreen: Full screen
  copyJson: Copy JSON code 📋
  seeJson: See JSON code
  exitFullScreen: Exit full screen (Esc)
fr:
  fullScreen: Plein écran
  copyJson: Copier le code JSON 📋
  seeJson: Voir le code JSON
  exitFullScreen: Quitter le plein écran (Échap)
</i18n>

<style scoped>
h2 {
  margin-top: 0;
}

button.exitFullScreen {
  position: absolute;
  left: 50%;
  transform: translate(-50%, 0);
  bottom: 2rem;
}
</style>
