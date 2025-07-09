<script lang="ts">
import type {
  AdaptedExercise,
  AnyExerciseComponent,
  FormattedTextExerciseComponent,
  PassiveExerciseComponent,
} from '@/apiClient'
import { match, P } from 'ts-pattern'
import deepEqual from 'deep-equal'

export type InProgressExercise = {
  exercise: RenderableExercise
  p:
    | {
        kind: 'none'
      }
    | {
        kind: 'movingSwappable'
        swappable: {
          pageIndex: number
          lineIndex: number
          componentIndex: number
          contentsFrom: {
            pageIndex: number
            lineIndex: number
            componentIndex: number
          }
        }
      }
    | {
        kind: 'solvingSelectableLetters'
        selectable: {
          pageIndex: number
          lineIndex: number
          componentIndex: number
        }
      }
    | {
        kind: 'solvingMultipleChoices'
        multipleChoices: {
          pageIndex: number
          lineIndex: number
          componentIndex: number
        }
      }
}

export type ComponentAnswer =
  | {
      kind: 'choice'
      choice: number | null
    }
  | {
      kind: 'text'
      text: string
    }
  | {
      kind: 'selectable'
      color: number
    }
  | {
      kind: 'swappable'
      contentsFrom: {
        pageIndex: number
        lineIndex: number
        componentIndex: number
      }
    }
  | {
      kind: 'highlights'
      highlights: number[]
    }

type LineAnswers = {
  components: Partial<Record<number, ComponentAnswer>>
}

type PageAnswers = {
  lines: Partial<Record<number, LineAnswers>>
}

export type StudentAnswers = {
  pages: Partial<Record<number, PageAnswers>>
  // @todo Factorize accessors. Probably using a Pinia store.
}

export const defaultSpacingVariables = () => ({
  '--extra-horizontal-space-between-words': 0.26,
  '--optional-extra-horizontal-space-between-letters-in-editable-text-input': 0.2,
  '--vertical-space-between-top-and-instruction': 0.35,
  '--vertical-space-between-instruction-lines': 2,
  '--vertical-space-between-instruction-and-statement': 2.15,
  '--vertical-space-between-statement-lines': 3.6,
  '--vertical-space-between-border-and-choices': 1.15,
  '--vertical-space-between-choices-lines': 3.05,
})

export type SpacingVariables = ReturnType<typeof defaultSpacingVariables>

type TextRenderable = {
  kind: 'text'
  text: string
}

type WhitespaceRenderable = {
  kind: 'whitespace'
}

export type PlainTextRenderable = TextRenderable | WhitespaceRenderable

type FormattedRenderable = {
  kind: 'formatted'
  contents: PassiveRenderable[]
  bold: boolean
  italic: boolean
  underlined: boolean
  highlighted: string | null
  boxed: boolean
  superscript: boolean
  subscript: boolean
}

export type PassiveRenderable = PlainTextRenderable | FormattedRenderable

type TextInputRenderable = {
  kind: 'textInput'
  initialText: string
  increaseHorizontalSpace: boolean
}

type MultipleChoicesInputRenderable = {
  kind: 'multipleChoicesInput'
  choices: {
    contents: PassiveRenderable[]
  }[]
  showChoicesByDefault: boolean
}

type SelectableInputRenderable = {
  kind: 'selectableInput'
  contents: PassiveRenderable[]
  colors: string[]
  boxed: boolean
}

type SelectableLettersInputRenderable = {
  kind: 'selectableLettersInput'
  contents: string
  colors: string[]
  boxed: boolean
}

type SwappableInputRenderable = {
  kind: 'swappableInput'
  contents: PassiveRenderable[]
}

type ActiveRenderable =
  | TextInputRenderable
  | MultipleChoicesInputRenderable
  | SelectableInputRenderable
  | SelectableLettersInputRenderable
  | SwappableInputRenderable

export type AnyRenderable = PassiveRenderable | ActiveRenderable

type StatementLine = {
  contents: AnyRenderable[]
  alone: boolean
}

type StatementRenderablePage = {
  kind: 'statement'
  instruction: { contents: PassiveRenderable[] }[]
  statement: StatementLine[]
}

type ReferenceRenderablePage = {
  kind: 'reference'
  contents: PassiveRenderable[]
}

type RenderablePage = StatementRenderablePage | ReferenceRenderablePage

type RenderableExercise = {
  pages: RenderablePage[]
}

function makeRenderableFromFormattedTextExerciseComponent(
  component: FormattedTextExerciseComponent,
): PassiveRenderable[] {
  return match(component)
    .returnType<PassiveRenderable[]>()
    .with({ kind: 'whitespace' }, () => [{ kind: 'whitespace' }])
    .with({ kind: 'text' }, (c) => [{ kind: 'text', text: c.text }])
    .with({ kind: 'arrow' }, () => [{ kind: 'text', text: '→' }])
    .with({ kind: 'formatted' }, (c) => [
      {
        kind: 'formatted',
        contents: c.contents.flatMap(makeRenderableFromFormattedTextExerciseComponent),
        bold: c.bold ?? false,
        italic: c.italic ?? false,
        underlined: c.underlined ?? false,
        highlighted: c.highlighted ?? null,
        boxed: c.boxed ?? false,
        superscript: c.superscript ?? false,
        subscript: c.subscript ?? false,
      },
    ])
    .exhaustive()
}

function makeRenderableFromPassiveExerciseComponent(component: PassiveExerciseComponent): PassiveRenderable[] {
  return match(component)
    .returnType<PassiveRenderable[]>()
    .with({ kind: 'choice' }, (c) => [
      {
        kind: 'formatted',
        contents: c.contents.flatMap(makeRenderableFromFormattedTextExerciseComponent),
        bold: false,
        italic: false,
        underlined: false,
        highlighted: null,
        boxed: true,
        superscript: false,
        subscript: false,
      },
    ])
    .otherwise(makeRenderableFromFormattedTextExerciseComponent)
}

function makeRenderableFromAnyExerciseComponent(component: AnyExerciseComponent): AnyRenderable[] {
  return match(component)
    .returnType<AnyRenderable[]>()
    .with({ kind: 'freeTextInput' }, ({}) => [
      {
        kind: 'textInput',
        initialText: '',
        increaseHorizontalSpace: false,
      },
    ])
    .with({ kind: 'multipleChoicesInput' }, ({ choices, showChoicesByDefault }) => [
      {
        kind: 'multipleChoicesInput',
        choices: choices.map(({ contents }) => ({
          contents: contents.flatMap(makeRenderableFromFormattedTextExerciseComponent),
        })),
        showChoicesByDefault,
      },
    ])
    .with({ kind: 'selectableInput' }, ({ boxed, colors, contents }) => [
      {
        kind: 'selectableInput',
        boxed,
        colors,
        contents: contents.flatMap(makeRenderableFromPassiveExerciseComponent),
      },
    ])
    .with({ kind: 'swappableInput' }, ({ contents }) => [
      {
        kind: 'swappableInput',
        contents: contents.flatMap(makeRenderableFromFormattedTextExerciseComponent),
      },
    ])
    .with({ kind: 'editableTextInput', showOriginalText: true }, (c) => c.contents)
    .with({ kind: 'editableTextInput' }, (c) => [makeRenderableFromEditableTextInput(c)])
    .otherwise(makeRenderableFromPassiveExerciseComponent)
}

function makeRenderableFromEditableTextInput({
  contents,
  increaseHorizontalSpace,
}: AnyExerciseComponent & { kind: 'editableTextInput' }): AnyRenderable {
  return {
    kind: 'textInput',
    initialText: contents
      .map((c) =>
        match(c)
          .returnType<string>()
          .with({ kind: 'text', text: P.select() }, (text) => text)
          .with({ kind: 'whitespace' }, () => ' ')
          .exhaustive(),
      )
      .join(''),
    increaseHorizontalSpace: increaseHorizontalSpace ?? false,
  }
}

function regroupSelectableInputs(contents: AnyRenderable[]): AnyRenderable[] {
  const ret: AnyRenderable[] = []
  const group: SelectableInputRenderable[] = []

  function mustRegroup(content: SelectableInputRenderable): boolean {
    if (group.length !== 0) {
      if (content.boxed !== group[0].boxed) return false
      if (!deepEqual(content.colors, group[0].colors)) return false
    }
    if (content.contents.length !== 1) return false
    if (content.contents[0].kind !== 'text') return false
    if (content.contents[0].text.length !== 1) return false
    return true
  }

  function pushGroup(): void {
    if (group.length > 1) {
      ret.push({
        kind: 'selectableLettersInput',
        contents: group
          .flatMap((g) => g.contents)
          .map((c) => (c.kind === 'text' ? c.text : ''))
          .join(''),
        colors: group[0].colors,
        boxed: group[0].boxed,
      })
    } else if (group.length === 1) {
      ret.push(group[0])
    }
    group.splice(0, group.length)
  }

  for (const content of contents) {
    if (content.kind === 'selectableInput' && mustRegroup(content)) {
      group.push(content)
    } else {
      pushGroup()
      if (content.kind === 'selectableInput' && mustRegroup(content)) {
        group.push(content)
      } else {
        ret.push(content)
      }
    }
  }
  pushGroup()

  return ret
}

function makeRenderableExercise(exercise: AdaptedExercise): RenderableExercise {
  const pages: RenderablePage[] = []

  const instruction = [
    ...exercise.instruction.lines,
    ...(exercise.example ? exercise.example.lines : []),
    ...(exercise.hint ? exercise.hint.lines : []),
  ].map((line) => ({
    contents: line.contents.flatMap(makeRenderableFromPassiveExerciseComponent),
  }))

  if (exercise.statement.pages.length === 0) {
    pages.push({ kind: 'statement', instruction, statement: [] })
  } else {
    for (const page of exercise.statement.pages) {
      const statement: { contents: AnyRenderable[]; alone: boolean }[] = []

      for (const { contents } of page.lines) {
        const alone =
          contents.length === 1 && (contents[0].kind === 'editableTextInput' || contents[0].kind === 'freeTextInput')
        statement.push({
          contents: regroupSelectableInputs(contents.flatMap(makeRenderableFromAnyExerciseComponent)),
          alone,
        })
        for (const component of contents) {
          if (component.kind === 'editableTextInput' && component.showOriginalText) {
            statement.push({
              contents: [
                { kind: 'text', text: '→' },
                { kind: 'whitespace' },
                makeRenderableFromEditableTextInput(component),
              ],
              alone: false,
            })
          }
        }
      }

      pages.push({ kind: 'statement', instruction, statement })
    }
  }

  if (exercise.reference !== null) {
    pages.push({
      kind: 'reference',
      contents: exercise.reference.contents.flatMap(makeRenderableFromFormattedTextExerciseComponent),
    })
  }

  return { pages }
}
</script>

<script setup lang="ts">
import { computed, nextTick, provide, reactive, ref, useTemplateRef, watch } from 'vue'
import { useStorage } from '@vueuse/core'

import AnySequenceComponent from './dispatch/AnySequenceComponent.vue'
import PassiveSequenceComponent from './dispatch/PassiveSequenceComponent.vue'
import PageNavigationControls from './PageNavigationControls.vue'
import TriColorLines from './TriColorLines.vue'

const props = withDefaults(
  defineProps<{
    navigateUsingArrowKeys: boolean
    studentAnswersStorageKey?: string | null
    adaptedExercise: AdaptedExercise
    spacingVariables?: SpacingVariables
  }>(),
  { studentAnswersStorageKey: null, spacingVariables: defaultSpacingVariables },
)

provide('adaptedExerciseContainerDiv', useTemplateRef('container'))
provide('adaptedExerciseStatementDiv', useTemplateRef('statement'))

const renderableExercise = computed(() => makeRenderableExercise(props.adaptedExercise))

const pageIndex = ref(0)

const inProgress = reactive<InProgressExercise>({
  exercise: renderableExercise.value,
  p: { kind: 'none' },
})
watch(renderableExercise, (exercise) => {
  inProgress.exercise = exercise
  inProgress.p = { kind: 'none' }
})
watch(pageIndex, () => {
  inProgress.p = { kind: 'none' }
})

const page = computed(() => renderableExercise.value.pages[pageIndex.value])

const defaultStudentAnswers = { pages: {} }

const studentAnswers =
  props.studentAnswersStorageKey === null
    ? ref(defaultStudentAnswers)
    : useStorage(`patty/student-answers/v3/exercise-${props.studentAnswersStorageKey}`, defaultStudentAnswers)

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

const spacingVariables = computed(() =>
  Object.fromEntries(Object.entries(props.spacingVariables).map(([key, value]) => [key, `${value}em`])),
)
</script>

<template>
  <PageNavigationControls :navigateUsingArrowKeys :pagesCount="renderableExercise.pages.length" v-model="pageIndex">
    <div ref="container" class="container" spellcheck="false" :style="spacingVariables">
      <template v-if="page.kind === 'statement'">
        <div class="instruction">
          <p v-for="{ contents } in page.instruction">
            <PassiveSequenceComponent :contents :tricolorable="false" />
          </p>
        </div>
        <div ref="statement" class="statement" v-if="page.statement.length !== 0">
          <TriColorLines ref="tricolor">
            <template v-for="({ contents, alone }, lineIndex) in page.statement">
              <p :class="{ alone }">
                <AnySequenceComponent
                  :pageIndex
                  :lineIndex
                  :contents
                  :aloneOnLine="alone"
                  :tricolorable="true"
                  v-model="studentAnswers"
                  v-model:inProgress="inProgress"
                />
              </p>
            </template>
          </TriColorLines>
        </div>
      </template>
      <template v-else-if="page.kind === 'reference'">
        <div class="reference">
          <p>
            <PassiveSequenceComponent :contents="page.contents" :tricolorable="false" />
          </p>
        </div>
      </template>
      <p v-else>BUG: unexpected page kind: {{ ((page: never) => page)(page) }}</p>
    </div>
  </PageNavigationControls>
</template>

<style scoped>
div.container {
  font-family: Arial, sans-serif;
  font-size: 32px;
  white-space-collapse: preserve;
  word-spacing: var(--extra-horizontal-space-between-words);
  /* Ensure anything 'Teleport'ed to this element is rendered strictly within this element */
  overflow-x: hidden;
  overflow-y: auto;
  transform: scale(1);
  height: 100%;
  display: flex;
  flex-direction: column;
}

:deep(*) {
  margin: 0;
  padding: 0;
}

.instruction {
  text-align: center;
  padding-left: 6px;
  padding-right: 6px;
  margin-top: calc(
    var(--vertical-space-between-top-and-instruction) - (var(--vertical-space-between-instruction-lines) - 1em) / 2
  );
  line-height: var(--vertical-space-between-instruction-lines);
}

.statement {
  flex: 1;
  position: relative;
  padding-left: 6px;
  padding-right: 6px;
  margin-top: calc(
    var(--vertical-space-between-instruction-and-statement) -
      (var(--vertical-space-between-instruction-lines) - 1em + var(--vertical-space-between-statement-lines) - 1em) / 2
  );
  line-height: var(--vertical-space-between-statement-lines);
}

.reference {
  padding-left: 6px;
  padding-right: 6px;
}

p.alone {
  border: 2px outset black;
  padding: 4px;
}

p.alone:has(:focus) {
  background-color: #fffdd4;
}
</style>
