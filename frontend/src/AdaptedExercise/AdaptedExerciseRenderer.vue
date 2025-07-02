<script lang="ts">
import type { AdaptedExercise, AnyComponent } from '@/apiClient'

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

export const defaultSpacingVariables = () => ({
  '--extra-horizontal-space-between-words': 0.26,
  '--vertical-space-between-top-and-instruction': 0.35,
  '--vertical-space-between-instruction-lines': 2,
  '--vertical-space-between-instruction-and-statement': 2.15,
  '--vertical-space-between-statement-lines': 3.6,
  '--vertical-space-between-border-and-choices': 1.15,
  '--vertical-space-between-choices-lines': 3.05,
})

export type SpacingVariables = ReturnType<typeof defaultSpacingVariables>
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
    navigateUsingArrowKeys: boolean
    studentAnswersStorageKey?: string | null
    adaptedExercise: AdaptedExercise
    spacingVariables?: SpacingVariables
  }>(),
  { studentAnswersStorageKey: null, spacingVariables: defaultSpacingVariables },
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

const inProgress = ref(
  reactive<InProgressExercise>({
    exercise: props.adaptedExercise,
    selectedSwappable: null,
  }),
)
watch(
  () => props.adaptedExercise,
  (exercise) => {
    inProgress.value.exercise = exercise
    inProgress.value.selectedSwappable = null
  },
)
watch(pageIndex, () => {
  inProgress.value.selectedSwappable = null
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
      if (component.kind === 'editableTextInput' && component.showOriginalText) {
        lines.push({
          lineIndex,
          contents: [
            { kind: 'arrow' },
            { kind: 'whitespace' },
            { kind: 'editableTextInput', showOriginalText: false, contents: component.contents },
          ],
        })
      }
    }
  }

  return lines
})

const spacingVariables = computed(() =>
  Object.fromEntries(Object.entries(props.spacingVariables).map(([key, value]) => [key, `${value}em`])),
)
</script>

<template>
  <PageNavigationControls :navigateUsingArrowKeys :pagesCount="totalPagesCount" v-model="pageIndex">
    <div ref="container" class="container" spellcheck="false" :style="spacingVariables">
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
        <p>
          <PassiveSequenceComponent :contents="adaptedExercise.reference.contents" :tricolorable="false" />
        </p>
      </template>
    </div>
  </PageNavigationControls>
</template>

<style scoped>
div.container {
  font-family: Arial, sans-serif;
  font-size: 32px;
  white-space-collapse: preserve;
  word-spacing: var(--extra-horizontal-space-between-words);
  padding-left: 6px;
  padding-right: 6px;
  /* Ensure anything 'Teleport'ed to this element is rendered strictly within this element */
  overflow-x: hidden;
  overflow-y: auto;
  transform: scale(1);
  height: 100%;
}

:deep(*) {
  margin: 0;
  padding: 0;
}

.instruction {
  text-align: center;
  margin-top: calc(
    var(--vertical-space-between-top-and-instruction) - (var(--vertical-space-between-instruction-lines) - 1em) / 2
  );
  line-height: var(--vertical-space-between-instruction-lines);
}

.statement {
  margin-top: calc(
    var(--vertical-space-between-instruction-and-statement) -
      (var(--vertical-space-between-instruction-lines) - 1em + var(--vertical-space-between-statement-lines) - 1em) / 2
  );
  line-height: var(--vertical-space-between-statement-lines);
}
</style>
