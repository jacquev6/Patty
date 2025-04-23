<script setup lang="ts">
import { computed, nextTick, provide, ref, useTemplateRef, watch } from 'vue'
import { useStorage } from '@vueuse/core'

import type { AdaptedExercise } from '@/apiClient'
import AnySequenceComponent from './dispatch/AnySequenceComponent.vue'
import PageNavigationControls from './PageNavigationControls.vue'
import TriColorLines from './TriColorLines.vue'
import PassiveSequenceComponent from './dispatch/PassiveSequenceComponent.vue'

const props = withDefaults(
  defineProps<{
    exerciseId?: string | null
    adaptedExercise: AdaptedExercise
  }>(),
  { exerciseId: null },
)

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
const pageIndex = ref(0)

const defaultModel = computed(() => {
  const model: Record<number, Record<number, Record<number, undefined | string | number | null | boolean>>> = {}
  for (let pageIndex = 0; pageIndex < props.adaptedExercise.statement.pages.length; pageIndex++) {
    model[pageIndex] = {}
    for (let lineIndex = 0; lineIndex < props.adaptedExercise.statement.pages[pageIndex].lines.length; lineIndex++) {
      model[pageIndex][lineIndex] = {}
    }
  }
  return model
})

const model =
  props.exerciseId === null
    ? ref(defaultModel.value)
    : useStorage(`patty/student-answers/v1/exercise-${props.exerciseId}`, defaultModel.value)

watch(defaultModel, (m) => {
  model.value = m
})

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
  <PageNavigationControls :pagesCount="totalPagesCount" v-model="pageIndex">
    <div ref="container" class="container">
      <template v-if="pageIndex < statementPagesCount">
        <div class="instruction">
          <p v-for="{ contents } in adaptedExercise.instruction.lines">
            <PassiveSequenceComponent :contents :tricolorable="false" />
          </p>
          <template v-if="adaptedExercise.example !== null">
            <p v-for="{ contents } in adaptedExercise.example.lines">
              <PassiveSequenceComponent :contents :tricolorable="false" />
            </p>
          </template>
          <template v-if="adaptedExercise.hint !== null">
            <p v-for="{ contents } in adaptedExercise.hint.lines">
              <PassiveSequenceComponent :contents :tricolorable="false" />
            </p>
          </template>
        </div>
        <div class="statement" v-if="pageIndex < props.adaptedExercise.statement.pages.length">
          <TriColorLines ref="tricolor">
            <p v-for="({ contents }, lineIndex) in adaptedExercise.statement.pages[pageIndex].lines">
              <AnySequenceComponent :contents :tricolorable="true" v-model="model[pageIndex][lineIndex]" />
            </p>
          </TriColorLines>
        </div>
      </template>
      <template v-else-if="adaptedExercise.reference !== null">
        <PassiveSequenceComponent :contents="adaptedExercise.reference.contents" :tricolorable="false" />
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
