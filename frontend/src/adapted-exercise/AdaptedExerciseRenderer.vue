<!-- Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net> -->

<script lang="ts">
import type { AdaptedExercise, AdaptedExerciseV2, ImagesUrls } from '@/frontend/ApiClient'
import { match, P } from 'ts-pattern'
import deepCopy from 'deep-copy'
import _ from 'lodash'

import assert from '$/assert'

type Phase = AdaptedExerciseV2['phases'][number]
type PhaseInstructionComponent = Phase['instruction']['lines'][number]['contents'][number]
type PhaseStatementComponent = (Phase['statement'] & {
  generated: undefined
})['pages'][number]['lines'][number]['contents'][number]

type TextComponent = PhaseInstructionComponent & { kind: 'text' }
type WhitespaceComponent = PhaseInstructionComponent & { kind: 'whitespace' }
type FormattedComponent = PhaseInstructionComponent & { kind: 'formatted' }
type ImageComponent = PhaseInstructionComponent & { kind: 'image' }
type ArrowComponent = PhaseInstructionComponent & { kind: 'arrow' }
type ChoiceComponent = PhaseInstructionComponent & { kind: 'choice' }
type ActiveFormattedComponent = PhaseStatementComponent & { kind: 'formatted' }
type FreeTextInputComponent = PhaseStatementComponent & { kind: 'freeTextInput' }
type MultipleChoicesInputComponent = PhaseStatementComponent & { kind: 'multipleChoicesInput' }
type SelectableInputComponent = PhaseStatementComponent & { kind: 'selectableInput' }
type SwappableInputComponent = PhaseStatementComponent & { kind: 'swappableInput' }
type EditableTextInputComponent = PhaseStatementComponent & { kind: 'editableTextInput' }
type SplitWordInputComponent = PhaseStatementComponent & { kind: 'splitWordInput' }

type PlainTextComponent = TextComponent | WhitespaceComponent
type FormattedTextComponent = PlainTextComponent | ArrowComponent | FormattedComponent | ImageComponent
type ActiveFormattedTextComponent =
  | PlainTextComponent
  | ArrowComponent
  | ActiveFormattedComponent
  | ImageComponent
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
  | SplitWordInputComponent
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
  | {
      kind: 'splitWord'
      separatorIndex: number | null
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
  '--clickable-padding-around-next-page-arrow': 2.0,
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

export type ImageRenderable = {
  kind: 'image'
  height: string
  align: 'left' | 'center' | 'right' | undefined
  url: string
}

export type PassiveRenderable = PlainTextRenderable | FormattedRenderable | ImageRenderable

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
  reducedLineSpacing: boolean
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

export type SplitWordInputRenderable = {
  kind: 'splitWordInput'
  path: string
  word: string
}

type ActiveRenderable =
  | TextInputRenderable
  | MultipleChoicesInputRenderable
  | SelectableInputRenderable
  | SwappableInputRenderable
  | SplitWordInputRenderable

export type AnyRenderable = PassiveRenderable | ActiveRenderable

type StatementLine = {
  contents: AnyRenderable[]
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

function makeRenderableUrl(url: string | undefined): string {
  if (url === undefined) {
    return 'data:image/png;base64,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'
  } else {
    return url
  }
}

function makeRenderableFromFormattedTextComponent(
  imagesUrls: ImagesUrls,
  component: FormattedTextComponent,
): PassiveRenderable[] {
  return match(component)
    .returnType<PassiveRenderable[]>()
    .with({ kind: 'whitespace' }, () => [{ kind: 'whitespace' }])
    .with({ kind: 'text' }, (c) => [{ kind: 'text', text: c.text }])
    .with({ kind: 'arrow' }, () => [{ kind: 'text', text: '→' }])
    .with({ kind: 'image' }, (c) => [
      {
        kind: 'image',
        height: c.height,
        align: c.align === undefined || c.align == null ? undefined : c.align,
        url: makeRenderableUrl(imagesUrls[c.identifier]),
      },
    ])
    .with({ kind: 'formatted' }, (c) => [
      {
        kind: 'formatted',
        contents: c.contents.flatMap((x) => makeRenderableFromFormattedTextComponent(imagesUrls, x)),
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

function makeRenderableFromInstructionComponent(
  imagesUrls: ImagesUrls,
  component: InstructionComponent,
): PassiveRenderable[] {
  return match(component)
    .returnType<PassiveRenderable[]>()
    .with({ kind: 'choice' }, (c) => [
      {
        kind: 'formatted',
        contents: c.contents.flatMap((x) => makeRenderableFromFormattedTextComponent(imagesUrls, x)),
        bold: false,
        italic: false,
        underlined: false,
        highlighted: null,
        boxed: true,
        superscript: false,
        subscript: false,
      },
    ])
    .otherwise((x) => makeRenderableFromFormattedTextComponent(imagesUrls, x))
}

function makeRenderableFromSelectableInputContent(
  imagesUrls: ImagesUrls,
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
        contents: c.contents.flatMap((x, index) =>
          makeRenderableFromSelectableInputContent(imagesUrls, path, x, index),
        ),
        colors: c.colors,
        boxed: c.boxed,
        mayBeSingleLetter: false,
      },
    ])
    .otherwise((x) => makeRenderableFromInstructionComponent(imagesUrls, x))
}

function makeRenderableFromActiveFormattedTextComponent(
  imagesUrls: ImagesUrls,
  path: string,
  component: ActiveFormattedTextComponent,
): AnyRenderable[] {
  return match(component)
    .returnType<AnyRenderable[]>()
    .with({ kind: 'formatted' }, (c) => [
      {
        kind: 'formatted',
        contents: c.contents.flatMap((x, index) =>
          makeRenderableFromActiveFormattedTextComponent(imagesUrls, `${path}-ct${index}`, x),
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
    .otherwise((x) => makeRenderableFromFormattedTextComponent(imagesUrls, x))
}

function makeRenderableFromStatementComponent(
  imagesUrls: ImagesUrls,
  path: string,
  component: StatementComponent,
): AnyRenderable[] {
  return match(component)
    .returnType<AnyRenderable[]>()
    .with({ kind: 'multipleChoicesInput' }, ({ choices, showChoicesByDefault, reducedLineSpacing }) => [
      {
        kind: 'multipleChoicesInput',
        path,
        choices: choices.map(({ contents }) => ({
          contents: contents.flatMap((x) => makeRenderableFromFormattedTextComponent(imagesUrls, x)),
        })),
        showChoicesByDefault,
        reducedLineSpacing: reducedLineSpacing === undefined ? false : reducedLineSpacing,
      },
    ])
    .with({ kind: 'selectableInput' }, ({ boxed, colors, contents }) => [
      {
        kind: 'selectableInput',
        path,
        boxed,
        colors,
        contents: contents.flatMap((c, index) => makeRenderableFromSelectableInputContent(imagesUrls, path, c, index)),
        mayBeSingleLetter: false,
      },
    ])
    .with({ kind: 'swappableInput' }, ({ contents }) => [
      {
        kind: 'swappableInput',
        path,
        contents: contents.flatMap((x) => makeRenderableFromFormattedTextComponent(imagesUrls, x)),
      },
    ])
    .with({ kind: 'editableTextInput', showOriginalText: true }, (c) => c.contents)
    .with({ kind: 'editableTextInput' }, (c) => [makeRenderableFromEditableTextInput(path, c)])
    .with({ kind: 'splitWordInput' }, (c) => [
      {
        kind: 'splitWordInput',
        path,
        word: c.word,
      },
    ])
    .otherwise((c) => makeRenderableFromActiveFormattedTextComponent(imagesUrls, path, c))
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
  let mayBeSingleLetters = true
  for (let i = 0; i < ret.length; i++) {
    const c = ret[i]
    if (
      c.kind === 'selectableInput' &&
      (c.contents.length !== 1 || c.contents[0].kind !== 'text' || c.contents[0].text.length !== 1)
    ) {
      mayBeSingleLetters = false
      break
    }
  }
  for (let i = 0; i < ret.length; i++) {
    const c = ret[i]
    if (c.kind === 'selectableInput') {
      c.mayBeSingleLetter = mayBeSingleLetters
    }
  }
  return ret
}

function makeRenderableExercise(
  imagesUrls: ImagesUrls,
  exercise: AdaptedExerciseV2,
  studentAnswers: StudentAnswers,
): RenderableExercise {
  const pages: RenderablePage[] = []

  for (const phase of exercise.phases) {
    const instruction = [
      ...phase.instruction.lines,
      ...(phase.example ? phase.example.lines : []),
      ...(phase.hint ? phase.hint.lines : []),
    ].map((line) => ({
      contents: line.contents.flatMap((x) => makeRenderableFromInstructionComponent(imagesUrls, x)),
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
              const contents = components.flatMap((c) =>
                makeRenderableFromStatementComponent(imagesUrls, `${path}-ecrire`, c),
              )
              statement.push({ contents })
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
            statement.push({
              contents: markConsecutiveSelectableInputs(
                Array.from(contents.entries()).flatMap(([componentIndex, c]) =>
                  makeRenderableFromStatementComponent(
                    imagesUrls,
                    `stmt-pg${pages.length}-ln${lineIndex}-ct${componentIndex}`,
                    c,
                  ),
                ),
              ),
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
      contents: exercise.reference.contents.flatMap((x) => makeRenderableFromFormattedTextComponent(imagesUrls, x)),
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
import { useI18n } from 'vue-i18n'

import AnySequenceComponent from './dispatch/AnySequenceComponent.vue'
import AloneFreeTextInput from './dispatch/AloneFreeTextInput.vue'
import PassiveSequenceComponent from './dispatch/PassiveSequenceComponent.vue'
import PageNavigationControls from './PageNavigationControls.vue'
import TriColorLines from './TriColorLines.vue'
import AloneImage from './dispatch/AloneImage.vue'

const props = withDefaults(
  defineProps<{
    navigateUsingArrowKeys: boolean
    studentAnswersStorageKey?: string | null
    adaptedExercise: AdaptedExercise
    imagesUrls: ImagesUrls
    spacingVariables?: SpacingVariables
    tricolored?: boolean
  }>(),
  { studentAnswersStorageKey: null, spacingVariables: defaultSpacingVariables, tricolored: true },
)

provide('adaptedExerciseContainerDiv', useTemplateRef('container'))
provide('adaptedExerciseStatementDiv', useTemplateRef('statement'))

const route = useRoute()
const { t } = useI18n()

const studentAnswers =
  props.studentAnswersStorageKey === null
    ? ref<StudentAnswers>({})
    : useStorage<StudentAnswers>(`patty/student-answers/v3/exercise-${props.studentAnswersStorageKey}`, {})
provide('adaptedExerciseStudentAnswers', studentAnswers)

const exerciseV2 = computed(() => ensureV2(props.adaptedExercise))
watch(
  exerciseV2,
  () => {
    // Reset answers when the exercise changes (only for preview mode where props.studentAnswersStorageKey === null)
    studentAnswers.value = {}
  },
  { deep: true, immediate: false /* Do not reset answers on load. */ },
)

const renderableExercise = computed(() =>
  makeRenderableExercise(props.imagesUrls, exerciseV2.value, studentAnswers.value),
)

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

const pageIndex = ref(0)
watch(
  computed(() => renderableExercise.value.pages.length - 1),
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
          <template v-for="{ contents } in page.instruction">
            <AloneImage v-if="contents.length == 1 && contents[0].kind === 'image'" :component="contents[0]" />
            <p v-else>
              <PassiveSequenceComponent :contents :tricolorable="false" />
            </p>
          </template>
        </div>
        <div ref="statement" class="statement" v-if="page.statement.length !== 0">
          <TriColorLines ref="tricolor" :tricolored>
            <template v-for="{ contents } in page.statement">
              <AloneFreeTextInput
                v-if="contents.length == 1 && contents[0].kind === 'textInput'"
                :component="contents[0]"
                :tricolorable="true"
              />
              <AloneImage v-else-if="contents.length == 1 && contents[0].kind === 'image'" :component="contents[0]" />
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
        <p class="reference">
          <button :disabled="!closable" @click="close">{{ t('exit') }}</button>
        </p>
        <p class="reference">
          <button @click="pageIndex = 0">{{ t('back') }}</button>
        </p>
        <p class="reference">
          <button @click="reset">{{ t('reset') }}</button>
        </p>
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
  padding: var(--clickable-padding-around-next-page-arrow);
}
</style>

<i18n>
fr:
  exit: Quitter l'exercice
  back: Revenir au début de l'exercice
  reset: Effacer mes réponses
</i18n>
