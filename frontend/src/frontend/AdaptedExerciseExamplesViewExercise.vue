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
import { ref, watch } from 'vue'
import jsonStringify from 'json-stringify-pretty-compact'
import { useMagicKeys } from '@vueuse/core'
import { useI18n } from 'vue-i18n'

import type { Example } from './AdaptedExerciseExamples.ts'
import MiniatureScreen from '$/MiniatureScreen.vue'
import AdaptedExerciseRenderer, { type SpacingVariables } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import FixedColumns from '$/FixedColumns.vue'

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
      <p v-if="example.imagesUrls && Object.keys(example.imagesUrls).length !== 0">
        <template v-for="(imageUrl, imageIdentifier) in example.imagesUrls">
          <span style="display: inline-block; margin-right: 1em; margin-bottom: 1em; text-align: center">
            <img :src="imageUrl" style="max-height: 4em" />
            <br />
            {{ imageIdentifier }}
          </span>
        </template>
      </p>
      <p v-else>{{ t('noImages') }}</p>
    </template>
    <template #col-2>
      <MiniatureScreen :fullScreen>
        <AdaptedExerciseRenderer
          :navigateUsingArrowKeys="fullScreen"
          :spacingVariables
          :adaptedExercise="example.exercise"
          :imagesUrls="example.imagesUrls ?? {}"
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
  noImages: "No images"
  exitFullScreen: Exit full screen (Esc)
fr:
  fullScreen: Plein écran
  copyJson: Copier le code JSON 📋
  seeJson: Voir le code JSON
  noImages: "Pas d'images"
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
