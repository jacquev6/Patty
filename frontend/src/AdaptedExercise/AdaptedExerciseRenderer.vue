<script lang="ts">
import type { AdaptedExercise, AnyComponent } from '@/apiClient'
import { isPassive } from './dispatch/PassiveSingleComponent.vue'

export type InProgressExercise = {
  exercise: AdaptedExercise
  selectedSwappable: {
    pageIndex: number
    lineIndex: number
    componentIndex: number
    contentsFrom: {
      pageIndex: number
      lineIndex: number
      componentIndex: number
    }
  } | null
}

export type ComponentAnswer =
  | {
      kind: 'multipleChoicesInput'
      choice: number | null
    }
  | {
      kind: 'freeTextInput'
      text: string
    }
  | {
      kind: 'selectableInput'
      color: number
    }
  | {
      kind: 'swappableInput'
      contentsFrom: {
        pageIndex: number
        lineIndex: number
        componentIndex: number
      }
    }
  | {
      kind: 'editableTextInput'
      text: string
    }

type LineAnswers = {
  components: Partial<Record<number, ComponentAnswer>>
}

type PageAnswers = {
  lines: Partial<Record<number, LineAnswers>>
}

export type StudentAnswers = {
  pages: Partial<Record<number, PageAnswers>>
}
</script>

<script setup lang="ts">
import { computed, nextTick, provide, reactive, ref, useTemplateRef, watch } from 'vue'
import { useStorage } from '@vueuse/core'

import AnySequenceComponent from './dispatch/AnySequenceComponent.vue'
import PageNavigationControls from './PageNavigationControls.vue'
import TriColorLines from './TriColorLines.vue'
import PassiveSequenceComponent from './dispatch/PassiveSequenceComponent.vue'

const props = withDefaults(
  defineProps<{
    studentAnswersStorageKey?: string | null
    adaptedExercise: AdaptedExercise
  }>(),
  { studentAnswersStorageKey: null },
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

const inProgress = reactive<InProgressExercise>({
  exercise: props.adaptedExercise,
  selectedSwappable: null,
})
watch(
  () => props.adaptedExercise,
  (exercise) => {
    inProgress.exercise = exercise
    inProgress.selectedSwappable = null
  },
)
watch(pageIndex, () => {
  inProgress.selectedSwappable = null
})

const defaultStudentAnswers = { pages: {} }

const studentAnswers =
  props.studentAnswersStorageKey === null
    ? ref(defaultStudentAnswers)
    : useStorage(`patty/student-answers/v2/exercise-${props.studentAnswersStorageKey}`, defaultStudentAnswers)

const triColorLines = useTemplateRef('tricolor')
watch(
  studentAnswers,
  async () => {
    await nextTick()
    if (triColorLines.value !== null) {
      triColorLines.value.recolor()
    }
  },
  { deep: true },
)

type StatementLine = {
  lineIndex: number
  contents: AnyComponent[]
}

const statementLines = computed<StatementLine[]>(() => {
  const lines: StatementLine[] = []

  for (const [lineIndex, { contents }] of props.adaptedExercise.statement.pages[pageIndex.value].lines.entries()) {
    lines.push({ lineIndex, contents })
    for (const component of contents) {
      if (
        isPassive(component) ||
        component.kind === 'swappableInput' ||
        component.kind === 'selectableInput' ||
        component.kind === 'multipleChoicesInput' ||
        component.kind === 'freeTextInput'
      ) {
        // Nothing to do
      } else if (component.kind === 'editableTextInput') {
        lines.push({
          lineIndex,
          contents: [
            { kind: 'arrow' },
            { kind: 'whitespace' },
            { kind: 'activeEditableTextInput', contents: component.contents },
          ],
        })
      } else {
        ;((component: never) => console.log(`Unexpected component: ${component}`))(component)
      }
    }
  }

  return lines
})
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
            <p v-for="{ lineIndex, contents } in statementLines">
              <AnySequenceComponent
                :pageIndex
                :lineIndex
                :contents
                :tricolorable="true"
                v-model="studentAnswers"
                v-model:inProgress="inProgress"
              />
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
