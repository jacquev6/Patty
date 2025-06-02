import { ignoreResizeObserverLoopError, screenshot, visit } from './utils'

describe('The classification batch creation page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    // cy.request('POST', 'http://fixtures-loader/load?fixtures=dummy-adaptation')
    ignoreResizeObserverLoopError()
    visit('/new-classification-batch')
    cy.get('[data-cy="identified-user"]').type('Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
  })

  it('looks like this', () => {
    screenshot('classification-batch-creation-page')
  })
})
