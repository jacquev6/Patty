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

import { ignoreResizeObserverLoopError, loadFixtures } from './utils'

describe("Patty's authentication system", () => {
  beforeEach(() => {
    ignoreResizeObserverLoopError()
    loadFixtures(['dummy-adaptation'])
  })

  it('asks for password, warns if it is incorrect, and stores it', () => {
    cy.visit('/adaptation-batch-1')
    cy.get('h1:contains("Inputs")').should('not.exist')
    cy.get('[data-cy="password"]').should('exist')
    cy.get('[data-cy="password"]').type('not-the-password')
    cy.get('[data-cy="submit"]').click()
    cy.get('p:contains("Incorrect password")').should('exist')
    cy.get('[data-cy="password"]').should('exist')
    cy.get('[data-cy="password"]').clear()
    cy.get('[data-cy="password"]').type('password')
    cy.get('[data-cy="submit"]').click()
    cy.get('[data-cy="password"]').should('not.exist')
    cy.get('[data-cy="submit"]').should('not.exist')
    cy.get('h1:contains("Inputs")').should('exist').should('be.visible')

    cy.visit('/adaptation-batch-1')
    cy.get('h1:contains("Inputs")').should('exist').should('be.visible')
  })

  it('anticipates token expiration - on the same visit', () => {
    cy.intercept('POST', '/api/token', (req) => {
      req.continue((res) => {
        res.body.validUntil = new Date(Date.now() + 1000).toISOString()
      })
    })

    cy.visit('/adaptation-batch-1')
    cy.get('[data-cy="password"]').type('password')
    cy.get('[data-cy="submit"]').click()
    cy.get('h1:contains("Inputs")').should('exist')
    // Some time passes, the token is about to expire => ask for password again
    cy.get('h1:contains("Inputs")').should('not.exist')
    cy.get('[data-cy="password"]').should('exist')
  })

  it('anticipates token expiration - on a subsequent visit', () => {
    cy.intercept('POST', '/api/token', (req) => {
      req.continue((res) => {
        res.body.validUntil = new Date(Date.now() + 2000).toISOString()
      })
    })

    cy.visit('/adaptation-batch-1')
    cy.get('[data-cy="password"]').type('password')
    cy.get('[data-cy="submit"]').click()
    cy.get('h1:contains("Inputs")').should('exist')

    cy.visit('/adaptation-batch-1')
    cy.get('h1:contains("Inputs")').should('exist')
    // Some time passes, the token is about to expire => ask for password again
    cy.get('h1:contains("Inputs")').should('not.exist')
    cy.get('[data-cy="password"]').should('exist')
  })
})
