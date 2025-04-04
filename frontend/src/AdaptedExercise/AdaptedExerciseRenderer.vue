<script setup lang="ts">
import { computed, nextTick, provide, reactive, ref, useTemplateRef, watch } from 'vue'

import type { AdaptedExercise } from '@/apiClient'
import assert from '@/assert'
import LineComponent from './components/LineComponent.vue'
import PageNavigationControls from './PageNavigationControls.vue'
import TriColorLines from './TriColorLines.vue'

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

const triColorLines = useTemplateRef('tricolor')
watch(
  model,
  async () => {
    assert(triColorLines.value !== null)
    await nextTick()
    triColorLines.value.recolor()
  },
  { deep: true },
)
</script>

<template>
  <PageNavigationControls :pagesCount v-model="page">
    <div ref="container" class="container">
      <div class="instructions">
        <p v-for="{ contents } in adaptedExercise.instructions.lines">
          <LineComponent :contents :tricolorable="false" />
        </p>
      </div>
      <div class="wording">
        <TriColorLines ref="tricolor">
          <template v-if="page < pagesCount">
            <p v-for="({ contents }, lineIndex) in adaptedExercise.wording.pages[page].lines">
              <LineComponent :contents :tricolorable="true" v-model="model[page][lineIndex]" />
            </p>
          </template>
        </TriColorLines>
      </div>
    </div>
  </PageNavigationControls>
</template>

<style scoped>
div {
  font-family: Arial, sans-serif;
  font-size: 32px;
}

.container {
  /* Ensure anything 'Teleport'ed to this element is rendered strictly within this element */
  overflow: hidden;
  transform: scale(1);
  height: 100%;
}

.instructions {
  text-align: center;
}

.instructions :deep(p:first-child) {
  margin-top: 11px;
}

.wording {
  padding: 27px 6px;
}

.wording :deep(*:first-child) {
  margin-top: 0;
}
</style>
