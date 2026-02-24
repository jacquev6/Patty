// MALIN Platform https://malin.cahiersfantastiques.fr/
// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

import { defineComponent, h } from 'vue'
import { createI18n } from 'vue-i18n'

import { examples } from './AdaptedExerciseExamples'
import { ensureV2 } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import MiniatureScreen from '$/MiniatureScreen.vue'
import AdaptedExerciseRenderer from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import type { AdaptedExercise, ImagesUrls } from '@/frontend/ApiClient'

const screenshotsCounts: Record<string, number> = {}

function screenshot(title: string, width: number, height: number, pageIndex: number) {
  if (!Cypress.config().isInteractive) {
    const baseName = `${width}x${height}-${title.replaceAll('/', '')}-page${pageIndex + 1}`
    screenshotsCounts[baseName] = (screenshotsCounts[baseName] ?? 0) + 1
    cy.compareSnapshot({
      name: `${baseName}-${screenshotsCounts[baseName]}`,
      cypressScreenshotOptions: { capture: 'viewport' },
    })
  }
}

const AdaptedExerciseExamplesCaptureComponent = defineComponent({
  name: 'InlineExerciseMiniature',
  props: {
    adaptedExercise: {
      type: Object as () => AdaptedExercise,
      required: true,
    },
    imagesUrls: {
      type: Object as () => ImagesUrls,
      required: true,
    },
  },
  setup(props) {
    return () =>
      h(
        MiniatureScreen,
        { fullScreen: true },
        {
          default: () =>
            h(AdaptedExerciseRenderer, {
              adaptedExercise: props.adaptedExercise,
              imagesUrls: props.imagesUrls,
              navigateUsingArrowKeys: false,
            }),
        },
      )
  },
})

describe('Adapted exercises examples', () => {
  const i18n = createI18n({ legacy: false, locale: 'fr' })

  if (Cypress.browser.name === 'electron') {
    for (const [exampleIndex, example] of examples.entries()) {
      for (const [width, height] of [
        [800, 600],
        [1920, 1080],
      ]) {
        const demos = {
          'not-a-demo': () => {},
          ...(example.demos ?? {}),
        }
        for (const [demoName, demoFn] of Object.entries(demos)) {
          it(
            `renders "${example.title}" in ${width}x${height}` + (demoName !== 'not-a-demo' ? ` - ${demoName}` : ''),
            () => {
              cy.viewport(width, height)
              cy.mount(AdaptedExerciseExamplesCaptureComponent, {
                props: { adaptedExercise: example.exercise, imagesUrls: example.imagesUrls ?? {} },
                global: { plugins: [i18n] },
              })

              demoFn()

              let pagesCount = ensureV2(example.exercise)
                .phases.map((s) => ('pages' in s.statement ? Math.max(1, s.statement.pages.length) : 1))
                .reduce((a, b) => a + b, 0)
              if (example.exercise.reference !== null) {
                pagesCount += 1
              }
              if (demoName === 'not-a-demo' && exampleIndex == examples.length - 1) {
                pagesCount += 1 // For the end page, only once per resolution
              }

              const screenshotTitle = example.title + (demoName !== 'not-a-demo' ? `-${demoName}` : '')
              for (let pageIndex = 0; pageIndex < pagesCount; pageIndex++) {
                cy.get('.container')
                  .eq(0)
                  .then((el) => {
                    cy.get('.container').eq(0).scrollTo('top', { ensureScrollable: false })
                    screenshot(screenshotTitle, width, height, pageIndex)
                    if (el[0].scrollHeight > el[0].clientHeight) {
                      cy.get('.container').eq(0).scrollTo('bottom')
                      screenshot(screenshotTitle, width, height, pageIndex)
                    }
                  })
                if (pageIndex < pagesCount - 1) {
                  cy.get('div.control').eq(1).click()
                }
              }
            },
          )
        }
      }
    }
  }
})
