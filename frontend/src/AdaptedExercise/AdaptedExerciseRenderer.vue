<script lang="ts">
import type { AdaptedExercise, AdaptedExerciseV2 } from '@/apiClient'
import { match, P } from 'ts-pattern'
import deepCopy from 'deep-copy'
import _ from 'lodash'

import assert from '../assert'

type Phase = AdaptedExerciseV2['phases'][number]
type PhaseInstructionComponent = Phase['instruction']['lines'][number]['contents'][number]
type PhaseStatementComponent = (Phase['statement'] & {
  generated: undefined
})['pages'][number]['lines'][number]['contents'][number]

type TextComponent = PhaseInstructionComponent & { kind: 'text' }
type WhitespaceComponent = PhaseInstructionComponent & { kind: 'whitespace' }
type FormattedComponent = PhaseInstructionComponent & { kind: 'formatted' }
type ArrowComponent = PhaseInstructionComponent & { kind: 'arrow' }
type ChoiceComponent = PhaseInstructionComponent & { kind: 'choice' }
type ActiveFormattedComponent = PhaseStatementComponent & { kind: 'formatted' }
type FreeTextInputComponent = PhaseStatementComponent & { kind: 'freeTextInput' }
type MultipleChoicesInputComponent = PhaseStatementComponent & { kind: 'multipleChoicesInput' }
type SelectableInputComponent = PhaseStatementComponent & { kind: 'selectableInput' }
type SwappableInputComponent = PhaseStatementComponent & { kind: 'swappableInput' }
type EditableTextInputComponent = PhaseStatementComponent & { kind: 'editableTextInput' }

type PlainTextComponent = TextComponent | WhitespaceComponent
type FormattedTextComponent = PlainTextComponent | ArrowComponent | FormattedComponent
type ActiveFormattedTextComponent =
  | PlainTextComponent
  | ArrowComponent
  | ActiveFormattedComponent
  | FreeTextInputComponent

export type InstructionComponent = FormattedTextComponent | ChoiceComponent
export type ExampleComponent = FormattedTextComponent
export type HintComponent = FormattedTextComponent
export type StatementComponent =
  | ActiveFormattedTextComponent
  | MultipleChoicesInputComponent
  | SelectableInputComponent
  | SwappableInputComponent
  | EditableTextInputComponent
export type ReferenceComponent = FormattedTextComponent

export type InProgressExercise = {
  swappables: { [path: string]: SwappableInputRenderable }
  p:
    | {
        kind: 'none'
      }
    | {
        kind: 'movingSwappable'
        swappable: {
          path: string
          contentsFrom: string
        }
      }
    | {
        kind: 'solvingMultipleChoices'
        path: string
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
      contentsFrom: string
    }

export type StudentAnswers = Partial<Record<string, ComponentAnswer>>

export function ensureV2(exercise: AdaptedExercise): AdaptedExerciseV2 {
  if (exercise.format === 'v2') {
    return exercise
  } else {
    return {
      format: 'v2',
      phases: [
        {
          instruction: exercise.instruction,
          example: exercise.example,
          hint: exercise.hint,
          statement: exercise.statement,
        },
      ],
      reference: exercise.reference,
    }
  }
}

export function countPages(exercise: AdaptedExerciseV2) {
  let pagesCount = exercise.steps
    .map((s) => ('pages' in s.statement ? Math.max(1, s.statement.pages.length) : 1))
    .reduce((a, b) => a + b, 0)
  if (exercise.reference !== null) {
    pagesCount += 1
  }
  return pagesCount
}

export const defaultSpacingVariables = () => ({
  '--extra-horizontal-space-between-words': 0.26,
  '--optional-extra-horizontal-space-between-letters-in-editable-text-input': 0.2,
  '--font-size-for-single-character-selectable': 1.2,
  '--extra-horizontal-space-around-single-letter-selectable': 0.0625,
  '--extra-vertical-space-around-single-letter-selectable': 0.0625,
  '--extra-horizontal-space-around-single-punctuation-selectable': 0.1,
  '--extra-vertical-space-around-single-punctuation-selectable': 0.5,
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
  contents: AnyRenderable[]
  bold: boolean
  italic: boolean
  underlined: boolean
  highlighted: string | null
  boxed: boolean
  superscript: boolean
  subscript: boolean
}

export type PassiveRenderable = PlainTextRenderable | FormattedRenderable

export type TextInputRenderable = {
  kind: 'textInput'
  path: string
  initialText: string
  increaseHorizontalSpace: boolean
}

type MultipleChoicesInputRenderable = {
  kind: 'multipleChoicesInput'
  path: string
  choices: {
    contents: PassiveRenderable[]
  }[]
  showChoicesByDefault: boolean
}

export type SelectableInputRenderable = {
  kind: 'selectableInput'
  path: string
  contents: (PassiveRenderable | SelectableInputRenderable)[]
  colors: string[]
  boxed: boolean
  mayBeSingleLetter: boolean
}

type SwappableInputRenderable = {
  kind: 'swappableInput'
  path: string
  contents: PassiveRenderable[]
}

type ActiveRenderable =
  | TextInputRenderable
  | MultipleChoicesInputRenderable
  | SelectableInputRenderable
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

type EndRenderablePage = {
  kind: 'end'
}

type RenderablePage = StatementRenderablePage | ReferenceRenderablePage | EndRenderablePage

type RenderableExercise = {
  pages: RenderablePage[]
}

function makeRenderableFromFormattedTextComponent(component: FormattedTextComponent): PassiveRenderable[] {
  return match(component)
    .returnType<PassiveRenderable[]>()
    .with({ kind: 'whitespace' }, () => [{ kind: 'whitespace' }])
    .with({ kind: 'text' }, (c) => [{ kind: 'text', text: c.text }])
    .with({ kind: 'arrow' }, () => [{ kind: 'text', text: '→' }])
    .with({ kind: 'formatted' }, (c) => [
      {
        kind: 'formatted',
        contents: c.contents.flatMap(makeRenderableFromFormattedTextComponent),
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

function makeRenderableFromInstructionComponent(component: InstructionComponent): PassiveRenderable[] {
  return match(component)
    .returnType<PassiveRenderable[]>()
    .with({ kind: 'choice' }, (c) => [
      {
        kind: 'formatted',
        contents: c.contents.flatMap(makeRenderableFromFormattedTextComponent),
        bold: false,
        italic: false,
        underlined: false,
        highlighted: null,
        boxed: true,
        superscript: false,
        subscript: false,
      },
    ])
    .otherwise(makeRenderableFromFormattedTextComponent)
}

function makeRenderableFromSelectableInputContent(
  basePath: string,
  component: SelectableInputComponent['contents'][number],
  index: number,
): (PassiveRenderable | SelectableInputRenderable)[] {
  const path = `${basePath}-ct${index}`
  return match(component)
    .returnType<(PassiveRenderable | SelectableInputRenderable)[]>()
    .with({ kind: 'selectableInput' }, (c) => [
      {
        kind: 'selectableInput',
        path,
        contents: c.contents.flatMap((x, index) => makeRenderableFromSelectableInputContent(path, x, index)),
        colors: c.colors,
        boxed: c.boxed,
        mayBeSingleLetter: false,
      },
    ])
    .otherwise(makeRenderableFromInstructionComponent)
}

function makeRenderableFromActiveFormattedTextComponent(
  path: string,
  component: ActiveFormattedTextComponent,
): AnyRenderable[] {
  return match(component)
    .returnType<AnyRenderable[]>()
    .with({ kind: 'formatted' }, (c) => [
      {
        kind: 'formatted',
        contents: c.contents.flatMap((x, index) =>
          makeRenderableFromActiveFormattedTextComponent(`${path}-ct${index}`, x),
        ),
        bold: c.bold ?? false,
        italic: c.italic ?? false,
        underlined: c.underlined ?? false,
        highlighted: c.highlighted ?? null,
        boxed: c.boxed ?? false,
        superscript: c.superscript ?? false,
        subscript: c.subscript ?? false,
      },
    ])
    .with({ kind: 'freeTextInput' }, ({}) => [
      {
        kind: 'textInput',
        path,
        initialText: '',
        increaseHorizontalSpace: false,
      },
    ])
    .otherwise(makeRenderableFromFormattedTextComponent)
}

function makeRenderableFromStatementComponent(path: string, component: StatementComponent): AnyRenderable[] {
  return match(component)
    .returnType<AnyRenderable[]>()
    .with({ kind: 'multipleChoicesInput' }, ({ choices, showChoicesByDefault }) => [
      {
        kind: 'multipleChoicesInput',
        path,
        choices: choices.map(({ contents }) => ({
          contents: contents.flatMap(makeRenderableFromFormattedTextComponent),
        })),
        showChoicesByDefault,
      },
    ])
    .with({ kind: 'selectableInput' }, ({ boxed, colors, contents }) => [
      {
        kind: 'selectableInput',
        path,
        boxed,
        colors,
        contents: contents.flatMap((c, index) => makeRenderableFromSelectableInputContent(path, c, index)),
        mayBeSingleLetter: false,
      },
    ])
    .with({ kind: 'swappableInput' }, ({ contents }) => [
      {
        kind: 'swappableInput',
        path,
        contents: contents.flatMap(makeRenderableFromFormattedTextComponent),
      },
    ])
    .with({ kind: 'editableTextInput', showOriginalText: true }, (c) => c.contents)
    .with({ kind: 'editableTextInput' }, (c) => [makeRenderableFromEditableTextInput(path, c)])
    .otherwise((c) => makeRenderableFromActiveFormattedTextComponent(path, c))
}

function makeRenderableFromEditableTextInput(
  path: string,
  { contents, increaseHorizontalSpace }: EditableTextInputComponent,
): AnyRenderable {
  return {
    kind: 'textInput',
    path,
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

function markConsecutiveSelectableInputs(contents: AnyRenderable[]): AnyRenderable[] {
  const ret: AnyRenderable[] = deepCopy(contents)
  for (let i = 1; i < ret.length; i++) {
    const a = ret[i - 1]
    const b = ret[i]
    if (a.kind === 'selectableInput' && b.kind === 'selectableInput') {
      a.mayBeSingleLetter = true
      b.mayBeSingleLetter = true
    }
  }
  return ret
}

function makeRenderableExercise(exercise: AdaptedExerciseV2, studentAnswers: StudentAnswers): RenderableExercise {
  const pages: RenderablePage[] = []

  for (const phase of exercise.phases) {
    const instruction = [
      ...phase.instruction.lines,
      ...(phase.example ? phase.example.lines : []),
      ...(phase.hint ? phase.hint.lines : []),
    ].map((line) => ({
      contents: line.contents.flatMap(makeRenderableFromInstructionComponent),
    }))

    match(phase.statement)
      .with({ generated: P.select() }, (generator) => {
        assert(generator.items.kind === 'selectableInput')
        const selected: [string, SelectableInputComponent][] = []
        for (const previousPhase of exercise.phases) {
          if (previousPhase === phase) {
            break
          }
          if ('pages' in previousPhase.statement) {
            for (const [pageIndex, page] of previousPhase.statement.pages.entries()) {
              for (const [lineIndex, line] of page.lines.entries()) {
                for (const [componentIndex, component] of line.contents.entries()) {
                  if (component.kind === 'selectableInput') {
                    const path = `stmt-pg${pageIndex}-ln${lineIndex}-ct${componentIndex}`
                    const answer = studentAnswers[path]
                    if (answer !== undefined) {
                      assert(answer.kind === 'selectable')
                      if (answer.color === generator.items.colorIndex) {
                        selected.push([path, component])
                      }
                    }
                  }
                }
              }
            }
          }
        }

        if (selected.length === 0) {
          pages.push({ kind: 'statement', instruction, statement: [] })
        } else {
          for (const group of _.chunk(selected, generator.itemsPerPage)) {
            const statement: StatementLine[] = []
            for (const [path, component] of group) {
              const components: StatementComponent[] = generator.template.contents.flatMap((c) =>
                match(c)
                  .with({ kind: 'itemPlaceholder' }, () => component.contents)
                  .otherwise((c) => c),
              )
              const contents = components.flatMap((c) => makeRenderableFromStatementComponent(`${path}-ecrire`, c))
              statement.push({ contents, alone: false })
            }
            pages.push({ kind: 'statement', instruction, statement })
          }
        }
      })
      .with({ pages: [] }, () => {
        pages.push({ kind: 'statement', instruction, statement: [] })
      })
      .with({ pages: P.select() }, (statementPages) => {
        for (const page of statementPages) {
          const statement: StatementLine[] = []

          for (const [lineIndex, { contents }] of page.lines.entries()) {
            const alone =
              contents.length === 1 &&
              (contents[0].kind === 'editableTextInput' || contents[0].kind === 'freeTextInput')

            statement.push({
              contents: markConsecutiveSelectableInputs(
                Array.from(contents.entries()).flatMap(([componentIndex, c]) =>
                  makeRenderableFromStatementComponent(`stmt-pg${pages.length}-ln${lineIndex}-ct${componentIndex}`, c),
                ),
              ),
              alone,
            })
            for (const [componentIndex, component] of contents.entries()) {
              if (component.kind === 'editableTextInput' && component.showOriginalText) {
                statement.push({
                  contents: [
                    { kind: 'text', text: '→' },
                    { kind: 'whitespace' },
                    makeRenderableFromEditableTextInput(
                      `stmt-pg${pages.length}-ln${lineIndex}-ct${componentIndex}`,
                      component,
                    ),
                  ],
                  alone: false,
                })
              }
            }
          }

          pages.push({ kind: 'statement', instruction, statement })
        }
      })
      .exhaustive()
  }

  if (exercise.reference !== null) {
    pages.push({
      kind: 'reference',
      contents: exercise.reference.contents.flatMap(makeRenderableFromFormattedTextComponent),
    })
  }

  pages.push({
    kind: 'end',
  })

  return { pages }
}
</script>

<script setup lang="ts">
import { computed, nextTick, provide, reactive, ref, useTemplateRef, watch } from 'vue'
import { useStorage } from '@vueuse/core'
import { useRoute } from 'vue-router'

import AnySequenceComponent from './dispatch/AnySequenceComponent.vue'
import AloneFreeTextInput from './dispatch/AloneFreeTextInput.vue'
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

const route = useRoute()

const studentAnswers =
  props.studentAnswersStorageKey === null
    ? ref<StudentAnswers>({})
    : useStorage<StudentAnswers>(`patty/student-answers/v3/exercise-${props.studentAnswersStorageKey}`, {})
provide('adaptedExerciseStudentAnswers', studentAnswers)

const exerciseV2 = computed(() => ensureV2(props.adaptedExercise))

const renderableExercise = computed(() => makeRenderableExercise(exerciseV2.value, studentAnswers.value))

const swappables = computed(() => {
  const swappables: { [path: string]: SwappableInputRenderable } = {}
  for (const page of renderableExercise.value.pages) {
    if (page.kind === 'statement') {
      for (const line of page.statement) {
        for (const component of line.contents) {
          if (component.kind === 'swappableInput') {
            swappables[component.path] = component
          }
        }
      }
    }
  }
  return swappables
})

const pagesCount = computed(() => countPages(exerciseV2.value))
const pageIndex = ref(0)
watch(
  pagesCount,
  (pagesCount) => {
    if (pageIndex.value >= pagesCount) {
      pageIndex.value = Math.max(0, pagesCount - 1)
    }
  },
  { immediate: true },
)

const inProgress = reactive<InProgressExercise>({
  swappables: swappables.value,
  p: { kind: 'none' },
})
watch(swappables, (swappables) => {
  inProgress.swappables = swappables
  inProgress.p = { kind: 'none' }
})
watch(pageIndex, () => {
  inProgress.p = { kind: 'none' }
})
provide('adaptedExerciseInProgress', inProgress)

const page = computed(() => renderableExercise.value.pages[pageIndex.value])

function reset() {
  studentAnswers.value = {}
  inProgress.p = { kind: 'none' }
  pageIndex.value = 0
}

const closable = computed(() => route !== undefined && route.query.closable === 'true')

function close() {
  window.close()
}

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
            <template v-for="{ contents, alone } in page.statement">
              <AloneFreeTextInput
                v-if="alone && contents[0].kind === 'textInput'"
                :component="contents[0]"
                :tricolorable="true"
              />
              <p v-else>
                <AnySequenceComponent :contents :tricolorable="true" />
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
      <template v-else-if="page.kind === 'end'">
        <p class="reference"><button :disabled="!closable" @click="close">Quitter l'exercice</button></p>
        <p class="reference"><button @click="pageIndex = 0">Revenir au début de l'exercice</button></p>
        <p class="reference"><button @click="reset">Effacer mes réponses</button></p>
      </template>
      <p v-else>BUG: {{ ((page: never) => page)(page) }}</p>
      <p v-if="pageIndex < renderableExercise.pages.length - 1" class="arrow">
        <!-- arrow.png has been provided by the client in https://github.com/jacquev6/Patty/issues/28 -->
        <img src="./arrow.png" @click="++pageIndex" />
      </p>
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
  margin-top: 1em;
  margin-bottom: 1em;
}

p.arrow {
  text-align: center;
}
p.arrow img {
  cursor: pointer;
}
</style>
