import AdaptationRender from './AdaptationRender.vue'

describe('AdaptationRender', () => {
  it('renders', () => {
    cy.mount(AdaptationRender, { props: { adaptedExercise: { instructions: 'Instructions', wording: 'Wording' } } })
    cy.get('p:contains("Instructions")').should('exist')
    cy.get('p:contains("Wording")').should('exist')
  })
})
