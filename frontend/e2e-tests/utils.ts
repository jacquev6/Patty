export function ignoreResizeObserverLoopError() {
  Cypress.on('uncaught:exception', (error) => {
    if (error.message.includes('ResizeObserver loop completed with undelivered notifications.')) {
      // @todo Deep dive into this issue: avoid the error instead of ignoring it.
      // https://developer.mozilla.org/en-US/docs/Web/API/ResizeObserver#observation_errors
      return false
    } else {
      return true
    }
  })
}

export function screenshot(name: string) {
  if (!Cypress.config('isInteractive')) {
    cy.compareSnapshot({
      name,
      cypressScreenshotOptions: { disableTimersAndAnimations: true },
    })
  }
}

export function visit(url: string) {
  cy.visit(url)
  cy.get('[data-cy="password"]').type('password')
  cy.get('[data-cy="submit"]').click()
}

export function loadFixtures(fixtures_: string[]) {
  const fixtures = fixtures_.join(',')
  const fixturesLoader = (() => {
    if (Cypress.config('isInteractive')) {
      return 'fixtures-loader'
    } else {
      return `fixtures-loader--for-${Cypress.browser.name}`
    }
  })()
  cy.request('POST', `http://${fixturesLoader}/load?fixtures=${fixtures}`)
}
