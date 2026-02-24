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

import VirtualNumericalKeyboardTestComponent from './VirtualNumericalKeyboardTestComponent.vue'
import assert from '$/assert'

describe('VirtualNumericalKeyboard into TriColoredInput', () => {
  it('inserts at the end', () => {
    cy.mount(VirtualNumericalKeyboardTestComponent)

    cy.get('p:contains("TriColoredInput") > [contenteditable]').as('input')
    cy.get('p:contains("TriColoredInput") > span').last().as('output')
    cy.get('@input').focus()
    cy.get('[data-cy="virtual-button"]:contains("3")').click()
    cy.get('@input').should('have.text', '3')
    cy.get('@output').should('have.text', '3')
    cy.get('[data-cy="virtual-button"]:contains("7")').click()
    cy.get('@input').should('have.text', '37')
    cy.get('@output').should('have.text', '37')
    cy.get('[data-cy="virtual-button"]:contains("5")').click()
    cy.get('@input').should('have.text', '375')
    cy.get('@output').should('have.text', '375')
  })

  it('inserts at the start', () => {
    cy.mount(VirtualNumericalKeyboardTestComponent)

    cy.get('p:contains("TriColoredInput") > [contenteditable]').as('input')
    cy.get('p:contains("TriColoredInput") > span').last().as('output')
    cy.get('@input').focus()
    cy.get('[data-cy="virtual-button"]:contains("3")').click()
    cy.get('@input').should('have.text', '3')
    cy.get('@output').should('have.text', '3')
    cy.get('@input').type('{moveToStart}')
    cy.get('[data-cy="virtual-button"]:contains("7")').click()
    cy.get('@input').should('have.text', '73')
    cy.get('@output').should('have.text', '73')
    cy.get('@input').type('{moveToStart}')
    cy.get('[data-cy="virtual-button"]:contains("5")').click()
    cy.get('@input').should('have.text', '573')
    cy.get('@output').should('have.text', '573')
  })

  it('replaces selection', () => {
    cy.mount(VirtualNumericalKeyboardTestComponent)

    cy.get('p:contains("TriColoredInput") > [contenteditable]').as('input')
    cy.get('p:contains("TriColoredInput") > span').last().as('output')

    cy.get('@input').focus().type('12345')
    cy.get('@input').then((el) => {
      const sel = window.getSelection()
      assert(sel !== null)
      sel.removeAllRanges()
      const range = document.createRange()
      range.setStart(el[0], 1)
      range.setEnd(el[0], 4)
      sel.addRange(range)
    })
    cy.get('[data-cy="virtual-button"]:contains("7")').click()
    cy.get('@input').should('have.text', '175')
    cy.get('@output').should('have.text', '175')
  })
})
