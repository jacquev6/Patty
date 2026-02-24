// MALIN Platform https://malin.cahiersfantastiques.fr/
// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.

// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

import { visit, loadFixtures } from './utils'

describe("Patty's error catcher", () => {
  beforeEach(() => {
    loadFixtures([])
    visit('/errors')
  })

  it('catches failed assertion', () => {
    cy.get('button:contains("Assert")').click()

    cy.get('h1:contains("Error")').should('exist')

    cy.visit('/errors')
    cy.get('pre')
      .should('have.length', 1)
      .should('contain', '"caughtBy": "Vue.config.errorHandler",')
      .should('contain', 'Error: Assertion failed')
      .should('contain', '"githubIssueNumber": null')
  })

  it('catches dereferencing undefined', () => {
    cy.get('button:contains("Dereference undefined")').click()

    cy.get('h1:contains("Error")').should('exist')

    cy.visit('/errors')
    cy.get('pre')
      .should('have.length', 1)
      .should('contain', '"caughtBy": "Vue.config.errorHandler",')
      .should('contain', 'TypeError:')
      .should('contain', 'undefined')
      .should('contain', '"githubIssueNumber": null')
  })

  it('catches dereferencing null', () => {
    cy.get('button:contains("Dereference null")').click()

    cy.get('h1:contains("Error")').should('exist')

    cy.visit('/errors')
    cy.get('pre')
      .should('have.length', 1)
      .should('contain', '"caughtBy": "Vue.config.errorHandler",')
      .should('contain', 'TypeError:')
      .should('contain', 'null')
      .should('contain', '"githubIssueNumber": null')
  })

  it('catches unhandled rejection', () => {
    cy.get('button:contains("Unhandled rejection")').click()

    cy.get('h1:contains("Error")').should('exist')

    cy.visit('/errors')
    cy.get('pre')
      .should('have.length', 1)
      .should('contain', '"caughtBy": "Vue.config.errorHandler",')
      .should('contain', 'This is the reason')
      .should('contain', '"githubIssueNumber": null')
  })

  it('catches exception', () => {
    cy.get('button:contains("Throw exception")').click()

    cy.get('h1:contains("Error")').should('exist')

    cy.visit('/errors')
    cy.get('pre')
      .should('have.length', 1)
      .should('contain', '"caughtBy": "Vue.config.errorHandler",')
      .should('contain', 'Error: This is the error')
      .should('contain', '"githubIssueNumber": null')
  })

  it('catches network error', () => {
    cy.get('button:contains("Network error")').click()

    cy.get('h1:contains("Network error")').should('exist')

    cy.visit('/errors')
    cy.get('pre')
      .should('have.length', 1)
      .should('contain', '"caughtBy": "Vue.config.errorHandler",')
      .should(
        'contain',
        Cypress.browser.family === 'chromium'
          ? 'TypeError: Failed to fetch'
          : 'TypeError: NetworkError when attempting to fetch resource.',
      )
      .should('contain', '"githubIssueNumber": 99')
  })

  it('reports repeated undefined only once', () => {
    cy.get('button:contains("Repeated undefined")').click()

    cy.get('h1:contains("Error"):contains("(10 occurrences)")').should('exist')

    cy.visit('/errors')
    cy.get('pre').should('have.length', 1)
  })
})
