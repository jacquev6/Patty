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

import TextArea from './TextArea.vue'

describe('TextArea', () => {
  it('gets its size from its initial model', () => {
    cy.viewport(500, 500)
    cy.mount(TextArea, { props: { modelValue: 'Blah\nBlah\nBlah\n' } })
    const large = { firefox: '82px' }[Cypress.browser.name] ?? '80px'
    cy.get('textarea').should('have.css', 'height', large)
  })

  it('resizes with content when typing', () => {
    cy.viewport(500, 500)
    cy.mount(TextArea)

    const small = { firefox: '45px' }[Cypress.browser.name] ?? '43px'
    const large = { firefox: '82px' }[Cypress.browser.name] ?? '80px'

    cy.get('textarea').should('have.css', 'height', small)
    cy.get('textarea').type('Blah\nBlah\nBlah\n', { delay: 0 })
    cy.get('textarea').should('have.css', 'height', large)
    cy.get('textarea').type('{selectall}{backspace}', { delay: 0 })
    cy.get('textarea').should('have.css', 'height', small)
  })

  it('resizes with window width', () => {
    cy.viewport(500, 500)
    cy.mount(TextArea)

    cy.get('textarea').type(
      'Blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah blah',
      { delay: 0 },
    )

    const small = { firefox: '64px' }[Cypress.browser.name] ?? '61px'
    const large = { firefox: '100px' }[Cypress.browser.name] ?? '98px'

    cy.get('textarea').should('have.css', 'height', small)
    cy.viewport(300, 500)
    cy.get('textarea').should('have.css', 'height', large)
    cy.viewport(500, 500)
    cy.get('textarea').should('have.css', 'height', small)
  })

  it('resizes when model is changed', () => {
    cy.viewport(500, 500)

    const small = { firefox: '45px' }[Cypress.browser.name] ?? '43px'
    const large = { firefox: '82px' }[Cypress.browser.name] ?? '80px'

    cy.mount(TextArea, { props: { modelValue: '' } })
    cy.get('textarea').should('have.value', '')
    cy.get('textarea').should('have.css', 'height', small)
    cy.vue<typeof TextArea>().then((wrapper) => wrapper.setProps({ modelValue: 'Blah\nBlah\nBlah\n' }))
    cy.get('textarea').should('have.value', 'Blah\nBlah\nBlah\n')
    cy.get('textarea').should('have.css', 'height', large)
    cy.vue<typeof TextArea>().then((wrapper) => wrapper.setProps({ modelValue: '' }))
    cy.get('textarea').should('have.value', '')
    cy.get('textarea').should('have.css', 'height', small)
  })
})
