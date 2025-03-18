<script setup lang="ts">
import { computed, provide, reactive, ref, useTemplateRef, watch } from 'vue'

import type { AdaptedExercise } from '@/apiClient'
import LineComponent from './components/LineComponent.vue'
import PageNavigationControls from './PageNavigationControls.vue'

const props = defineProps<{
  adaptedExercise: AdaptedExercise
}>()

provide('adaptedExerciseTeleportBackdropTo', useTemplateRef('container'))

const pagesCount = computed(() => props.adaptedExercise.wording.pages.length)
const page = ref(0)

const model = reactive<Record<number, Record<number, Record<number, string | number>>>>({})
watch(
  () => props.adaptedExercise,
  (adaptedExercise) => {
    for (const key of Object.keys(model)) {
      delete model[key as unknown as number]
    }
    for (let pageIndex = 0; pageIndex < adaptedExercise.wording.pages.length; pageIndex++) {
      model[pageIndex] = {}
      for (let lineIndex = 0; lineIndex < adaptedExercise.wording.pages[pageIndex].lines.length; lineIndex++) {
        model[pageIndex][lineIndex] = {}
      }
    }
  },
  { immediate: true },
)
</script>

<template>
  <div ref="container">
    <PageNavigationControls :pagesCount v-model="page">
      <p v-for="{ contents } in adaptedExercise.instructions.lines">
        <LineComponent :contents />
      </p>
      <p v-for="({ contents }, lineIndex) in adaptedExercise.wording.pages[page].lines">
        <LineComponent :contents v-model="model[page][lineIndex]" />
      </p>
    </PageNavigationControls>
  </div>
</template>

<style scoped>
div {
  height: 100%;
  overflow: hidden;
}
</style>
