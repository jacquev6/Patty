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

import { loadFixtures, visit } from './utils'

describe('The index view', () => {
  beforeEach(() => {
    cy.viewport(1600, 800)
    visit('/')
  })

  it('paginates the existing adaptation batches', () => {
    loadFixtures(['20-adaptation-batches'])
    cy.visit('/')
    cy.get('a:contains("Batch A")').should('have.length', 20)
    cy.get('a:contains("Batch A")').eq(0).should('contain', 'Batch A20')
    cy.get('a:contains("Batch A")').eq(19).should('contain', 'Batch A1')
    cy.get('button:contains("Load more...")').eq(2).should('be.disabled')

    loadFixtures(['21-adaptation-batches'])
    cy.visit('/')
    cy.get('a:contains("Batch A")').should('have.length', 20)
    cy.get('a:contains("Batch A")').eq(0).should('contain', 'Batch A21')
    cy.get('a:contains("Batch A")').eq(19).should('contain', 'Batch A2')
    cy.get('button:contains("Load more...")').eq(2).should('be.enabled').click()
    cy.get('a:contains("Batch A")').should('have.length', 21)
    cy.get('a:contains("Batch A")').eq(0).should('contain', 'Batch A21')
    cy.get('a:contains("Batch A")').eq(19).should('contain', 'Batch A2')
    cy.get('a:contains("Batch A")').eq(20).should('contain', 'Batch A1')
    cy.get('button:contains("Load more...")').eq(2).should('be.disabled')

    loadFixtures(['70-adaptation-batches'])
    cy.visit('/')
    cy.get('a:contains("Batch A")').should('have.length', 20)
    cy.get('a:contains("Batch A")').eq(0).should('contain', 'Batch A70')
    cy.get('a:contains("Batch A")').eq(19).should('contain', 'Batch A51')
    cy.get('button:contains("Load more...")').eq(2).should('be.enabled').click()
    cy.get('a:contains("Batch A")').should('have.length', 40)
    cy.get('a:contains("Batch A")').eq(0).should('contain', 'Batch A70')
    cy.get('a:contains("Batch A")').eq(19).should('contain', 'Batch A51')
    cy.get('a:contains("Batch A")').eq(20).should('contain', 'Batch A50')
    cy.get('a:contains("Batch A")').eq(39).should('contain', 'Batch A31')
    cy.get('button:contains("Load more...")').eq(2).should('be.enabled').click()
    cy.get('a:contains("Batch A")').should('have.length', 60)
    cy.get('a:contains("Batch A")').eq(0).should('contain', 'Batch A70')
    cy.get('a:contains("Batch A")').eq(19).should('contain', 'Batch A51')
    cy.get('a:contains("Batch A")').eq(20).should('contain', 'Batch A50')
    cy.get('a:contains("Batch A")').eq(39).should('contain', 'Batch A31')
    cy.get('a:contains("Batch A")').eq(40).should('contain', 'Batch A30')
    cy.get('a:contains("Batch A")').eq(59).should('contain', 'Batch A11')
    cy.get('button:contains("Load more...")').eq(2).should('be.enabled').click()
    cy.get('a:contains("Batch A")').should('have.length', 70)
    cy.get('a:contains("Batch A")').eq(0).should('contain', 'Batch A70')
    cy.get('a:contains("Batch A")').eq(19).should('contain', 'Batch A51')
    cy.get('a:contains("Batch A")').eq(20).should('contain', 'Batch A50')
    cy.get('a:contains("Batch A")').eq(39).should('contain', 'Batch A31')
    cy.get('a:contains("Batch A")').eq(40).should('contain', 'Batch A30')
    cy.get('a:contains("Batch A")').eq(59).should('contain', 'Batch A11')
    cy.get('a:contains("Batch A")').eq(60).should('contain', 'Batch A10')
    cy.get('a:contains("Batch A")').eq(69).should('contain', 'Batch A1')
    cy.get('button:contains("Load more...")').eq(2).should('be.disabled')
  })
})
