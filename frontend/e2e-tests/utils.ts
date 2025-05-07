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
  cy.compareSnapshot({
    name: `${name}.${Cypress.browser.name}`,
    cypressScreenshotOptions: { disableTimersAndAnimations: true },
  })
}
