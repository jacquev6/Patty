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

import ComboInput from './ComboInput.vue'

const screenshotsCounts: Record<string, number> = {}

function screenshot() {
  if (!Cypress.config('isInteractive')) {
    const baseName = Cypress.currentTest.titlePath.join('-').replaceAll(' ', '_')
    screenshotsCounts[baseName] = (screenshotsCounts[baseName] ?? 0) + 1
    const name = `${baseName}-${screenshotsCounts[baseName]}`
    cy.compareSnapshot(name)
  }
}

describe('ComboInput', () => {
  it('puts additional attributes on the input', () => {
    cy.mount(ComboInput, {
      props: { modelValue: '', suggestions: [], maxSuggestionsDisplayCount: 4 },
      attrs: { 'data-foo': 'bar' },
    })

    cy.get('input').should('have.attr', 'data-foo', 'bar')
  })

  it('renders', () => {
    cy.mount(ComboInput, {
      props: {
        modelValue: '',
        suggestions: ['Alpha 1', 'Alpha 2', 'Bravo', 'Charlie'],
        maxSuggestionsDisplayCount: 4,
      },
    })

    cy.get('span.clue').should('exist')
    cy.get('div.suggestions').should('not.exist')
    screenshot()
    cy.get('input').focus()
    cy.get('span.clue').should('not.exist')
    cy.get('div.suggestions').should('exist')
    screenshot()
    cy.get('div.suggestions > p').eq(2).click()
    cy.get('input').should('have.value', 'Bravo')
    cy.get('div.suggestions').should('not.exist')
    cy.get('span.clue').should('exist')
    screenshot()
  })

  it('filters suggestions', () => {
    cy.mount(ComboInput, {
      props: {
        modelValue: '',
        suggestions: ['Alpha 1', 'Alpha 2', 'Bravo', 'Charlie'],
        maxSuggestionsDisplayCount: 4,
      },
    })

    cy.get('input').focus()
    cy.get('[data-cy="suggestion"]').eq(0).should('have.text', 'Alpha 1')
    cy.get('[data-cy="suggestion"]').eq(1).should('have.text', 'Alpha 2')
    cy.get('[data-cy="suggestion"]').eq(2).should('have.text', 'Bravo')
    cy.get('[data-cy="suggestion"]').eq(3).should('have.text', 'Charlie')
    cy.get('input').type('h')
    // Suggestions that contain "h", in alphabetical order:
    cy.get('[data-cy="suggestion"]').eq(0).should('have.text', 'Alpha 1')
    cy.get('[data-cy="suggestion"]').eq(1).should('have.text', 'Alpha 2')
    cy.get('[data-cy="suggestion"]').eq(2).should('have.text', 'Charlie')
    // Suggestions that do not contain "h", in alphabetical order:
    cy.get('[data-cy="suggestion"]').eq(3).should('have.text', 'Bravo')
    cy.get('input').type('ar')
    // Suggestions that contain "har", in alphabetical order:
    cy.get('[data-cy="suggestion"]').eq(0).should('have.text', 'Charlie')
    // Suggestions that do not contain "har", in alphabetical order:
    cy.get('[data-cy="suggestion"]').eq(1).should('have.text', 'Alpha 1')
    cy.get('[data-cy="suggestion"]').eq(2).should('have.text', 'Alpha 2')
    cy.get('[data-cy="suggestion"]').eq(3).should('have.text', 'Bravo')
  })
})
