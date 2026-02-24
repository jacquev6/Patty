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

import ThreeStatesCheckbox from './ThreeStatesCheckbox.vue'

describe('ThreeStatesCheckbox', () => {
  it('is initialy indeterminate and gets checked', () => {
    cy.mount(ThreeStatesCheckbox, { props: { modelValue: null, 'onUpdate:modelValue': cy.spy().as('onUpdate') } })

    cy.get('input[type="checkbox"]').should('not.be.checked')
    cy.get('input[type="checkbox"]').should('have.prop', 'indeterminate', true)
    cy.get('input[type="checkbox"]').click()
    cy.get('input[type="checkbox"]').should('be.checked')
    cy.get('input[type="checkbox"]').should('have.prop', 'indeterminate', false)
    cy.get('@onUpdate').should('have.been.calledWith', true)
  })

  it('is initialy checked and gets unchecked', () => {
    cy.mount(ThreeStatesCheckbox, { props: { modelValue: true, 'onUpdate:modelValue': cy.spy().as('onUpdate') } })

    cy.get('input[type="checkbox"]').should('be.checked')
    cy.get('input[type="checkbox"]').should('have.prop', 'indeterminate', false)
    cy.get('input[type="checkbox"]').click()
    cy.get('input[type="checkbox"]').should('not.be.checked')
    cy.get('input[type="checkbox"]').should('have.prop', 'indeterminate', false)
    cy.get('@onUpdate').should('have.been.calledWith', false)
  })

  it('is initialy unchecked and gets checked', () => {
    cy.mount(ThreeStatesCheckbox, { props: { modelValue: false, 'onUpdate:modelValue': cy.spy().as('onUpdate') } })

    cy.get('input[type="checkbox"]').should('not.be.checked')
    cy.get('input[type="checkbox"]').should('have.prop', 'indeterminate', false)
    cy.get('input[type="checkbox"]').click()
    cy.get('input[type="checkbox"]').should('be.checked')
    cy.get('input[type="checkbox"]').should('have.prop', 'indeterminate', false)
    cy.get('@onUpdate').should('have.been.calledWith', true)
  })

  it('reacts to model changes', () => {
    cy.mount(ThreeStatesCheckbox, { props: { modelValue: null } })
    cy.get('input[type="checkbox"]').should('not.be.checked')
    cy.get('input[type="checkbox"]').should('have.prop', 'indeterminate', true)
    cy.vue<typeof ThreeStatesCheckbox>().then((wrapper) => {
      wrapper.setProps({ modelValue: true })
    })
    cy.get('input[type="checkbox"]').should('be.checked')
    cy.get('input[type="checkbox"]').should('have.prop', 'indeterminate', false)
    cy.vue<typeof ThreeStatesCheckbox>().then((wrapper) => {
      wrapper.setProps({ modelValue: false })
    })
    cy.get('input[type="checkbox"]').should('not.be.checked')
    cy.get('input[type="checkbox"]').should('have.prop', 'indeterminate', false)
    cy.vue<typeof ThreeStatesCheckbox>().then((wrapper) => {
      wrapper.setProps({ modelValue: null })
    })
    cy.get('input[type="checkbox"]').should('not.be.checked')
    cy.get('input[type="checkbox"]').should('have.prop', 'indeterminate', true)
  })
})
