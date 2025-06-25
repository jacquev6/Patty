import { visit } from './utils'

describe("Patty's error catcher", () => {
  beforeEach(() => {
    cy.request('POST', 'http://fixtures-loader/load?fixtures=')
    visit('/errors')
  })

  it('catches failed assertion', () => {
    cy.get('pre').should('not.exist')
    cy.get('button:contains("Assert")').click()

    cy.get('h1:contains("There was a bug")').should('exist')

    cy.visit('/errors')
    cy.get('pre')
      .should('contain', '"caughtBy": "Vue.config.errorHandler",')
      .should('contain', 'Error: Assertion failed')
  })

  it('catches dereferencing undefined', () => {
    cy.get('pre').should('not.exist')
    cy.get('button:contains("Dereference undefined")').click()

    cy.get('h1:contains("There was a bug")').should('exist')

    cy.visit('/errors')
    cy.get('pre')
      .should('contain', '"caughtBy": "Vue.config.errorHandler",')
      .should('contain', 'TypeError:')
      .should('contain', 'undefined')
  })

  it('catches dereferencing null', () => {
    cy.get('pre').should('not.exist')
    cy.get('button:contains("Dereference null")').click()

    cy.get('h1:contains("There was a bug")').should('exist')

    cy.visit('/errors')
    cy.get('pre')
      .should('contain', '"caughtBy": "Vue.config.errorHandler",')
      .should('contain', 'TypeError:')
      .should('contain', 'null')
  })

  it('catches unhandled rejection', () => {
    cy.get('pre').should('not.exist')
    cy.get('button:contains("Unhandled rejection")').click()

    cy.get('h1:contains("There was a bug")').should('exist')

    cy.visit('/errors')
    cy.get('pre').should('contain', '"caughtBy": "Vue.config.errorHandler",').should('contain', 'This is the reason')
  })

  it('catches exception', () => {
    cy.get('pre').should('not.exist')
    cy.get('button:contains("Throw exception")').click()

    cy.get('h1:contains("There was a bug")').should('exist')

    cy.visit('/errors')
    cy.get('pre')
      .should('contain', '"caughtBy": "Vue.config.errorHandler",')
      .should('contain', 'Error: This is the error')
  })
})
