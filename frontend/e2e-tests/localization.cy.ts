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
