import { defineComponent, h } from 'vue'

import { examples } from './AdaptedExerciseExamplesView.vue'
import { ensureV2 } from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import MiniatureScreen from '$/MiniatureScreen.vue'
import AdaptedExerciseRenderer from '@/adapted-exercise/AdaptedExerciseRenderer.vue'
import type { AdaptedExercise } from '@/frontend/ApiClient'

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
              navigateUsingArrowKeys: false,
            }),
        },
      )
  },
})

describe('Adapted exercises examples', () => {
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
              cy.mount(AdaptedExerciseExamplesCaptureComponent, { props: { adaptedExercise: example.exercise } })

              demoFn()

              // Maybe we could iterate until cy.get('div.control').eq(1) is disabled instead of counting pages?
              // (would probably be more reliable that computing pagesCount a priori)
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
                cy.get('div.control').eq(1).click()
              }
            },
          )
        }
      }
    }
  }
})
