<script setup lang="ts">
import { computed, nextTick, provide, reactive, ref, useTemplateRef, watch } from 'vue'

import type { AdaptedExercise } from '@/apiClient'
import LineComponent from './components/LineComponent.vue'
import PageNavigationControls from './PageNavigationControls.vue'
import TriColorLines from './TriColorLines.vue'

const props = defineProps<{
  adaptedExercise: AdaptedExercise
}>()

provide('adaptedExerciseTeleportBackdropTo', useTemplateRef('container'))

const statementPagesCount = computed(() => {
  return Math.max(1, props.adaptedExercise.statement.pages.length)
})

const totalPagesCount = computed(() => {
  if (props.adaptedExercise.reference === null) {
    return statementPagesCount.value
  } else {
    return statementPagesCount.value + 1
  }
})
const page = ref(0)

const model = reactive<Record<number, Record<number, Record<number, string | number>>>>({})
watch(
  () => props.adaptedExercise,
  (adaptedExercise) => {
    for (const key of Object.keys(model)) {
      delete model[key as unknown as number]
    }
    for (let pageIndex = 0; pageIndex < adaptedExercise.statement.pages.length; pageIndex++) {
      model[pageIndex] = {}
      for (let lineIndex = 0; lineIndex < adaptedExercise.statement.pages[pageIndex].lines.length; lineIndex++) {
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
    await nextTick()
    if (triColorLines.value !== null) {
      triColorLines.value.recolor()
    }
  },
  { deep: true },
)
</script>

<template>
  <PageNavigationControls :pagesCount="totalPagesCount" v-model="page">
    <div ref="container" class="container">
      <template v-if="page < statementPagesCount">
        <div class="instruction">
          <p v-for="{ contents } in adaptedExercise.instruction.lines">
            <LineComponent :contents :tricolorable="false" />
          </p>
        </div>
        <div class="statement" v-if="page < props.adaptedExercise.statement.pages.length">
          <TriColorLines ref="tricolor">
            <p v-for="({ contents }, lineIndex) in adaptedExercise.statement.pages[page].lines">
              <LineComponent :contents :tricolorable="true" v-model="model[page][lineIndex]" />
            </p>
          </TriColorLines>
        </div>
      </template>
      <template v-else-if="adaptedExercise.reference !== null">
        <LineComponent :contents="adaptedExercise.reference.contents" :tricolorable="false" />
      </template>
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

.instruction {
  text-align: center;
}

.instruction :deep(p:first-child) {
  margin-top: 11px;
}

.statement {
  padding: 27px 6px;
}

.statement :deep(*:first-child) {
  margin-top: 0;
}
</style>
