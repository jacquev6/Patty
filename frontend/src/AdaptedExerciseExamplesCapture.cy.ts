import { examples } from './AdaptedExerciseExamplesView.vue'
import AdaptedExerciseExamplesCaptureComponent from './AdaptedExerciseExamplesCaptureComponent.vue'
import { ensureV2 } from './AdaptedExercise/AdaptedExerciseRenderer.vue'

const screenshotsCounts: Record<string, number> = {}

function screenshot(title: string, pageIndex: number) {
  if (!Cypress.config().isInteractive) {
    cy.get('.inner-container').then((el) => {
      const width = el[0].clientWidth
      const height = el[0].clientHeight
      const baseName = `${width}x${height}-${title.replaceAll('/', '')}-page${pageIndex + 1}`
      screenshotsCounts[baseName] = (screenshotsCounts[baseName] ?? 0) + 1
      cy.compareSnapshot({
        name: `${baseName}-${screenshotsCounts[baseName]}`,
        cypressScreenshotOptions: { capture: 'viewport' },
      })
    })
  }
}

describe('Adapted exercises examples', () => {
  if (Cypress.browser.name === 'electron') {
    for (const [exampleIndex, example] of examples.entries()) {
      for (const [width, height] of [
        [800, 600],
        [1920, 1080],
      ]) {
        it(`renders "${example.title}" in ${width}x${height}`, () => {
          cy.viewport(width, height)
          cy.mount(AdaptedExerciseExamplesCaptureComponent, { props: { adaptedExercise: example.exercise } })

          let pagesCount = ensureV2(example.exercise)
            .phases.map((s) => ('pages' in s.statement ? Math.max(1, s.statement.pages.length) : 1))
            .reduce((a, b) => a + b, 0)
          if (example.exercise.reference !== null) {
            pagesCount += 1
          }
          if (exampleIndex == examples.length - 1) {
            pagesCount += 1 // For the end page, only once per resolution
          }

          for (let pageIndex = 0; pageIndex < pagesCount; pageIndex++) {
            screenshot(example.title, pageIndex)
            cy.get('.container')
              .eq(0)
              .then((el) => {
                if (el[0].scrollHeight > el[0].clientHeight) {
                  cy.get('.container').eq(0).scrollTo('bottom')
                  screenshot(example.title, pageIndex)
                }
              })
            cy.get('div.control').eq(1).click()
          }
        })
      }
    }
  }
})
