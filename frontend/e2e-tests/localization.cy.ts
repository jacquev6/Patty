import { ignoreResizeObserverLoopError, visit } from './utils'

describe('Patty localization', () => {
  beforeEach(ignoreResizeObserverLoopError)

  it("remembers the user's chosen locale", () => {
    visit('/')

    cy.get('[data-cy="localeSelect"]').should('have.value', 'en')
    cy.get('h1:contains("Textbooks")').should('exist')
    cy.get('[data-cy="localeSelect"]').select('fr')
    cy.get('h1:contains("Manuels")').should('exist')

    cy.visit('/')
    cy.get('[data-cy="localeSelect"]').should('have.value', 'fr')
    cy.get('h1:contains("Manuels")').should('exist')
    cy.get('[data-cy="localeSelect"]').select('en')
    cy.get('h1:contains("Textbooks")').should('exist')

    cy.visit('/')
    cy.get('[data-cy="localeSelect"]').should('have.value', 'en')
    cy.get('h1:contains("Textbooks")').should('exist')
  })
})
