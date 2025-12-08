// Copyright 2025 Vincent Jacques <vincent@vincent-jacques.net>

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
