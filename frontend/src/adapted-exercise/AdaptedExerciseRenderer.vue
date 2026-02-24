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
  editable: boolean
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
    return 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGQAAAAyCAYAAACqNX6+AAABhGlDQ1BJQ0MgcHJvZmlsZQAAKJF9kT1Iw0AcxV9TpVoqInYQcchQneyiIoJLrUIRKoRaoVUHk0u/oElDkuLiKLgWHPxYrDq4OOvq4CoIgh8g7oKToouU+L+k0CLWg+N+vLv3uHsHCPUy06yuGKDptplKxMVMdlUMvCKEAfRiFkGZWcacJCXRcXzdw8fXuyjP6nzuz9Gn5iwG+ETiGDNMm3iDeHrTNjjvE4dZUVaJz4nHTbog8SPXFY/fOBdcFnhm2Eyn5onDxGKhjZU2ZkVTI54ijqiaTvlCxmOV8xZnrVxlzXvyF4Zy+soy12mOIIFFLEGCCAVVlFCGjSitOikWUrQf7+Afdv0SuRRylcDIsYAKNMiuH/wPfndr5ScnvKRQHOh+cZyPUSCwCzRqjvN97DiNE8D/DFzpLX+lDsx8kl5raZEjoH8buLhuacoecLkDDD0Zsim7kp+mkM8D72f0TVlg8BYIrnm9Nfdx+gCkqavkDXBwCIwVKHu9w7t72nv790yzvx+r0XK9cASKtAAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAAuIwAALiMBeKU/dgAAAAd0SU1FB+kMEQoHDnWkAwcAAAAZdEVYdENvbW1lbnQAQ3JlYXRlZCB3aXRoIEdJTVBXgQ4XAAAGtUlEQVR42u1bb0iTXRT/LcWwNFrYKDP6X7TFCGttzlaGNVmB1qawyKCPGRT5IT8Y9iEW0R+SjCiMKCnLlCRqGEvULdkacxaVU6FWRm0NtUV/TNvM+37ysmd7Vr6xVu/b/cED5+zcc+95nt+9zzn3bhMQQggY/hhMYo+AEcLACGGEMDBCGCEMjBBGCAMjhBHCwAhhYIQwQhgYIYwQBkbIBHDp0iUIBAIIBAIcOXKEY/vy5QsqKiogkUhQXl6Oz58///mEqNVqekNGo/F/RZbX64XBYEB3dzeOHj2KN2/e/FHxJf5tr4T58+fj+vXr6O3txbJly7Bo0SJGyG+94cRE6PV6lkPiiYSEhP/uhIllZ8PDw7BarWhpaYHdbsfIyAjWrFkDtVoNlUqFadOm8fq53W6YzWbYbDY4nU4kJiZCoVBgw4YN2LhxI6ZPn87r19PTg4aGBty9exdCoRBbtmxBUVERpk6dGjVGn8+H2bNnU93j8SA9PT3CZjQasXnzZjidThiNRrS0tAAA8vLyoNVqIZFIePt3uVxoaGiAyWSCUChEfn4+CgsLEQgEMGfOHACAwWDAwYMH+QMkPNi0aRMBQACQO3fukInA5/MRvV5P/cKvvLw88vz58wi/mpqaqD4AiEqlIl6vN8Lv/v37vO1lMhk5f/481Q0GA8fv7du3nPYej4fXVlFRQa5duxY1rtbW1oiYLBYLb1uFQkEaGxujxhSKmBDy9etXsnPnTk4QGo2GFBcXcz7Lyckhfr+f4+t2u6ldLBaTkpISotPpOH6HDh3i+AwODpKFCxdy2uh0OlJQUBDxMH6WkNBr9+7dEX1nZmaS4eFh6vvu3TvemMLvJS6EtLe3cwa0Wq3U1tfXRxQKBbXV1tbyznaPx0PGxsYIIYSMjY2RmzdvcvoMvfnbt29zbBaLhdpcLhcRiUQxISR8ddbW1nLsoSveaDRybHa7ndq6u7tJRkbGhAiJSVK32WxULi0thVKppPq8efNQWlpK9QsXLiD8t3kqlQrp6ekQCAQAAIFAgFWrVnHaDA0NUdnpdFK5pKQE69ato7pYLEZZWVlMcuLevXs5+UatVnPsoZvKjo4OKu/fvx9yuZzqy5cvR3l5efyS+qNHj6i8evXqCPvixYupbDabMTQ0hJSUFADAhw8fYLFYYLPZ0NHRga6uLvT39/PlOk7iDCUzHGKxOCaEhPeTmprK0b99+0blJ0+eUFkmk0X0tXTp0vgR4vP5ogYNAFOmTImoxlJSUuD1eqHX69He3v7T4/FVbtGquX+L8Gpt0qToL5TQScT3DJKTk+O3D1myZAmVP378GGEPfd0AQFJSEgDg4sWLlIzs7Gy4XC6MjIyAEILXr19HHS8tLY3Knz594i2/Y4HxOCcCkUj03ZiCwWD8CAmtyR0OR4T92bNnnFfM+Ay+fPky/fzAgQMQi8WYPHkyAOD9+/dRx5NKpbzv7tB9TbyxYsUK3hw3ju9NsJgTEppUq6qqYLVaqf7q1SucPn2a6rt27aLJOxAIcA79xvOE3+/HuXPnoo4XmvBPnTqFBw8ecMg4fvx43AkJzZ2VlZWw2+1U7+vrQ2VlZWxyyOHDh1FdXc1rq66uxqxZsyCVSlFWVkYfxNq1a6HRaJCWloYrV67Q9pmZmcjPz6f6jh07cOzYMQDAnj170NbWBqFQiFu3bqG/vx+pqam8yz87OxsZGRn0pFapVEKn0yEhIQH19fW/5cgjKysLIpGI5pKsrCzodDokJyfj6tWrE+/oR/uQ712hNbzf7yf79u2L2lYmk5Genh7OOF1dXVHbm0wmcubMGaoPDAxwfNva2nj99Ho9aW5ujsk+JNRGCCGBQIBj7+zs5NhNJhNvTMXFxeTs2bMT2ofE7CxLKBTi5MmTKCwsRHNzMxwOBwYGBiCXy5Gbm4vc3NyIMymJRAK32426ujqYzWYEg0GsX78eWq0WUqkUM2fOjDpeTk4Onj59ihs3bqCpqQlz587F1q1bodPpkJSUBKlUyilF4wG1Wo2HDx+ivr4eTU1NWLBgAbZt2watVovGxsafXyEMsUdVVRVdISdOnPi1O3WGH056dHZ28pbtf8X3Ib8Dg4ODqKurw4sXLzA6Osoh4969e6ipqeHdJvzS70P+ZoyOjmL79u10k6jRaDBjxgw8fvwYra2ttF1RURFWrlzJcsivRrSj+9CroKAgonILh4D9LTo2CAaDcDgccDqd6O3txcuXL+FyuSCRSCCXy6FSqaBUKiPO9cLBCPnDwJI6I4SBEcIIYWCEMEIYGCGMEAZGyF+OfwA+brXtkdhMkgAAAABJRU5ErkJggg=='
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
    .with({ kind: 'swappableInput' }, ({ contents, editable }) => [
      {
        kind: 'swappableInput',
        path,
        contents: contents.flatMap((x) => makeRenderableFromFormattedTextComponent(imagesUrls, x)),
        editable: editable == undefined ? false : editable,
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
                v-if="
                  contents.length == 1 &&
                  contents[0].kind === 'textInput' &&
                  contents[0].increaseHorizontalSpace === false
                "
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
        <p class="endPage">
          <button :disabled="!closable" @click="close">{{ t('exit') }}</button>
        </p>
        <p class="endPage">
          <button @click="pageIndex = 0">{{ t('back') }}</button>
        </p>
        <p class="endPage">
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
  margin-bottom: 1em;
  margin-top: calc(
    var(--vertical-space-between-top-and-instruction) - (var(--vertical-space-between-instruction-lines) - 1em) / 2
  );
  line-height: var(--vertical-space-between-instruction-lines);
}

.endPage {
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
