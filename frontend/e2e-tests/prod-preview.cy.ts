import { ignoreResizeObserverLoopError, loadFixtures, visit } from './utils'

describe('Patty', () => {
  beforeEach(() => {
    ignoreResizeObserverLoopError()
    if (Cypress.env('PATTY_UNIT_TESTING')) {
      loadFixtures(['extraction-seed-data-v3', 'adaptation-seed-data'])
    }
    cy.viewport(1600, 800)
    visit('/')
  })

  if (!Cypress.env('PATTY_UNIT_TESTING') && Cypress.env('PATTY_USE_JACQUEV6_S3')) {
    it('loads a textbook', () => {
      cy.get('a:contains("Outils pour le français CE2 2019")').click()
      cy.location('pathname').should('eq', '/textbook-1')
      cy.get('h1:contains("Outils pour le français CE2 2019")').should('exist')
    })
  }

  it('creates an extraction batch', () => {
    cy.get('a:contains("New extraction batch")').click()
    cy.get('input[type="file"]').selectFile('e2e-tests/inputs/test.pdf')
    cy.get('button:contains("Submit")').click()
    cy.get(':contains("in progress")').should('exist')

    cy.get('a:contains("Malin home")').click()
    cy.get('li:contains("created by Alice") a:contains("Batch E")').should('exist')
  })
})
