import { ignoreResizeObserverLoopError, visit } from './utils'

describe('Patty', () => {
  beforeEach(() => {
    ignoreResizeObserverLoopError()
    cy.viewport(1600, 800)
    visit('/')
    cy.get('[data-cy="identified-user"]').type('Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
  })

  it('creates an extraction batch', () => {
    cy.get('a:contains("New extraction batch")').click()
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('button:contains("Submit")').click()
    cy.get(':contains("in progress")').should('exist')
    cy.get('div.busy', { timeout: 30000 }).should('exist')

    cy.get('a:contains("Patty home")').click()
    cy.get('li:contains("created by Alice") a:contains("Batch E")').should('exist')
  })
})
