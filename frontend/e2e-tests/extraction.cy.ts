import { ignoreResizeObserverLoopError, visit } from './utils'

describe('The extraction batch creation page', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    cy.request('POST', 'http://fixtures-loader/load?fixtures=')
    ignoreResizeObserverLoopError()
    visit('/new-extraction-batch')
    cy.get('[data-cy="identified-user"]').type('Alice', { delay: 0 })
    cy.get('[data-cy="identified-user-ok"]').click()
  })

  // @todo it('looks like this', () => {
  //   screenshot('extraction-batch-creation-page')
  // })

  it('creates an extraction batch', () => {
    cy.get('button:contains("Submit")').click()
    cy.location('pathname').should('eq', '/extraction-batch-1')
    cy.get('p:contains("Created by: Alice")').should('exist')
    cy.get('a:contains("Download standalone HTML")')
      .should('have.attr', 'href')
      .then((href) => {
        expect(href).to.include('/api/export/extraction-batch/1.html?token=')
      })

    cy.visit('/')
    cy.get('ul:contains("Batch E1 (created by Alice")').should('exist')
    cy.get('a:contains("Batch E1")').should('have.attr', 'href', '/extraction-batch-1')
  })
})
