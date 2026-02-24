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
